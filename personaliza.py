import customtkinter as ctk
from tkinter import colorchooser

class PortfolioPersonalizacao(ctk.CTkFrame):
    """
    Tela para personalizar as cores do template do portfólio.
    """
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self, 
            text="🎨 Personalize o Design do seu Portfólio", 
            font=ctk.CTkFont(size=25, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="n")

        self.desc_label = ctk.CTkLabel(
            self, 
            text="Escolha as cores principais que serão usadas no cabeçalho, caixas de texto e botões.",
            font=ctk.CTkFont(size=14)
        )
        self.desc_label.grid(row=1, column=0, padx=20, pady=(0, 30), sticky="n")
        
        # Frame para os seletores de cor
        color_frame = ctk.CTkFrame(self)
        color_frame.grid(row=2, column=0, padx=20, pady=10, sticky="n")
        color_frame.grid_columnconfigure((0, 2), weight=1)
        
        # --- Seletor de Cor Principal ---
        ctk.CTkLabel(color_frame, text="Cor Principal (Fundo de Seções):", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10)
        self.main_color_var = ctk.StringVar(value=self.controller.design_config["cor_principal"])
        self.main_color_label = ctk.CTkLabel(color_frame, text=self.main_color_var.get(), fg_color=self.main_color_var.get(), width=100, height=30)
        self.main_color_label.grid(row=0, column=1, padx=10, pady=10)
        self.main_color_button = ctk.CTkButton(
            color_frame, 
            text="Selecionar", 
            command=lambda: self._choose_color("cor_principal")
        )
        self.main_color_button.grid(row=0, column=2, padx=10, pady=10)

        # --- Seletor de Cor de Texto/Detalhe (Opcional, mas útil) ---
        ctk.CTkLabel(color_frame, text="Cor Secundária (Texto/Detalhe):", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=10)
        self.secondary_color_var = ctk.StringVar(value=self.controller.design_config["cor_secundaria"])
        self.secondary_color_label = ctk.CTkLabel(color_frame, text=self.secondary_color_var.get(), fg_color=self.secondary_color_var.get(), width=100, height=30)
        self.secondary_color_label.grid(row=1, column=1, padx=10, pady=10)
        self.secondary_color_button = ctk.CTkButton(
            color_frame, 
            text="Selecionar", 
            command=lambda: self._choose_color("cor_secundaria")
        )
        self.secondary_color_button.grid(row=1, column=2, padx=10, pady=10)

        # --- Botões de Navegação ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=4, column=0, padx=20, pady=(40, 20), sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        self.back_button = ctk.CTkButton(
            button_frame, 
            text="Voltar ao Início", 
            command=lambda: controller.show_frame("WelcomeFrame"),
            height=40,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="gray"
        )
        self.back_button.grid(row=0, column=0, padx=10, sticky="e")

        self.next_button = ctk.CTkButton(
            button_frame, 
            text="Gerar Portfólio PDF", 
            command=self._save_and_next,
            height=40,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.next_button.grid(row=0, column=1, padx=10, sticky="w")

    def _choose_color(self, key):
        """Abre o seletor de cores nativo e atualiza o estado."""
        # Abre o seletor de cores. Retorna (RGB, HEX)
        color_code = colorchooser.askcolor(title=f"Escolha a {key}") 
        if color_code and color_code[1]: # Verifica se uma cor foi selecionada (e se não foi cancelado)
            hex_color = color_code[1]
            if key == "cor_principal":
                self.main_color_var.set(hex_color)
                self.main_color_label.configure(text=hex_color, fg_color=hex_color)
            elif key == "cor_secundaria":
                self.secondary_color_var.set(hex_color)
                self.secondary_color_label.configure(text=hex_color, fg_color=hex_color)

    def _save_and_next(self):
        """Salva as configurações de design no controlador e avança."""
        config = {
            "cor_principal": self.main_color_var.get(),
            "cor_secundaria": self.secondary_color_var.get()
        }
        self.controller.set_design_config(config)
        
        # Salva na lista geral de portfólios
        from lista_portfolios import ListaPortfolios
        ListaPortfolios.save_portfolio(self.controller.portfolio_data, config)
        
        self.controller.show_frame("PDFGeneratorFrame")