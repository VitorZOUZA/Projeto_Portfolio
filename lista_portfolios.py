import customtkinter as ctk
import json
import os
from datetime import datetime
from PIL import Image
from relatorios import GeradorRelatorios
import hashlib

class ListaPortfolios(ctk.CTkFrame):
    """
    Tela para visualizar todos os portfólios registrados.
    """
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.portfolios_file = "portfolios_registrados.json"
        self.chart_gen = GeradorRelatorios(output_dir="uploads/charts")
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Título
        self.title_label = ctk.CTkLabel(
            self, 
            text="📋 Portfólios Registrados", 
            font=ctk.CTkFont(size=25, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="n")
        
        # Frame scrollable para a lista
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Botão voltar
        self.back_button = ctk.CTkButton(
            self, 
            text="Voltar ao Início", 
            command=lambda: controller.show_frame("WelcomeFrame"),
            height=40,
            width=200,
            fg_color="gray"
        )
        self.back_button.grid(row=2, column=0, padx=20, pady=(0, 20))
        
    def update_data(self):
        """Atualiza a lista de portfólios ao exibir a tela."""
        # Limpa a lista atual
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Cria diretório de gráficos se não existir
        if not os.path.exists("uploads/charts"):
            os.makedirs("uploads/charts")
        
        portfolios = self._load_portfolios()
        
        if not portfolios:
            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="Nenhum portfólio registrado ainda.\nCrie seu primeiro portfólio!",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            empty_label.grid(row=0, column=0, pady=50)
        else:
            for idx, portfolio in enumerate(portfolios):
                self._create_portfolio_card(portfolio, idx)
    
    def _create_portfolio_card(self, portfolio, index):
        """Cria um card para cada portfólio."""
        card = ctk.CTkFrame(self.scrollable_frame, fg_color="#f0f0f0", corner_radius=10)
        card.grid(row=index, column=0, sticky="ew", padx=10, pady=10)
        card.grid_columnconfigure(0, weight=1)
        
        # Nome
        name_label = ctk.CTkLabel(
            card,
            text=portfolio.get("nome", "Sem nome"),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000",
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        # Título profissional
        title_label = ctk.CTkLabel(
            card,
            text=portfolio.get("titulo", "Sem título"),
            font=ctk.CTkFont(size=14),
            text_color="#333333",
            anchor="w"
        )
        title_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 5))
        
        # Email
        email_label = ctk.CTkLabel(
            card,
            text=f"📧 {portfolio.get('email', 'Sem email')}",
            font=ctk.CTkFont(size=12),
            text_color="#1a1a1a",
            anchor="w"
        )
        email_label.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 5))
        
        # Formação
        formacao = portfolio.get("formacao_curso", "")
        if formacao:
            formacao_label = ctk.CTkLabel(
                card,
                text=f"🎓 {formacao} - {portfolio.get('formacao_instituicao', '')}",
                font=ctk.CTkFont(size=11),
                text_color="#1a1a1a",
                anchor="w"
            )
            formacao_label.grid(row=3, column=0, sticky="w", padx=15, pady=(0, 5))
        
        # Badges de habilidades
        badges_frame = ctk.CTkFrame(card, fg_color="transparent")
        badges_frame.grid(row=4, column=0, sticky="w", padx=15, pady=(5, 5))
        
        skills = []
        if portfolio.get("habilidades_frontend_list"):
            skills.extend(portfolio["habilidades_frontend_list"][:3])
        if portfolio.get("habilidades_backend_list"):
            skills.extend(portfolio["habilidades_backend_list"][:2])
        
        for i, skill in enumerate(skills[:5]):
            badge = ctk.CTkLabel(
                badges_frame,
                text=skill,
                font=ctk.CTkFont(size=9),
                fg_color="#3498db",
                text_color="white",
                corner_radius=5,
                padx=6,
                pady=2
            )
            badge.grid(row=0, column=i, padx=2)
        
        # Mini gráfico de habilidades (matplotlib)
        chart_path = self._generate_skills_chart(portfolio)
        if chart_path and os.path.exists(chart_path):
            try:
                img = Image.open(chart_path)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(200, 130))
                chart_label = ctk.CTkLabel(card, image=ctk_img, text="")
                chart_label.grid(row=5, column=0, sticky="w", padx=15, pady=(8, 8))
            except Exception as e:
                print(f"Erro ao carregar gráfico: {e}")
        
        # Data de criação
        date_label = ctk.CTkLabel(
            card,
            text=f"📅 {portfolio.get('data_criacao', 'Data desconhecida')}",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        date_label.grid(row=6, column=0, sticky="w", padx=15, pady=(0, 15))
        
        # Botão carregar
        load_button = ctk.CTkButton(
            card,
            text="Carregar",
            width=100,
            height=30,
            command=lambda p=portfolio: self._load_portfolio(p)
        )
        load_button.grid(row=0, column=1, rowspan=7, padx=15, pady=15)
    
    def _load_portfolio(self, portfolio):
        """Carrega um portfólio selecionado."""
        self.controller.set_portfolio_data(portfolio)
        if "design_config" in portfolio:
            self.controller.set_design_config(portfolio["design_config"])
        self.controller.show_frame("FormsFrame")
    
    def _load_portfolios(self):
        """Carrega a lista de portfólios do arquivo JSON."""
        if not os.path.exists(self.portfolios_file):
            return []
        
        try:
            with open(self.portfolios_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar portfólios: {e}")
            return []
    
    def _generate_skills_chart(self, portfolio):
        """Gera um mini gráfico de habilidades para o card."""
        frontend = len(portfolio.get("habilidades_frontend_list", []))
        backend = len(portfolio.get("habilidades_backend_list", []))
        soft = len(portfolio.get("habilidades_soft_list", []))
        
        if frontend == 0 and backend == 0 and soft == 0:
            return None
        
        categories = []
        values = []
        
        if frontend > 0:
            categories.append("Frontend")
            values.append(frontend)
        if backend > 0:
            categories.append("Backend")
            values.append(backend)
        if soft > 0:
            categories.append("Soft")
            values.append(soft)
        
        # Gera nome único baseado no email
        email_hash = hashlib.md5(portfolio.get("email", "default").encode()).hexdigest()[:8]
        filename = f"mini_chart_{email_hash}.png"
        
        color = portfolio.get("design_config", {}).get("cor_principal", "#3498db")
        return self.chart_gen.generate_mini_bar_chart(categories, values, filename, color)
    
    @staticmethod
    def save_portfolio(portfolio_data, design_config):
        """Salva um portfólio na lista geral."""
        portfolios_file = "portfolios_registrados.json"
        
        # Carrega portfólios existentes
        if os.path.exists(portfolios_file):
            try:
                with open(portfolios_file, "r", encoding="utf-8") as f:
                    portfolios = json.load(f)
            except:
                portfolios = []
        else:
            portfolios = []
        
        # Adiciona data de criação
        portfolio_data["data_criacao"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        portfolio_data["design_config"] = design_config
        
        # Verifica se já existe (por email) e atualiza, senão adiciona
        email = portfolio_data.get("email")
        found = False
        for i, p in enumerate(portfolios):
            if p.get("email") == email:
                portfolios[i] = portfolio_data
                found = True
                break
        
        if not found:
            portfolios.append(portfolio_data)
        
        # Salva
        try:
            with open(portfolios_file, "w", encoding="utf-8") as f:
                json.dump(portfolios, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erro ao salvar portfólio na lista: {e}")
