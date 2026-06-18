"""
Módulo responsável por carregar e validar o banco de perguntas a partir do
arquivo JSON.
"""

from __future__ import annotations

import json
from functools import lru_cache

from core import config
from core.models.pergunta import Pergunta, PerguntaInvalidaError


class BancoPerguntasError(Exception):
    """Erro genérico ao carregar/validar o banco de perguntas."""


@lru_cache(maxsize=1)
def _carregar_bruto() -> dict:
    """Lê o arquivo JSON do disco (apenas uma vez, graças ao cache)."""
    if not config.ARQUIVO_PERGUNTAS.exists():
        raise BancoPerguntasError(
            f"Arquivo de perguntas não encontrado em {config.ARQUIVO_PERGUNTAS}"
        )

    try:
        with open(config.ARQUIVO_PERGUNTAS, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise BancoPerguntasError(
            f"O arquivo de perguntas está com um JSON inválido: {exc}"
        ) from exc


def limpar_cache() -> None:
    _carregar_bruto.cache_clear()
    carregar_perguntas.cache_clear()


@lru_cache(maxsize=None)
def carregar_perguntas(dificuldade: str) -> tuple[Pergunta, ...]:
    """
    Carrega e valida todas as perguntas de uma dificuldade.
    Levanta ``BancoPerguntasError`` caso a dificuldade não exista no banco
    ou caso alguma pergunta esteja malformada (em vez de deixar o erro
    estourar lá na interface, no meio de um clique de botão).
    """
    bruto = _carregar_bruto()

    if dificuldade not in bruto:
        raise BancoPerguntasError(
            f"Dificuldade '{dificuldade}' não existe no banco de perguntas. "
            f"Opções disponíveis: {', '.join(bruto.keys())}"
        )

    perguntas: list[Pergunta] = []
    for i, dados in enumerate(bruto[dificuldade]):
        try:
            perguntas.append(Pergunta.from_dict(dados, dificuldade=dificuldade))
        except PerguntaInvalidaError as exc:
            raise BancoPerguntasError(
                f"Pergunta inválida na dificuldade '{dificuldade}' (índice {i}): {exc}"
            ) from exc

    if not perguntas:
        raise BancoPerguntasError(
            f"Não há nenhuma pergunta cadastrada para a dificuldade '{dificuldade}'."
        )

    return tuple(perguntas)


def dificuldades_disponiveis() -> list[str]:
    return list(_carregar_bruto().keys())


def validar_banco_completo() -> list[str]:
    """
    Valida todas as dificuldades cadastradas e retorna uma lista de erros.
    Lista vazia significa que o banco inteiro está consistente. Pensado
    para ser usado em testes finais / verificação de integridade dos dados.
    """
    erros: list[str] = []
    for dificuldade in dificuldades_disponiveis():
        try:
            carregar_perguntas(dificuldade)
        except BancoPerguntasError as exc:
            erros.append(str(exc))
    return erros
