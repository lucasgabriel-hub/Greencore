"""
Módulo de Recompensa: Define as recompensas (troféus) do jogo e a lógica para concedê-las.
"""

from __future__ import annotations

from dataclasses import dataclass

from core import config
from core.models.jogador import Jogador


@dataclass(frozen=True)
class Recompensa:
    dificuldade: str
    nome: str
    arquivo_imagem: str

    @property
    def caminho_imagem(self):
        from core.services import personagens  # import local evita ciclo

        return personagens.caminho_trofeu(self.dificuldade)


class GerenciadorRecompensas:
    """Decide e organiza as recompensas (troféus) do jogador."""

    def __init__(self) -> None:
        self._catalogo: dict[str, Recompensa] = {
            dificuldade: Recompensa(
                dificuldade=dificuldade,
                nome=f"Troféu {dificuldade}",
                arquivo_imagem=arquivo,
            )
            for dificuldade, arquivo in config.TROFEU_POR_DIFICULDADE.items()
        }

    def recompensa_da_dificuldade(self, dificuldade: str) -> Recompensa:
        try:
            return self._catalogo[dificuldade]
        except KeyError as exc:
            raise KeyError(f"Não há recompensa cadastrada para '{dificuldade}'.") from exc

    def avaliar_conquista(
        self, jogador: Jogador, dificuldade: str, pontuacao: int, total_perguntas: int
    ) -> Recompensa | None:
        """
        Verifica se o desempenho do jogador é suficiente para um troféu.
        Critério: acertar 100% das perguntas da rodada. Caso o jogador já
        possua o troféu daquela dificuldade, ele continua sendo "elegível"
        (joga de novo, sem problema), mas ``jogador.conquistar_trofeu``
        simplesmente não duplica o troféu já existente.
        """
        if total_perguntas <= 0:
            return None

        acertou_tudo = pontuacao >= total_perguntas
        if not acertou_tudo:
            return None

        jogador.conquistar_trofeu(dificuldade)
        return self.recompensa_da_dificuldade(dificuldade)

    def listar_trofeus_conquistados(self, jogador: Jogador) -> list[Recompensa]:
        """
        Retorna os troféus do jogador, na ordem de dificuldade do jogo
        (e não na ordem em que foram conquistados), para exibição
        consistente na Sala de Troféus.
        """
        return [
            self._catalogo[dificuldade]
            for dificuldade in config.DIFICULDADES
            if dificuldade in jogador.trofeus
        ]
