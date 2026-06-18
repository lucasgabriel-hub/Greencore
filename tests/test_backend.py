"""
tests.test_backend
====================
Testes finais do backend do Greencore (tarefa do Dia 5: "testes finais").
Executar com:
    python -m unittest discover -s tests -v
ou simplesmente:
    python -m unittest tests.test_backend -v

Não depende de Tkinter nem de pygame: testa exclusivamente a lógica de
jogo, então roda em qualquer ambiente, inclusive sem tela (headless).
"""

from __future__ import annotations
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from core import config
from core.models.jogador import Jogador
from core.models.pergunta import Pergunta, PerguntaInvalidaError
from core.models.quiz import Quiz, QuizError
from core.models.recompensa import GerenciadorRecompensas
from core.services import banco_perguntas, persistencia, personagens


class TestPergunta(unittest.TestCase):
    def test_pergunta_valida_eh_aceita(self):
        p = Pergunta(
            texto="2 + 2?",
            alternativas=["3", "4", "5"],
            correta="4",
            personagem="urso_ecologico.png",
            dica="Pense em dois pares.",
        )
        self.assertTrue(p.verificar_resposta("4"))
        self.assertTrue(p.verificar_resposta("  4 "))  # tolera espaços
        self.assertFalse(p.verificar_resposta("5"))
        self.assertFalse(p.verificar_resposta(None))

    def test_resposta_correta_fora_das_alternativas_eh_invalida(self):
        with self.assertRaises(PerguntaInvalidaError):
            Pergunta(
                texto="Pergunta ruim",
                alternativas=["A", "B"],
                correta="C",
                personagem="x.png",
                dica="dica",
            )

    def test_alternativas_duplicadas_sao_invalidas(self):
        with self.assertRaises(PerguntaInvalidaError):
            Pergunta(
                texto="Pergunta ruim",
                alternativas=["A", "A"],
                correta="A",
                personagem="x.png",
                dica="dica",
            )

    def test_embaralhar_nao_altera_lista_original(self):
        original = ["A", "B", "C", "D"]
        p = Pergunta(
            texto="X", alternativas=original, correta="A", personagem="x.png", dica="d"
        )
        embaralhada = p.alternativas_embaralhadas()
        self.assertEqual(sorted(embaralhada), sorted(original))
        self.assertEqual(p.alternativas, original)


class TestBancoPerguntas(unittest.TestCase):
    def test_banco_completo_eh_valido(self):
        erros = banco_perguntas.validar_banco_completo()
        self.assertEqual(erros, [])

    def test_todas_dificuldades_tem_dez_perguntas(self):
        for dificuldade in config.DIFICULDADES:
            perguntas = banco_perguntas.carregar_perguntas(dificuldade)
            self.assertEqual(len(perguntas), 10, f"Dificuldade {dificuldade} sem 10 perguntas")

    def test_dificuldade_inexistente_gera_erro_tratado(self):
        with self.assertRaises(banco_perguntas.BancoPerguntasError):
            banco_perguntas.carregar_perguntas("Impossível")


class TestPersonagens(unittest.TestCase):
    def test_todos_os_sprites_existem_em_disco(self):
        erros = personagens.validar_arquivos_existentes()
        self.assertEqual(erros, [])

    def test_personagem_desconhecido_nao_quebra(self):
        p = personagens.obter_personagem("arquivo_que_nao_existe.png")
        self.assertEqual(p.arquivo, "arquivo_que_nao_existe.png")


class TestJogador(unittest.TestCase):
    def test_limite_de_dicas_por_pergunta(self):
        j = Jogador()
        j.iniciar_rodada()
        self.assertTrue(j.pode_usar_dica(0))
        self.assertTrue(j.registrar_uso_dica(0))
        self.assertFalse(j.pode_usar_dica(0))
        self.assertFalse(j.registrar_uso_dica(0))
        # outra pergunta tem seu próprio contador
        self.assertTrue(j.pode_usar_dica(1))

    def test_trofeu_nao_duplica(self):
        j = Jogador()
        self.assertTrue(j.conquistar_trofeu("Fácil"))
        self.assertFalse(j.conquistar_trofeu("Fácil"))
        self.assertEqual(j.trofeus, {"Fácil"})

    def test_serializacao_ida_e_volta(self):
        j = Jogador(nome="Ana", pontuacao_total=42, trofeus={"Fácil", "Médio"})
        j.registrar_resultado("Fácil", 10, 10, True)
        dados = j.to_dict()
        j2 = Jogador.from_dict(dados)
        self.assertEqual(j2.nome, "Ana")
        self.assertEqual(j2.pontuacao_total, 42)
        self.assertEqual(j2.trofeus, {"Fácil", "Médio"})
        self.assertEqual(len(j2.historico), 1)


class TestQuiz(unittest.TestCase):
    def test_fluxo_completo_acertando_tudo_concede_trofeu(self):
        j = Jogador()
        q = Quiz(jogador=j)
        q.iniciar("Fácil")
        self.assertEqual(q.tempo_restante, config.TEMPO_POR_DIFICULDADE["Fácil"])

        while not q.terminou:
            pergunta = q.pergunta_atual
            q.responder(pergunta.correta)

        resultado = q.finalizar()
        self.assertTrue(resultado.trofeu_conquistado)
        self.assertEqual(resultado.pontuacao, 10)
        self.assertIn("Fácil", j.trofeus)

    def test_errar_tudo_nao_concede_trofeu(self):
        j = Jogador()
        q = Quiz(jogador=j)
        q.iniciar("Fácil")

        while not q.terminou:
            pergunta = q.pergunta_atual
            errada = next(a for a in pergunta.alternativas if a != pergunta.correta)
            q.responder(errada)

        resultado = q.finalizar()
        self.assertFalse(resultado.trofeu_conquistado)
        self.assertEqual(resultado.pontuacao, 0)
        self.assertNotIn("Fácil", j.trofeus)

    def test_tempo_esgotado_avanca_pergunta_sem_pontos(self):
        q = Quiz()
        q.iniciar("Pesadelo")
        q.tempo_restante = 0
        resultado = q.registrar_tempo_esgotado()
        self.assertFalse(resultado.correta)
        self.assertEqual(resultado.pontos_ganhos, 0)
        self.assertEqual(q.indice, 1)

    def test_pontuacao_por_dificuldade_eh_diferente(self):
        for dificuldade, pontos_esperados in config.PONTOS_POR_DIFICULDADE.items():
            q = Quiz()
            q.iniciar(dificuldade)
            pergunta = q.pergunta_atual
            r = q.responder(pergunta.correta)
            self.assertEqual(r.pontos_ganhos, pontos_esperados)

    def test_acessar_pergunta_atual_sem_iniciar_gera_erro(self):
        q = Quiz()
        with self.assertRaises(QuizError):
            _ = q.pergunta_atual

    def test_pedir_dica_respeita_limite_do_jogador(self):
        q = Quiz()
        q.iniciar("Fácil")
        self.assertIsNotNone(q.pedir_dica())
        self.assertIsNone(q.pedir_dica())


class TestRecompensas(unittest.TestCase):
    def test_avaliar_conquista_apenas_com_100_porcento(self):
        gerenciador = GerenciadorRecompensas()
        j = Jogador()
        self.assertIsNone(gerenciador.avaliar_conquista(j, "Fácil", 9, 10))
        self.assertIsNotNone(gerenciador.avaliar_conquista(j, "Fácil", 10, 10))

    def test_listar_trofeus_segue_ordem_das_dificuldades(self):
        gerenciador = GerenciadorRecompensas()
        j = Jogador(trofeus={"Pesadelo", "Fácil"})
        trofeus = gerenciador.listar_trofeus_conquistados(j)
        self.assertEqual([t.dificuldade for t in trofeus], ["Fácil", "Pesadelo"])


class TestPersistencia(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp_dir, ignore_errors=True)
        self.caminho = self.tmp_dir / "progresso.json"

    def test_salvar_e_carregar(self):
        j = Jogador(nome="Beto", pontuacao_total=7, trofeus={"Médio"})
        persistencia.salvar_progresso(j, caminho=self.caminho)
        self.assertTrue(self.caminho.exists())

        j2 = persistencia.carregar_progresso(caminho=self.caminho)
        self.assertEqual(j2.nome, "Beto")
        self.assertEqual(j2.pontuacao_total, 7)
        self.assertEqual(j2.trofeus, {"Médio"})

    def test_carregar_arquivo_inexistente_devolve_jogador_novo(self):
        j = persistencia.carregar_progresso(caminho=self.caminho)
        self.assertEqual(j.pontuacao_total, 0)
        self.assertEqual(j.trofeus, set())

    def test_carregar_arquivo_corrompido_nao_quebra(self):
        self.caminho.write_text("{ isso não é JSON válido", encoding="utf-8")
        j = persistencia.carregar_progresso(caminho=self.caminho)
        self.assertEqual(j.pontuacao_total, 0)


if __name__ == "__main__":
    unittest.main()
