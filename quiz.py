import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from core.models.quiz import Quiz
from core.services import persistencia, personagens

"""
classe QuizApp é a interface gráfica do quiz, permitindo ao jogador selecionar a dificuldade, responder perguntas, 
ver dicas e acompanhar o tempo e pontuação. Ela gerencia o fluxo do jogo, incluindo a exibição de perguntas, alternativas, 
dicas e resultados finais. A classe também lida com a persistência do progresso do jogador entre sessões.
"""

class QuizApp:
    def __init__(self, root, controller=None):
        self.root = root
        self.root.title("Greencore")
        self.timer_id = None
        self.controller = controller

        """
        Inicializa o aplicativo de quiz, configurando a janela principal, carregando o progresso do jogador 
        e preparando a interface gráfica.
        """
        self.jogador = persistencia.carregar_progresso()
        self.quiz: Quiz | None = None
        bg_image = Image.open(personagens.caminho_fundo("fundo_greencore.png"))
        bg_image = bg_image.resize((1600, 1200), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        self.canvas = tk.Canvas(root, width=self.bg_photo.width(), height=self.bg_photo.height())
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        self.criar_tela_inicial()

        """
        Cria a tela inicial do quiz, permitindo ao jogador escolher a dificuldade do jogo.
        """
    def criar_tela_inicial(self):
        self.titulo_label = tk.Label(self.root, text="🌱 Bem-vindo ao Quiz Greencore!",
                                      font=("Arial", 18, "bold"), bg="#ffffff")
        self.titulo_label.place(relx=0.5, rely=0.2, anchor="center")

        self.btn_facil = tk.Button(self.root, text="Fácil", width=20, command=lambda: self.iniciar_quiz("Fácil"))
        self.btn_facil.place(relx=0.5, rely=0.4, anchor="center")

        self.btn_medio = tk.Button(self.root, text="Médio", width=20, command=lambda: self.iniciar_quiz("Médio"))
        self.btn_medio.place(relx=0.5, rely=0.5, anchor="center")

        self.btn_dificil = tk.Button(self.root, text="Difícil", width=20, command=lambda: self.iniciar_quiz("Difícil"))
        self.btn_dificil.place(relx=0.5, rely=0.6, anchor="center")

        self.btn_pesadelo = tk.Button(self.root, text="Pesadelo", width=20,
                                       command=lambda: self.iniciar_quiz("Pesadelo"))
        self.btn_pesadelo.place(relx=0.5, rely=0.7, anchor="center")

    def destruir_tela_inicial(self):
        self.titulo_label.destroy()
        self.btn_facil.destroy()
        self.btn_medio.destroy()
        self.btn_dificil.destroy()
        self.btn_pesadelo.destroy()

    """
    Inicia o quiz com a dificuldade selecionada, destruindo a tela inicial e configurando os widgets do quiz.
    """
    def iniciar_quiz(self, dificuldade):
        self.destruir_tela_inicial()

        self.quiz = Quiz(jogador=self.jogador)
        self.quiz.iniciar(dificuldade)

        self.criar_widgets_quiz()
        self.carregar_pergunta()

    def criar_widgets_quiz(self):
        # Pergunta
        self.pergunta_label = tk.Label(self.root, text="", font=("Arial", 16), bg="#ffffff")
        self.pergunta_label.place(relx=0.5, rely=0.2, anchor="center")

        self.buttons = []
        for i in range(4):
            btn = tk.Button(self.root, text="", width=30, command=lambda i=i: self.verificar_resposta(i))
            btn.place(relx=0.5, rely=0.35 + i * 0.08, anchor="center")
            self.buttons.append(btn)

        self.info_label = tk.Label(self.root, text="", font=("Arial", 12), bg="#ffffff")
        self.info_label.place(relx=0.5, rely=0.7, anchor="center")

        self.dica_btn = tk.Button(self.root, text="Mostrar Dica", command=self.mostrar_dica)
        self.dica_btn.place(relx=0.5, rely=0.75, anchor="center")

        self.sair_btn = tk.Button(self.root, text="Sair", command=self.voltar_inicio, bg="red", fg="white")
        self.sair_btn.place(relx=0.9, rely=0.05, anchor="center")

        self.dica_frame = tk.Frame(self.root, bg="#e6f7ff", bd=3, relief="ridge")
        self.dica_frame.place(relx=0.5, rely=0.88, anchor="center")

        self.personagem_label = tk.Label(self.dica_frame, bg="#e6f7ff")
        self.personagem_label.pack(side="left", padx=10)

        self.dica_label = tk.Label(self.dica_frame, text="", font=("Arial", 11, "italic"),
                                    fg="black", bg="#e6f7ff", wraplength=300, justify="left")
        self.dica_label.pack(side="left", padx=10, pady=5)

    def destruir_widgets_quiz(self):
        self.pergunta_label.destroy()
        self.info_label.destroy()
        self.dica_btn.destroy()
        self.sair_btn.destroy()
        self.dica_frame.destroy()
        for btn in self.buttons:
            btn.destroy()

    def voltar_inicio(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        self.destruir_widgets_quiz()

        if self.controller:
            self.controller.mostrar_inicial()
        else:
            self.criar_tela_inicial()

    def carregar_pergunta(self):
        if self.quiz.terminou:
            self.finalizar_quiz()
            return

        pergunta_atual = self.quiz.pergunta_atual
        self.pergunta_label.config(text=pergunta_atual.texto)

        alternativas = pergunta_atual.alternativas_embaralhadas()
        for i, alt in enumerate(alternativas):
            self.buttons[i].config(text=alt)

        self.dica_label.config(text="")
        self.personagem_label.config(image="")

        self.atualizar_timer()

    def atualizar_timer(self):
        tempo = self.quiz.tempo_restante
        self.info_label.config(text=f"⏱ Tempo: {tempo}s | ⭐ Pontuação: {self.quiz.pontuacao}")

        if tempo > 0:
            self.quiz.tick()
            self.timer_id = self.root.after(1000, self.atualizar_timer)
        else:
            messagebox.showwarning("Tempo esgotado", "Você não respondeu a tempo!")
            resultado = self.quiz.registrar_tempo_esgotado()
            self.apos_responder(resultado)

    def verificar_resposta(self, i):
        resposta = self.buttons[i].cget("text")

        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        resultado = self.quiz.responder(resposta)
        self.apos_responder(resultado)

    def apos_responder(self, resultado):
        if resultado.fim_da_partida:
            self.finalizar_quiz()
        else:
            self.carregar_pergunta()

    def mostrar_dica(self):
        dica = self.quiz.pedir_dica()
        if dica is None:
            messagebox.showinfo("Dica", "Você já usou a dica disponível para esta pergunta.")
            return

        self.dica_label.config(text=f"💬 {dica}")

        caminho_imagem = personagens.caminho_personagem(self.quiz.personagem_da_dica())
        try:
            img = Image.open(caminho_imagem)
            img = img.resize((100, 100))
            self.personagem_photo = ImageTk.PhotoImage(img)
            self.personagem_label.config(image=self.personagem_photo)
        except (FileNotFoundError, OSError):
            self.personagem_label.config(image="")
    
    """
    Finaliza o quiz, exibindo a pontuação final e se o jogador conquistou algum troféu.
    """

    def finalizar_quiz(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        resultado = self.quiz.finalizar()
        persistencia.salvar_progresso(self.jogador)

        mensagem = f"Pontuação final: {resultado.pontuacao}/{resultado.total_perguntas}"
        if resultado.trofeu_conquistado:
            mensagem += f"\n🏆 Parabéns! Você conquistou o {resultado.trofeu.nome}!"
        messagebox.showinfo("Fim do Quiz", mensagem)

        self.voltar_inicio()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
