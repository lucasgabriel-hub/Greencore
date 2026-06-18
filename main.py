"""
main.py
========
Ponto de entrada único do Greencore.

Agora todas as telas (Tela Inicial, Tutorial, Quiz, Sala de Troféus)
usam só Tkinter e vivem dentro da MESMA janela (``root``). A classe
``GreencoreApp`` abaixo é o controlador de navegação: ao trocar de
tela, ela apaga todos os widgets da janela atual e constrói os da
próxima — nenhuma janela pygame separada é mais aberta.

Basta rodar `python main.py` (na pasta do projeto) para abrir o jogo a
partir da Tela Inicial.
"""

import sys
import tkinter as tk

from core.services import personagens, navegacao


def verificar_instalacao() -> None:
    """Confere se todos os arquivos de imagem usados pelo jogo (fundos,
    sprites de personagens e troféus) realmente existem em disco. Se
    algo estiver faltando, avisa no terminal mas não impede o jogo de
    abrir (a tela específica que precisar do arquivo ausente é que vai
    falhar, com uma mensagem mais clara do que um traceback cru)."""
    erros = personagens.validar_arquivos_existentes()
    if erros:
        print("Aviso: alguns arquivos de imagem não foram encontrados:")
        for erro in erros:
            print(f"  - {erro}")
        print()


class GreencoreApp:
    """Controlador único de navegação do Greencore.

    Mantém uma única janela (``root``) e troca o conteúdo exibido nela
    conforme o jogador navega entre Tela Inicial, Tutorial, Quiz e Sala
    de Troféus. Cada tela é uma classe própria (TelaInicial, QuizApp,
    TelaTutorial, TelaTrofeus) que recebe ``root`` e este controlador.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Greencore")
        self.root.geometry("1000x750")
        self.tela_atual = None  # mantém referência viva (evita garbage collection das imagens)
        self.mostrar_inicial()

    def _limpar_tela(self) -> None:
        # Remove qualquer atalho de teclado deixado pela tela anterior
        # (ex.: a barra de espaço usada no Tutorial) antes de destruir os
        # widgets, para que ele não dispare em cima de uma tela nova.
        self.root.unbind("<space>")
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_inicial(self) -> None:
        self._limpar_tela()
        navegacao.salvar_ultima_tela("inicial")
        from tela_inicial import TelaInicial
        self.tela_atual = TelaInicial(self.root, self)

    def mostrar_tutorial(self) -> None:
        self._limpar_tela()
        navegacao.salvar_ultima_tela("tutorial")
        from tutorial import TelaTutorial
        self.tela_atual = TelaTutorial(self.root, self)

    def mostrar_quiz(self) -> None:
        self._limpar_tela()
        navegacao.salvar_ultima_tela("quiz")
        from quiz import QuizApp
        self.tela_atual = QuizApp(self.root, controller=self)

    def mostrar_trofeus(self) -> None:
        self._limpar_tela()
        navegacao.salvar_ultima_tela("trofeus")
        from sala_trofeus import TelaTrofeus
        self.tela_atual = TelaTrofeus(self.root, self)


def main() -> int:
    verificar_instalacao()

    root = tk.Tk()
    app = GreencoreApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
