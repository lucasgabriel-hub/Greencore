import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # garante compatibilidade com PNG

from core.services import personagens


class TelaInicial:
    """
    Classe que representa a tela inicial do jogo Greencore.
    """

    def __init__(self, root, controller=None):
        self.root = root
        self.controller = controller

        """
        Inicializa a tela inicial do Greencore.
        :param root: A janela principal do Tkinter.
        :param controller: O controlador de navegação (opcional).
        """
        imagem = Image.open(personagens.caminho_fundo("fundo_pixel.png"))
        imagem = imagem.resize((1600, 1200))
        self.bg_image = ImageTk.PhotoImage(imagem)

        self.bg_label = tk.Label(root, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)
        self.frame = tk.Frame(root, bg="#ffffff", bd=3, relief="ridge")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        titulo = tk.Label(self.frame, text="Greencore", font=("Press Start 2P", 20, "bold"),
                          fg="#1b5e20", bg="#ffffff")
        titulo.pack(pady=20)

        style = ttk.Style()
        style.configure("TButton", font=("Arial", 14, "bold"), padding=10)

        btn_jogar = ttk.Button(self.frame, text="▶ Jogar", command=lambda: self.acao("Jogar"))
        btn_jogar.pack(pady=8, fill="x")

        btn_tutorial = ttk.Button(self.frame, text="❓ Tutorial", command=lambda: self.acao("Tutorial"))
        btn_tutorial.pack(pady=8, fill="x")

        btn_recompensas = ttk.Button(self.frame, text="🏆 Recompensas", command=lambda: self.acao("Recompensas"))
        btn_recompensas.pack(pady=8, fill="x")

        btn_sair = ttk.Button(self.frame, text="✖ Sair", command=self._sair)
        btn_sair.pack(pady=8, fill="x")

        """
        Cria o rodapé da tela inicial.
        """
        self.rodape = tk.Label(root, text="Greencore Project © 2026",
                          font=("Arial", 10), bg="#ffffff", fg="#388e3c")
        self.rodape.place(relx=0.5, rely=0.95, anchor="center")

    def acao(self, texto):
        """
        Executa a ação correspondente ao botão clicado.
        :param texto: O texto do botão clicado.
        """
        print(f"Ação escolhida: {texto}")

        if self.controller is None:
            return

        if texto == "Jogar":
            self.controller.mostrar_quiz()
        elif texto == "Tutorial":
            self.controller.mostrar_tutorial()
        elif texto == "Recompensas":
            self.controller.mostrar_trofeus()

    def _sair(self):
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Greencore - Tela Inicial")
    app = TelaInicial(root)
    root.mainloop()
