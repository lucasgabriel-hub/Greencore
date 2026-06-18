"""
Módulo central do modelo de domínio do quiz, contendo a classe Quiz e
classes auxiliares relacionadas ao ciclo de vida da partida, respostas e recompensas.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core import config
from core.models.jogador import Jogador
from core.models.pergunta import Pergunta
from core.models.recompensa import GerenciadorRecompensas, Recompensa
from core.services import banco_perguntas


class QuizError(Exception):
    """Erro genérico de uso da classe Quiz (ex.: método chamado fora de hora)."""


@dataclass
class ResultadoResposta:
    correta: bool
    pontos_ganhos: int
    pontuacao_atual: int
    fim_da_partida: bool


@dataclass
class ResultadoPartidaFinal:
    dificuldade: str
    pontuacao: int
    total_perguntas: int
    trofeu: Recompensa | None

    @property
    def trofeu_conquistado(self) -> bool:
        return self.trofeu is not None


class Quiz:
    """Controlador de uma partida do quiz Greencore."""

    def __init__(self, jogador: Jogador | None = None, gerenciador_recompensas=None):
        self.jogador = jogador or Jogador()
        self.gerenciador_recompensas = gerenciador_recompensas or GerenciadorRecompensas()

        self.dificuldade: str | None = None
        self.perguntas: tuple[Pergunta, ...] = ()
        self.indice: int = -1
        self.pontuacao: int = 0
        self.tempo_restante: int = 0
        self._finalizada: bool = False


    def iniciar(self, dificuldade: str) -> Pergunta:
        """
        Inicia uma nova partida na dificuldade informada e retorna a
        primeira pergunta."""
        self.perguntas = banco_perguntas.carregar_perguntas(dificuldade)
        self.dificuldade = dificuldade
        self.indice = 0
        self.pontuacao = 0
        self._finalizada = False
        self.jogador.iniciar_rodada()
        self._reiniciar_cronometro()
        return self.pergunta_atual

    @property
    def pergunta_atual(self) -> Pergunta:
        if self.dificuldade is None:
            raise QuizError("O quiz ainda não foi iniciado. Chame iniciar() primeiro.")
        if self.terminou:
            raise QuizError("Não há pergunta atual: a partida já terminou.")
        return self.perguntas[self.indice]

    @property
    def total_perguntas(self) -> int:
        return len(self.perguntas)

    @property
    def terminou(self) -> bool:
        return self._finalizada or self.indice >= len(self.perguntas)

    def _reiniciar_cronometro(self) -> None:
        self.tempo_restante = config.tempo_para_dificuldade(self.dificuldade)

    def tick(self) -> int:
        """Decrementa um segundo do cronômetro e retorna o tempo restante.

        Quem é responsável por *chamar* este método uma vez por segundo é
        o frontend (ex.: via ``root.after(1000, ...)`` no Tkinter), já que
        o agendamento de chamadas depende da biblioteca de interface
        usada. Esta classe só guarda a regra: quanto tempo resta.
        """
        if self.tempo_restante > 0:
            self.tempo_restante -= 1
        return self.tempo_restante

    @property
    def tempo_esgotado(self) -> bool:
        return self.tempo_restante <= 0


    def responder(self, resposta: str) -> ResultadoResposta:
        """
        Valida a resposta do jogador para a pergunta atual, atualiza a
        pontuação e avança para a próxima pergunta.
        """
        pergunta = self.pergunta_atual
        correta = pergunta.verificar_resposta(resposta)

        pontos_ganhos = 0
        if correta:
            pontos_ganhos = config.pontos_para_dificuldade(self.dificuldade)
            self.pontuacao += pontos_ganhos

        self._avancar()

        return ResultadoResposta(
            correta=correta,
            pontos_ganhos=pontos_ganhos,
            pontuacao_atual=self.pontuacao,
            fim_da_partida=self.terminou,
        )

    def registrar_tempo_esgotado(self) -> ResultadoResposta:
        """
        Usado quando o cronômetro chega a zero sem o jogador responder.
        Não há pontos, e a pergunta é tratada como "passada" (sem penalidade
        adicional, mantendo o comportamento original do jogo).
        """
        self._avancar()
        return ResultadoResposta(
            correta=False,
            pontos_ganhos=0,
            pontuacao_atual=self.pontuacao,
            fim_da_partida=self.terminou,
        )

    def _avancar(self) -> None:
        self.indice += 1
        if self.indice >= len(self.perguntas):
            self._finalizada = True
        else:
            self._reiniciar_cronometro()


    def pedir_dica(self) -> str | None:
        """
        Retorna o texto da dica da pergunta atual, respeitando o limite
        de uma dica por pergunta. Retorna ``None`` se o limite já foi
        atingido (no jogo antigo, era possível pedir dica ilimitadamente).
        """
        if not self.jogador.registrar_uso_dica(self.indice):
            return None
        return self.pergunta_atual.dica

    def personagem_da_dica(self) -> str:
        """Nome do arquivo de sprite do personagem associado à pergunta atual."""
        return self.pergunta_atual.personagem

    def finalizar(self) -> ResultadoPartidaFinal:
        """Encerra a partida (mesmo que ainda faltem perguntas, ex.: o
        jogador saiu no meio), registra o resultado no histórico do
        jogador e avalia se um troféu foi conquistado."""
        self._finalizada = True

        trofeu = self.gerenciador_recompensas.avaliar_conquista(
            self.jogador, self.dificuldade, self.pontuacao, len(self.perguntas)
        )

        self.jogador.adicionar_pontos(self.pontuacao)
        self.jogador.registrar_resultado(
            dificuldade=self.dificuldade,
            pontuacao=self.pontuacao,
            total_perguntas=len(self.perguntas),
            trofeu_conquistado=trofeu is not None,
        )

        return ResultadoPartidaFinal(
            dificuldade=self.dificuldade,
            pontuacao=self.pontuacao,
            total_perguntas=len(self.perguntas),
            trofeu=trofeu,
        )
