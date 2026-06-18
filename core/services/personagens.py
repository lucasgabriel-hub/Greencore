"""
core.services.personagens
===========================
Gerenciamento dos personagens usados nas dicas do quiz e no tutorial
(tarefa do Dia 4 do backend: "gerenciamento dos personagens").

Antes, cada arquivo de frontend escrevia o nome do arquivo de imagem "na
mão" (ex.: ``Image.open("abelha_trabalhadora.png")``), sem checar se o
arquivo de fato existia e sem saber em qual pasta procurar — o que é um
bug real neste projeto, já que as imagens estão em ``sprites_personagens/``
e ``cenarios/``, não na raiz do projeto.

Este módulo centraliza:
- a resolução do caminho absoluto de cada sprite;
- um pequeno cadastro (registro) de personagens com um "papel" amigável,
  útil tanto para o quiz quanto para o tutorial;
- validação de que os arquivos realmente existem em disco.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core import config


class PersonagemNaoEncontradoError(FileNotFoundError):
    """Levantada quando o arquivo de sprite de um personagem não existe."""


@dataclass(frozen=True)
class Personagem:
    arquivo: str
    papel: str  # breve descrição do papel do personagem (usado no tutorial/dicas)

    @property
    def caminho(self) -> Path:
        return caminho_personagem(self.arquivo)

    def existe(self) -> bool:
        return self.caminho.exists()


# Registro central de personagens conhecidos pelo jogo. Mantém, em um único
# lugar, a relação entre o arquivo de sprite e o papel do personagem — hoje
# usado apenas como metadado, mas que evita "espalhar" essas strings pelos
# arquivos de frontend.
_REGISTRO: dict[str, Personagem] = {
    "abelha_trabalhadora.png": Personagem("abelha_trabalhadora.png", "Trabalho em equipe"),
    "arara_azul.png": Personagem("arara_azul.png", "Conquistas e troféus"),
    "guardiao_floresta.png": Personagem("guardiao_floresta.png", "Proteção ambiental"),
    "inseto_engenhoso.png": Personagem("inseto_engenhoso.png", "Explicação de regras"),
    "lemure_divertido.png": Personagem("lemure_divertido.png", "Boas-vindas / introdução"),
    "peixe_aventureiro.png": Personagem("peixe_aventureiro.png", "Vida marinha"),
    "protetor_arvores.png": Personagem("protetor_arvores.png", "Reflorestamento"),
    "tartaruga_sabia.png": Personagem("tartaruga_sabia.png", "Dicas e sabedoria"),
    "robo_ecologico.png": Personagem("robo_ecologico.png", "Tecnologia sustentável"),
    "urso_ecologico.png": Personagem("urso_ecologico.png", "Equilíbrio com a natureza"),
}


def caminho_personagem(arquivo: str) -> Path:
    """Resolve o caminho absoluto do sprite de um personagem."""
    return config.SPRITES_PERSONAGENS_DIR / arquivo


def caminho_fundo(arquivo: str) -> Path:
    """Resolve o caminho absoluto de uma imagem de cenário/fundo."""
    return config.CENARIOS_DIR / arquivo


def caminho_trofeu(dificuldade: str) -> Path:
    """Resolve o caminho absoluto do troféu de uma dificuldade."""
    arquivo = config.TROFEU_POR_DIFICULDADE.get(dificuldade)
    if arquivo is None:
        raise KeyError(f"Não existe troféu cadastrado para a dificuldade '{dificuldade}'.")
    return config.SPRITES_TROFEUS_DIR / arquivo


def obter_personagem(arquivo: str) -> Personagem:
    """Retorna o registro de um personagem; cria um registro mínimo se for
    um personagem novo que ainda não está no cadastro (ex.: adicionado pelo
    designer sem atualizar este arquivo), em vez de quebrar o jogo."""
    return _REGISTRO.get(arquivo, Personagem(arquivo, "Personagem do Greencore"))


def listar_personagens() -> list[Personagem]:
    return list(_REGISTRO.values())


def validar_arquivos_existentes() -> list[str]:
    """Confere, em disco, se todos os sprites cadastrados realmente existem.

    Retorna uma lista de mensagens de erro (vazia = tudo certo). Pensado
    para ser usado nos testes finais, evitando descobrir um sprite
    faltante apenas quando o jogo já travou em produção.
    """
    erros: list[str] = []
    for personagem in listar_personagens():
        if not personagem.existe():
            erros.append(
                f"Sprite '{personagem.arquivo}' não encontrado em {config.SPRITES_PERSONAGENS_DIR}"
            )

    for dificuldade in config.TROFEU_POR_DIFICULDADE:
        caminho = caminho_trofeu(dificuldade)
        if not caminho.exists():
            erros.append(f"Troféu da dificuldade '{dificuldade}' não encontrado em {caminho}")

    return erros
