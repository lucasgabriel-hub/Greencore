"""
Módulo principal do Greencore. Contém a função ``main()`` que inicia
o jogo, além da classe ``GreencoreApp`` que controla a navegação entre
as telas do jogo.
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
    """
    Controlador de navegação do Greencore. Mantém a janela principal
    (``root``) e troca de tela conforme o usuário interage com o jogo.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Greencore")
        self.root.geometry("1000x750")
        self.tela_atual = None  
        self.mostrar_inicial()

    def _limpar_tela(self) -> None:
        
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
