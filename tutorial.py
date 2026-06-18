import tkinter as tk
from PIL import Image, ImageTk

from core import config
from core.services import personagens


class TelaTutorial:
    """
    Tela de tutorial do jogo, com diálogos e imagens de personagens.
    """

    def __init__(self, root, controller=None):
        self.root = root
        self.controller = controller
        self.dialogos = self._montar_dialogos()
        self.index = 0
        self._personagem_photos = {}

        """
        Configuração da interface gráfica: fundo, personagem, diálogo e botões.
        """
        bg_image = Image.open(personagens.caminho_fundo("fundo_tutorial.png"))
        bg_image = bg_image.resize((1600, 1200), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        self.bg_label = tk.Label(root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        self.personagem_label = tk.Label(root, bg="#ffffff")
        self.personagem_label.place(relx=0.5, rely=0.35, anchor="center")

        self.dialogo_frame = tk.Frame(root, bg="#ffffff", bd=3, relief="ridge")
        self.dialogo_frame.place(relx=0.5, rely=0.62, anchor="center")
        self.dialogo_label = tk.Label(self.dialogo_frame, text="", font=("Arial", 14),
                                       bg="#ffffff", wraplength=550, justify="left")
        self.dialogo_label.pack(padx=25, pady=25)

        self.btn_proximo = tk.Button(root, text="Próximo ▶", font=("Arial", 12, "bold"),
                                      command=self.proximo)
        self.btn_proximo.place(relx=0.5, rely=0.78, anchor="center")

        self.btn_sair = tk.Button(root, text="Sair", bg="#c83232", fg="white",
                                   command=self.sair)
        self.btn_sair.place(relx=0.9, rely=0.05, anchor="center")
        self.root.bind("<space>", self._avancar_com_espaco)

        self.mostrar_dialogo_atual()

    def _montar_dialogos(self):
        """
        Monta a lista de diálogos do tutorial.
        Os tempos por dificuldade ("Fácil → 60 segundos...") são gerados
        a partir de core.config.TEMPO_POR_DIFICULDADE em vez de strings
        fixas, para nunca ficarem desatualizados em relação ao jogo.
        """
        dialogos = [
            ("Bem-vindo ao Greencore!", "lemure_divertido.png"),
            ("Este é o modo Tutorial do Quiz.", "lemure_divertido.png"),
            ("Você deve responder antes do tempo acabar.", "lemure_divertido.png"),
            ("Níveis de dificuldade:", "inseto_engenhoso.png"),
        ]

        for dificuldade in config.DIFICULDADES:
            segundos = config.tempo_para_dificuldade(dificuldade)
            if dificuldade == "Pesadelo":
                texto = f"{dificuldade} → apenas {segundos} segundos!"
            else:
                texto = f"{dificuldade} → {segundos} segundos por pergunta."
            dialogos.append((texto, "inseto_engenhoso.png"))

        dialogos.extend([
            ("Use o botão de Dica se ficar em dúvida.", "tartaruga_sabia.png"),
            (f"Você pode usar {config.MAX_DICAS_POR_PERGUNTA} dica por pergunta!", "tartaruga_sabia.png"),
            ("Ao acertar todas as perguntas de um nível...", "arara_azul.png"),
            ("Você conquista um troféu especial!", "arara_azul.png"),
            ("Todos os troféus ficam guardados na Sala de Troféus.", "arara_azul.png"),
            ("Lá você pode ver seu progresso acumulado.", "arara_azul.png"),
            ("Boa sorte, clique em Próximo para começar!", "lemure_divertido.png"),
        ])
        return dialogos

    def mostrar_dialogo_atual(self):
        texto, arquivo_personagem = self.dialogos[self.index]
        self.dialogo_label.config(text=texto)

        if arquivo_personagem not in self._personagem_photos:
            caminho = personagens.caminho_personagem(arquivo_personagem)
            imagem = Image.open(caminho).resize((220, 220), Image.Resampling.LANCZOS)
            self._personagem_photos[arquivo_personagem] = ImageTk.PhotoImage(imagem)

        self.personagem_label.config(image=self._personagem_photos[arquivo_personagem])

    def proximo(self):
        self.index = (self.index + 1) % len(self.dialogos)
        self.mostrar_dialogo_atual()

    def _avancar_com_espaco(self, _event):
        self.proximo()

    def sair(self):
        self.root.unbind("<space>")
        if self.controller:
            self.controller.mostrar_inicial()
        else:
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Greencore - Tutorial")
    app = TelaTutorial(root)
    root.mainloop()
