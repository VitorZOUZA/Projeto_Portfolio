import customtkinter as ctk
import os
import webbrowser
import threading
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from PIL import Image

class PortfolioPDFGenerator(ctk.CTkFrame):
    """
    Tela para renderizar o template HTML, gerar o PDF e abrir o arquivo.
    """
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Label de status/informação
        self.title_label = ctk.CTkLabel(
            self, 
            text="✅ Portfólio Pronto!", 
            font=ctk.CTkFont(size=25, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(40, 10), sticky="n")

        self.info_label = ctk.CTkLabel(
            self, 
            text="Seu portfólio em PDF está pronto para ser gerado.",
            font=ctk.CTkFont(size=14)
        )
        self.info_label.grid(row=1, column=0, padx=20, pady=(0, 40), sticky="n")
        
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.generated_file_path = os.path.join(self.output_dir, "portfolio_profissional.pdf")
        self.html_file_path = os.path.join(self.output_dir, "output_portfolio.html")

        self.generate_button = ctk.CTkButton(
            self, 
            text="Gerar e Salvar PDF", 
            command=self._generate_pdf,
            height=40,
            width=250,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.generate_button.grid(row=2, column=0, padx=20, pady=(0, 20))
        
        self.open_button = ctk.CTkButton(
            self, 
            text="Abrir Portfólio", 
            command=self._open_pdf,
            height=40,
            width=250,
            state="disabled", # Desabilitado até o PDF ser gerado
            fg_color="green" # Cor diferente para destaque
        )
        self.open_button.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="n")

        self.back_button = ctk.CTkButton(
            self, 
            text="Voltar ao Início", 
            command=lambda: controller.show_frame("WelcomeFrame"),
            height=40,
            width=250,
            fg_color="gray"
        )
        self.back_button.grid(row=4, column=0, padx=20, pady=(0, 100), sticky="n")

    def update_data(self):
        """Atualiza a tela quando ela é exibida."""
        self.open_button.configure(state="disabled")
        self.generate_button.configure(text="Gerar e Salvar PDF", state="normal")
        self.info_label.configure(text="Seu portfólio em PDF está pronto para ser gerado.")

    def _process_image_for_template(self, photo_path):
        """Redimensiona, recorta em círculo e salva a imagem para uso no template."""
        if not photo_path or not os.path.exists(photo_path):
            return None # Retorna None se não houver foto

        # --- Tratamento de Imagem com Pillow ---
        try:
            img = Image.open(photo_path).convert("RGBA")
            
            # 1. Redimensionar para um tamanho ideal para o template (Ex: 150x150)
            target_size = 150
            img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)

            # 2. Criar uma máscara circular (para o efeito de círculo no template)
            # Embora o CSS possa fazer o efeito (border-radius: 50%), 
            # redimensionar a imagem é importante para otimização do PDF.
            
            # Salvar a imagem processada temporariamente
            upload_dir = "uploads"
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
                
            processed_img_path = os.path.join(upload_dir, "processed_profile_pic.png")
            img.save(processed_img_path, "PNG")

            return os.path.abspath(processed_img_path)

        except Exception as e:
            print(f"Erro ao processar imagem para PDF: {e}")
            return None
        
    def _generate_pdf(self):
        """Inicia o processo de geração de PDF em uma thread separada."""
        self.generate_button.configure(text="Gerando PDF...", state="disabled")
        self.info_label.configure(text="Aguarde, gerando seu portfólio...", text_color="blue")
        self.open_button.configure(state="disabled")
        
        # Inicia a thread
        threading.Thread(target=self._generate_pdf_task).start()

    def _generate_pdf_task(self):
        """Tarefa de geração do PDF que roda em background."""
        try:
            data = self.controller.portfolio_data
            design = self.controller.design_config
            
            # --- 1. Processar a imagem ---
            processed_img_path = self._process_image_for_template(data.get("photo_path"))
            
            # Adiciona o caminho da imagem processada aos dados
            data["processed_img_path"] = processed_img_path 
            
            # --- 1.5. Sanitizar URLs ---
            # Garante que os links tenham https:// para não serem tratados como locais
            for key in ["linkedin", "instagram"]:
                if data.get(key) and not data[key].startswith(("http://", "https://")):
                    data[key] = f"https://{data[key]}"

            # --- 2. Configurar Jinja2 ---
            # Carrega o ambiente Jinja2 com a pasta 'templates'
            env = Environment(loader=FileSystemLoader("templates"))
            template = env.get_template("portfolio_template.html")
            
            # --- 3. Renderizar o template ---
            # Passa os dados e as configurações de design para o template
            html_output = template.render(
                dados=data,
                design=design
            )
            
            # Salva o HTML gerado (útil para debug)
            with open(self.html_file_path, "w", encoding="utf-8") as f:
                f.write(html_output)
            
            # --- 4. Gerar o PDF com Weasyprint ---
            # Define o base_url para que o WeasyPrint encontre o CSS na pasta templates
            base_url = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
            HTML(string=html_output, base_url=base_url).write_pdf(self.generated_file_path)

            # Sucesso - Agenda a atualização da UI na thread principal
            self.after(0, self._on_generation_success)
            
        except Exception as e:
            print(f"Erro detalhado na geração de PDF: {e}")
            # Erro - Agenda a atualização da UI na thread principal
            self.after(0, lambda: self._on_generation_error(str(e)))

    def _on_generation_success(self):
        """Chamado quando a geração do PDF termina com sucesso."""
        self.info_label.configure(text=f"Portfólio salvo com sucesso em: {os.path.abspath(self.generated_file_path)}", text_color="green")
        self.open_button.configure(state="normal")
        self.generate_button.configure(text="PDF Gerado!", state="disabled")

    def _on_generation_error(self, error_message):
        """Chamado quando ocorre um erro na geração do PDF."""
        self.info_label.configure(text=f"Erro ao gerar PDF: {error_message}", text_color="red")
        self.generate_button.configure(text="Tentar Novamente", state="normal")

    def _open_pdf(self):
        """Abre o arquivo PDF gerado."""
        if os.path.exists(self.generated_file_path):
            webbrowser.open(os.path.abspath(self.generated_file_path))
        else:
            self.info_label.configure(text="O arquivo PDF não foi encontrado.", text_color="red")