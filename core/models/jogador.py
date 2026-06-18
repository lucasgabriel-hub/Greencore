"""
core.models.jogador
=====================
Modelo de dados do jogador (classe ``Jogador`` prevista no planejamento
do Dia 1).

Reúne tudo que antes não existia de forma persistente no projeto:
pontuação acumulada entre partidas, controle de quantas dicas já foram
usadas em cada pergunta (no código antigo era possível clicar em
"Mostrar Dica" infinitas vezes, mesmo o tutorial dizendo que só é
permitida uma dica por pergunta) e histórico de troféus conquistados.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from core import config


@dataclass
class ResultadoPartida:
    dificuldade: str
    pontuacao: int
    total_perguntas: int
    trofeu_conquistado: bool
    data: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict:
        return {
            "dificuldade": self.dificuldade,
            "pontuacao": self.pontuacao,
            "total_perguntas": self.total_perguntas,
            "trofeu_conquistado": self.trofeu_conquistado,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "ResultadoPartida":
        return cls(
            dificuldade=dados["dificuldade"],
            pontuacao=dados["pontuacao"],
            total_perguntas=dados["total_perguntas"],
            trofeu_conquistado=dados.get("trofeu_conquistado", False),
            data=dados.get("data", ""),
        )


@dataclass
class Jogador:
    nome: str = "Jogador"
    pontuacao_total: int = 0
    trofeus: set[str] = field(default_factory=set)
    historico: list[ResultadoPartida] = field(default_factory=list)

    _dicas_usadas_na_rodada: dict[int, int] = field(default_factory=dict, repr=False)


    def adicionar_pontos(self, pontos: int) -> None:
        if pontos < 0:
            raise ValueError("Não é possível adicionar uma pontuação negativa.")
        self.pontuacao_total += pontos


    def iniciar_rodada(self) -> None:
        self._dicas_usadas_na_rodada = {}

    def pode_usar_dica(self, indice_pergunta: int) -> bool:
        usadas = self._dicas_usadas_na_rodada.get(indice_pergunta, 0)
        return usadas < config.MAX_DICAS_POR_PERGUNTA

    def registrar_uso_dica(self, indice_pergunta: int) -> bool:
        """
        Tenta registrar o uso de uma dica para a pergunta informada.
        Retorna ``True`` se a dica pôde ser usada (dentro do limite) ou
        ``False`` se o jogador já esgotou as dicas disponíveis para essa
        pergunta.
        """
        if not self.pode_usar_dica(indice_pergunta):
            return False
        self._dicas_usadas_na_rodada[indice_pergunta] = (
            self._dicas_usadas_na_rodada.get(indice_pergunta, 0) + 1
        )
        return True


    def conquistar_trofeu(self, dificuldade: str) -> bool:
        """Adiciona um troféu ao jogador. Retorna True se era um troféu novo."""
        if dificuldade in self.trofeus:
            return False
        self.trofeus.add(dificuldade)
        return True

    def registrar_resultado(
        self, dificuldade: str, pontuacao: int, total_perguntas: int, trofeu_conquistado: bool
    ) -> ResultadoPartida:
        resultado = ResultadoPartida(
            dificuldade=dificuldade,
            pontuacao=pontuacao,
            total_perguntas=total_perguntas,
            trofeu_conquistado=trofeu_conquistado,
        )
        self.historico.append(resultado)
        return resultado

    def ultima_dificuldade_com_trofeu(self) -> str | None:
        """
        Retorna a dificuldade do troféu mais recentemente conquistado,
        com base no histórico de partidas (ou ``None`` se nenhum troféu
        foi conquistado ainda). Útil para destacar na Sala de Troféus qual
        foi a conquista mais recente do jogador.
        """
        for resultado in reversed(self.historico):
            if resultado.trofeu_conquistado:
                return resultado.dificuldade
        return None

    def melhor_pontuacao(self, dificuldade: str) -> int:
        """Maior pontuação já obtida pelo jogador numa dificuldade específica."""
        pontuacoes = [r.pontuacao for r in self.historico if r.dificuldade == dificuldade]
        return max(pontuacoes, default=0)


    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "pontuacao_total": self.pontuacao_total,
            "trofeus": sorted(self.trofeus),
            "historico": [r.to_dict() for r in self.historico],
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Jogador":
        return cls(
            nome=dados.get("nome", "Jogador"),
            pontuacao_total=dados.get("pontuacao_total", 0),
            trofeus=set(dados.get("trofeus", [])),
            historico=[ResultadoPartida.from_dict(r) for r in dados.get("historico", [])],
        )
