"""
Configurações e regras de jogo centralizadas.
Reúne, em um único lugar, tudo que antes estava espalhado (e duplicado)
pelos arquivos de frontend: caminhos de assets, tempo por dificuldade,
pontuação por dificuldade e limites de uso de dica.
Qualquer ajuste de "regra de jogo" deve ser feito aqui, e não dentro dos
arquivos de interface (tela_inicial.py, quiz.py, tutorial.py, sala_trofeus.py).
"""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CENARIOS_DIR = BASE_DIR / "cenarios"
SPRITES_PERSONAGENS_DIR = BASE_DIR / "sprites_personagens"
SPRITES_TROFEUS_DIR = BASE_DIR / "sprites_trofeus"

DATA_DIR = Path(__file__).resolve().parent / "data"
ARQUIVO_PERGUNTAS = DATA_DIR / "perguntas.json"
ARQUIVO_PROGRESSO = DATA_DIR / "progresso.json"

# ---------------------------------------------------------------------------
# Regras de jogo
# ---------------------------------------------------------------------------
DIFICULDADES = ["Fácil", "Médio", "Difícil", "Pesadelo"]

TEMPO_POR_DIFICULDADE = {
    "Fácil": 60,
    "Médio": 45,
    "Difícil": 30,
    "Pesadelo": 15,
}

PONTOS_POR_DIFICULDADE = {
    "Fácil": 1,
    "Médio": 2,
    "Difícil": 3,
    "Pesadelo": 5,
}


MAX_DICAS_POR_PERGUNTA = 1

TROFEU_POR_DIFICULDADE = {
    "Fácil": "trofeu_facil.png",
    "Médio": "trofeu_medio.png",
    "Difícil": "trofeu_dificil.png",
    "Pesadelo": "trofeu_pesadelo.png",
}


def tempo_para_dificuldade(dificuldade: str) -> int:
    """
    Retorna o tempo (segundos) configurado para a dificuldade informada.
    Mantém um valor padrão seguro caso uma dificuldade desconhecida seja
    informada, evitando KeyError em tempo de execução.
    """
    return TEMPO_POR_DIFICULDADE.get(dificuldade, 15)


def pontos_para_dificuldade(dificuldade: str) -> int:
    return PONTOS_POR_DIFICULDADE.get(dificuldade, 1)
