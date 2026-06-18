"""
core.models.pergunta
=====================
Modelo de dados de uma pergunta do quiz (classe ``Pergunta`` prevista no
planejamento do Dia 1).

Antes, cada pergunta era apenas um dicionário "solto" dentro de quiz.py,
sem nenhuma validação. Isso permitia, por exemplo, uma pergunta cuja
resposta "correta" não estivesse entre as alternativas, sem que nada
avisasse sobre o erro. Agora a validação é feita uma única vez, na criação
do objeto.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field


class PerguntaInvalidaError(ValueError):
    """Levantada quando os dados de uma pergunta estão inconsistentes."""


@dataclass
class Pergunta:
    texto: str
    alternativas: list[str]
    correta: str
    personagem: str
    dica: str
    dificuldade: str = field(default="")

    def __post_init__(self) -> None:
        self._validar()

    # ------------------------------------------------------------------
    # Validação
    # ------------------------------------------------------------------
    def _validar(self) -> None:
        if not self.texto or not self.texto.strip():
            raise PerguntaInvalidaError("Pergunta sem texto.")

        if not self.alternativas or len(self.alternativas) < 2:
            raise PerguntaInvalidaError(
                f"A pergunta '{self.texto}' precisa de ao menos 2 alternativas."
            )

        if len(set(self.alternativas)) != len(self.alternativas):
            raise PerguntaInvalidaError(
                f"A pergunta '{self.texto}' tem alternativas duplicadas."
            )

        if self.correta not in self.alternativas:
            raise PerguntaInvalidaError(
                f"A resposta correta de '{self.texto}' não está entre as alternativas."
            )

    # ------------------------------------------------------------------
    # Comportamento
    # ------------------------------------------------------------------
    def alternativas_embaralhadas(self) -> list[str]:
        """Retorna uma cópia embaralhada das alternativas.

        Nunca embaralha a lista original guardada no objeto, para que a
        pergunta possa ser reutilizada (ex.: reiniciar uma rodada) sem
        perder a ordem de cadastro.
        """
        embaralhadas = self.alternativas[:]
        random.shuffle(embaralhadas)
        return embaralhadas

    def verificar_resposta(self, resposta: str) -> bool:
        """Compara a resposta do jogador com a resposta correta.

        A comparação ignora espaços nas extremidades e diferenças de
        maiúsculas/minúsculas, tornando a validação mais tolerante a
        pequenas variações vindas da interface.
        """
        if resposta is None:
            return False
        return resposta.strip().casefold() == self.correta.strip().casefold()

    # ------------------------------------------------------------------
    # Serialização (usada pelo banco de perguntas / testes)
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "pergunta": self.texto,
            "alternativas": list(self.alternativas),
            "correta": self.correta,
            "personagem": self.personagem,
            "dica": self.dica,
        }

    @classmethod
    def from_dict(cls, dados: dict, dificuldade: str = "") -> "Pergunta":
        try:
            return cls(
                texto=dados["pergunta"],
                alternativas=list(dados["alternativas"]),
                correta=dados["correta"],
                personagem=dados["personagem"],
                dica=dados["dica"],
                dificuldade=dificuldade,
            )
        except KeyError as exc:
            raise PerguntaInvalidaError(
                f"Campo obrigatório ausente em uma pergunta: {exc}"
            ) from exc
