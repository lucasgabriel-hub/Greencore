"""
core.services.navegacao
=========================
Controle de navegação entre telas (tarefa do Dia 1 do backend: "configurar
navegação entre telas").

Hoje cada tela do Greencore é um script independente, com seu próprio
loop principal (``mainloop()`` do Tkinter ou ``while True`` do pygame) —
não existe, ainda, um único processo que troque de tela internamente.
Por isso, este módulo não tenta "forçar" essa unificação (isso mudaria o
frontend de forma muito mais profunda do que pedido). Em vez disso, ele
oferece:

1. Um pequeno controlador em memória (``Navegador``), já pronto para ser
   usado por quem futuramente unificar as telas em um só processo.
2. Persistência de "qual foi a última tela utilizada", para o jogo poder,
   por exemplo, voltar direto para a Sala de Troféus se for isso que o
   jogador estava vendo.
"""

from __future__ import annotations

import json

from core import config

TELAS_VALIDAS = {"inicial", "tutorial", "quiz", "trofeus"}


class TelaInvalidaError(ValueError):
    pass


class Navegador:
    """Mantém uma pilha simples de telas visitadas durante a execução."""

    def __init__(self, tela_inicial: str = "inicial"):
        self._validar_tela(tela_inicial)
        self._pilha: list[str] = [tela_inicial]

    @staticmethod
    def _validar_tela(tela: str) -> None:
        if tela not in TELAS_VALIDAS:
            raise TelaInvalidaError(
                f"Tela '{tela}' desconhecida. Telas válidas: {sorted(TELAS_VALIDAS)}"
            )

    @property
    def tela_atual(self) -> str:
        return self._pilha[-1]

    def ir_para(self, tela: str) -> None:
        self._validar_tela(tela)
        self._pilha.append(tela)

    def voltar(self) -> str:
        """Volta para a tela anterior. Nunca esvazia a pilha por completo,
        para sempre haver uma tela "atual" válida."""
        if len(self._pilha) > 1:
            self._pilha.pop()
        return self.tela_atual

    def historico(self) -> list[str]:
        return list(self._pilha)


def salvar_ultima_tela(tela: str) -> None:
    """Persiste qual foi a última tela acessada (arquivo separado do
    progresso do jogador, para não acoplar as duas responsabilidades)."""
    Navegador._validar_tela(tela)  # noqa: SLF001 - validação reaproveitada de propósito
    caminho = config.DATA_DIR / "navegacao.json"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump({"ultima_tela": tela}, f, ensure_ascii=False, indent=2)


def carregar_ultima_tela() -> str:
    caminho = config.DATA_DIR / "navegacao.json"
    if not caminho.exists():
        return "inicial"
    try:
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
        tela = dados.get("ultima_tela", "inicial")
        return tela if tela in TELAS_VALIDAS else "inicial"
    except (json.JSONDecodeError, OSError):
        return "inicial"
