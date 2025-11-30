import customtkinter as ctk
import os
import webbrowser
import threading
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from PIL import Image
import fitz # PyMuPDF
from relatorios import GeradorRelatorios
import random
import pathlib

class PortfolioPDFGenerator(ctk.CTkFrame):
    """
    Tela para renderizar o template HTML, gerar o PDF e abrir o arquivo.
    """
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        
        # Configuração do Grid Principal (2 colunas)
        self.grid_columnconfigure(0, weight=1) # Coluna da esquerda (Controles)
        self.grid_columnconfigure(1, weight=2) # Coluna da direita (Preview) - maior peso
        self.grid_rowconfigure(0, weight=1)
        
        # --- Coluna da Esquerda: Controles ---
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.left_frame.grid_rowconfigure(4, weight=1) # Empurrar botão voltar para baixo
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Label de status/informação
        self.title_label = ctk.CTkLabel(
            self.left_frame, 
            text="✅ Portfólio Pronto!", 
            font=ctk.CTkFont(size=25, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(40, 10), sticky="n")

        self.info_label = ctk.CTkLabel(
            self.left_frame, 
            text="Seu portfólio em PDF está pronto para ser gerado.",
            font=ctk.CTkFont(size=14),
            wraplength=250
        )
        self.info_label.grid(row=1, column=0, padx=20, pady=(0, 40), sticky="n")
        
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.generated_file_path = os.path.join(self.output_dir, "portfolio_profissional.pdf")
        self.temp_pdf_path = os.path.join(self.output_dir, "temp_preview.pdf")
        self.preview_file_path = os.path.join(self.output_dir, "preview.png") # Caminho do preview
        self.html_file_path = os.path.join(self.output_dir, "output_portfolio.html")

        self.generate_button = ctk.CTkButton(
            self.left_frame, 
            text="Gerar e Salvar PDF", 
            command=self._save_final_pdf,
            height=40,
            width=250,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.generate_button.grid(row=2, column=0, padx=20, pady=(0, 20))
        
        self.open_button = ctk.CTkButton(
            self.left_frame, 
            text="Abrir Portfólio", 
            command=self._open_pdf,
            height=40,
            width=250,
            state="disabled", # Desabilitado até o PDF ser gerado
            fg_color="green" # Cor diferente para destaque
        )
        self.open_button.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="n")

        self.back_button = ctk.CTkButton(
            self.left_frame, 
            text="Voltar ao Início", 
            command=lambda: controller.show_frame("WelcomeFrame"),
            height=40,
            width=250,
            fg_color="gray"
        )
        self.back_button.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="s") # Sticky south

        # --- Coluna da Direita: Preview ---
        self.right_frame = ctk.CTkFrame(self, fg_color="#e0e0e0") # Cor de fundo para destacar o papel
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)
        
        self.preview_label = ctk.CTkLabel(
            self.right_frame, 
            text="O preview aparecerá aqui...",
            text_color="gray"
        )
        self.preview_label.grid(row=0, column=0)
        self.preview_image = None # Referência para manter a imagem na memória
        
        self.chart_gen = GeradorRelatorios()

    def update_data(self):
        """Atualiza a tela quando ela é exibida."""
        self.open_button.configure(state="disabled")
        self.generate_button.configure(text="Gerar e Salvar PDF", state="normal")
        self.info_label.configure(text="Gerando preview automático...", text_color="blue")
        # Limpa o preview anterior
        self.preview_label.configure(image=None, text="Gerando preview...")
        self.preview_image = None
        
        # Auto-gerar PREVIEW ao entrar na tela
        self._generate_preview()

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
        
    def _generate_preview(self):
        """Inicia o processo de geração do PREVIEW (PDF temporário) em background."""
        # Não desabilita o botão de gerar final, pois é apenas um preview
        threading.Thread(target=self._generate_pdf_task, args=(True,)).start()

    def _save_final_pdf(self):
        """Salva o PDF final (pode reutilizar o temp ou gerar de novo)."""
        self.generate_button.configure(text="Salvando...", state="disabled")
        self.info_label.configure(text="Salvando arquivo final...", text_color="blue")
        # Gera novamente para garantir (ou poderia copiar)
        threading.Thread(target=self._generate_pdf_task, args=(False,)).start()

    def _generate_pdf_task(self, is_preview=True):
        """Tarefa de geração do PDF que roda em background.
           is_preview: Se True, salva em temp_pdf_path. Se False, salva em generated_file_path.
        """
        try:
            data = self.controller.portfolio_data
            design = self.controller.design_config
            
            target_path = self.temp_pdf_path if is_preview else self.generated_file_path

            # --- 1. Processar a imagem ---
            processed_img_path = self._process_image_for_template(data.get("photo_path"))
            if processed_img_path:
                data["processed_img_path"] = pathlib.Path(processed_img_path).as_uri()
            else:
                data["processed_img_path"] = None
            
            # --- 1.5. Sanitizar URLs ---
            for key in ["linkedin", "instagram"]:
                if data.get(key) and not data[key].startswith(("http://", "https://")):
                    data[key] = f"https://{data[key]}"

            # --- 2. Gerar Gráficos ---
            # Radar Chart (Equilíbrio)
            cats = ["Frontend", "Backend", "Soft Skills"]
            vals = [
                min(len(data.get("habilidades_frontend_list", [])) * 20, 100),
                min(len(data.get("habilidades_backend_list", [])) * 20, 100),
                min(len(data.get("habilidades_soft_list", [])) * 20, 100)
            ]
            # Evita gráfico vazio se não tiver skills
            if sum(vals) == 0: vals = [20, 20, 20] 
            
            radar_path = self.chart_gen.generate_radar_chart(cats, vals, color=design["cor_principal"])
            if radar_path:
                data["radar_chart_path"] = pathlib.Path(radar_path).as_uri()
            else:
                data["radar_chart_path"] = None

            # --- 3. Configurar Jinja2 ---
            env = Environment(loader=FileSystemLoader("templates"))
            template = env.get_template("portfolio_template.html")
            
            # --- 4. Renderizar o template ---
            html_output = template.render(
                dados=data,
                design=design
            )
            
            # Salva o HTML também (opcional, mas bom para debug)
            with open(self.html_file_path, "w", encoding="utf-8") as f:
                f.write(html_output)
            
            # --- 5. Gerar o PDF com Weasyprint ---
            base_url = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
            HTML(string=html_output, base_url=base_url).write_pdf(target_path)
            
            # --- 6. Gerar Preview com PyMuPDF (fitz) ---
            # Sempre geramos o preview para mostrar na tela, mesmo se for o save final
            doc = fitz.open(target_path)
            page = doc.load_page(0) # Primeira página
            pix = page.get_pixmap(dpi=72) # Baixa resolução para preview rápido
            pix.save(self.preview_file_path)
            doc.close()

            # Sucesso
            self.after(0, lambda: self._on_generation_success(is_preview))
            
        except Exception as e:
            print(f"Erro detalhado na geração de PDF: {e}")
            # Erro - Agenda a atualização da UI na thread principal
            self.after(0, lambda: self._on_generation_error(str(e)))

    def _on_generation_success(self, is_preview):
        """Chamado quando a geração do PDF termina com sucesso."""
        
        if is_preview:
            self.info_label.configure(text="Clique em 'Gerar e Salvar' para finalizar.", text_color="white")
            self.generate_button.configure(text="Gerar e Salvar PDF", state="normal")
        else:
            self.info_label.configure(text=f"Portfólio salvo com sucesso em 'output'!", text_color="green")
            self.open_button.configure(state="normal")
            self.generate_button.configure(text="PDF Salvo!", state="normal") # Mantém habilitado para gerar de novo se quiser
        
        # Exibe o preview
        try:
            if os.path.exists(self.preview_file_path):
                # Carrega a imagem com PIL e força o carregamento para memória
                pil_image = Image.open(self.preview_file_path)
                pil_image.load() # Garante que o arquivo foi lido
                
                # Calcula o tamanho para caber no frame da direita mantendo a proporção
                max_width = 400
                max_height = 550
                
                # Cria uma cópia para redimensionar (boa prática)
                img_copy = pil_image.copy()
                img_copy.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Cria o objeto CTkImage
                self.preview_image = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
                
                # Atualiza o label
                self.preview_label.configure(image=self.preview_image, text="")
            else:
                self.preview_label.configure(text="Erro ao carregar preview.", image=None)
                
        except Exception as e:
            print(f"Erro ao exibir preview: {e}")
            # Garante que remove a imagem se houver erro
            self.preview_label.configure(text=f"Erro visual: {e}", image=None)

    def _on_generation_error(self, error_message):
        """Chamado quando ocorre um erro na geração do PDF."""
        self.info_label.configure(text=f"Erro ao gerar PDF: {error_message}", text_color="red")
        self.generate_button.configure(text="Tentar Novamente", state="normal")
        self.preview_label.configure(text="Falha na geração.")

    def _open_pdf(self):
        """Abre o arquivo PDF gerado."""
        if os.path.exists(self.generated_file_path):
            webbrowser.open(os.path.abspath(self.generated_file_path))
        else:
            self.info_label.configure(text="O arquivo PDF não foi encontrado.", text_color="red")