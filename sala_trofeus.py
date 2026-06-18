import tkinter as tk
from PIL import Image, ImageTk

from core.services import persistencia, personagens
from core.models.recompensa import GerenciadorRecompensas

class TelaTrofeus:
    """
    Sala de Troféus, agora em Tkinter (antes era uma janela pygame
    separada). Mostra os troféus realmente conquistados pelo jogador,
    lidos do progresso salvo em disco.
    """

    def __init__(self, root, controller=None):
        self.root = root
        self.controller = controller
        """
        Inicializa a tela de troféus, carregando o progresso do jogador e exibindo os troféus conquistados.
        """
        self._trofeu_photos = []

        """
        Carrega a imagem de fundo da sala de troféus e a redimensiona para se ajustar à janela.
        """
        bg_image = Image.open(personagens.caminho_fundo("fundo_sala_trofeu.png"))
        bg_image = bg_image.resize((1600, 1200), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        self.bg_label = tk.Label(root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        titulo = tk.Label(root, text="🏆 Sala de Troféus", font=("Arial", 22, "bold"),
                           bg="#ffffff", fg="#1b5e20")
        titulo.place(relx=0.5, rely=0.12, anchor="center")

        """
        Carrega o progresso do jogador, lista os troféus conquistados e exibe-os na tela.
        """
        jogador = persistencia.carregar_progresso()
        gerenciador = GerenciadorRecompensas()
        recompensas = gerenciador.listar_trofeus_conquistados(jogador)
        ultimo_nivel = jogador.ultima_dificuldade_com_trofeu()

        self.trofeu_frame = tk.Frame(root, bg="#ffffff", bd=3, relief="ridge")
        self.trofeu_frame.place(relx=0.5, rely=0.5, anchor="center")

        if recompensas:
            subtitulo = tk.Label(self.trofeu_frame, text="Seus troféus conquistados:",
                                  font=("Arial", 14), bg="#ffffff")
            subtitulo.pack(pady=(20, 10))

            linha = tk.Frame(self.trofeu_frame, bg="#ffffff")
            linha.pack(padx=30, pady=10)

            for recompensa in recompensas:
                imagem = Image.open(recompensa.caminho_imagem)
                imagem = imagem.resize((150, 150), Image.Resampling.LANCZOS)
                foto = ImageTk.PhotoImage(imagem)
                self._trofeu_photos.append(foto)

                celula = tk.Frame(linha, bg="#ffffff")
                celula.pack(side="left", padx=15)
                tk.Label(celula, image=foto, bg="#ffffff").pack()
                tk.Label(celula, text=recompensa.dificuldade, font=("Arial", 11, "bold"),
                         bg="#ffffff").pack()

            if ultimo_nivel:
                parabens = tk.Label(
                    self.trofeu_frame,
                    text=f"🎉 Parabéns! Você conquistou o troféu do nível {ultimo_nivel}!",
                    font=("Arial", 12, "bold"), bg="#ffffff", fg="#1b5e20",
                    wraplength=500, justify="center",
                )
                parabens.pack(pady=(5, 20))
            else:
                tk.Label(self.trofeu_frame, text="", bg="#ffffff").pack(pady=(0, 15))
        else:
            tk.Label(
                self.trofeu_frame,
                text="Nenhum troféu ainda... acerte 10/10 para conquistar!",
                font=("Arial", 14), bg="#ffffff", wraplength=400, justify="center",
            ).pack(padx=40, pady=40)

        self.btn_voltar = tk.Button(root, text="◀ Voltar", font=("Arial", 11, "bold"),
                                     command=self.voltar)
        self.btn_voltar.place(relx=0.1, rely=0.05, anchor="center")

    def voltar(self):
        if self.controller:
            self.controller.mostrar_inicial()
        else:
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Greencore - Sala de Troféus")
    app = TelaTrofeus(root)
    root.mainloop()
