"""
core.services.persistencia
============================
Salvamento e carregamento do progresso do jogador em JSON (tarefa do
Dia 5 do backend: "salvamento em JSON").

A escrita é feita de forma "atômica" (grava em um arquivo temporário e só
depois substitui o arquivo final) para reduzir o risco de corromper o
progresso do jogador caso o jogo seja encerrado no meio de uma gravação.
"""

from __future__ import annotations

import json
import os
import tempfile

from core import config
from core.models.jogador import Jogador


def salvar_progresso(jogador: Jogador, caminho=None) -> None:
    """Persiste o estado do jogador em disco, em formato JSON."""
    caminho = caminho or config.ARQUIVO_PROGRESSO
    caminho.parent.mkdir(parents=True, exist_ok=True)

    dados = jogador.to_dict()

    # Escrita atômica: grava em arquivo temporário no mesmo diretório e
    # substitui o arquivo final só depois que a escrita terminou com sucesso.
    fd, caminho_temp = tempfile.mkstemp(dir=caminho.parent, prefix=".tmp_progresso_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        os.replace(caminho_temp, caminho)
    except Exception:
        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)
        raise


def carregar_progresso(caminho=None) -> Jogador:
    """Carrega o progresso salvo do jogador.

    Se o arquivo não existir (primeira vez que o jogo é executado) ou
    estiver corrompido, devolve um ``Jogador`` novo em vez de derrubar o
    jogo — assim uma falha de leitura nunca impede o jogador de jogar.
    """
    caminho = caminho or config.ARQUIVO_PROGRESSO

    if not caminho.exists():
        return Jogador()

    try:
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
        return Jogador.from_dict(dados)
    except (json.JSONDecodeError, KeyError, OSError):
        return Jogador()
