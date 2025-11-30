import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import shutil
import json

class PortfolioForms(ctk.CTkFrame):
    """
    Tela para coleta de todos os dados do portfólio.
    """
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.photo_path = None # Caminho da foto carregada
        self.json_file = "portfolio_data.json"
        
        # Configura o layout com rolagem, já que o formulário será longo
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="✍️ Preencha seus Dados Profissionais")
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Contador de linha para organizar os elementos no scrollable_frame
        self.row_counter = 0 
        
        # --- Seção de Dados Pessoais e Foto ---
        self._create_section_title("🧑 Dados Pessoais", 16)
        
        self.photo_label = ctk.CTkLabel(self.scrollable_frame, text="Foto de Perfil:")
        self._place_element(self.photo_label)
        
        self.photo_button = ctk.CTkButton(
            self.scrollable_frame, 
            text="Carregar Foto (PNG/JPEG)", 
            command=self._load_photo
        )
        self._place_element(self.photo_button, pady=5)
        
        self.photo_preview = ctk.CTkLabel(self.scrollable_frame, text="Pré-visualização da Foto")
        self._place_element(self.photo_preview, pady=(0, 20))
        
        self.fields = {} # Dicionário para armazenar as variáveis de entrada
        
        self._add_input_field("nome", "Nome Completo:")
        self._add_input_field("titulo", "Título Profissional (Ex: Desenvolvedor Full Stack):")
        self._add_input_field("bio", "Descrição Curta (Bio):", is_textbox=True)
        self._add_input_field("telefone", "Telefone:")
        self._add_input_field("email", "Email:")
        self._add_input_field("local", "Localização (Ex: Maceió-AL):")
        self._add_input_field("linkedin", "URL do LinkedIn:")
        self._add_input_field("instagram", "URL do Instagram (Opcional):")

        # --- Seção de Formação Acadêmica ---
        self._create_section_title("🎓 Formação Acadêmica", 20)
        self.formacoes = []  # lista de dicts com refs dos campos
        self.formacoes_container = ctk.CTkFrame(self.scrollable_frame)
        self._place_element(self.formacoes_container)
        self.formacoes_container.grid_columnconfigure(0, weight=1)
        # Botões de ação da seção
        formacao_actions = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        formacao_actions.grid(row=self.row_counter, column=0, sticky="ew", padx=10, pady=10)
        self.row_counter += 1
        self.add_formacao_btn = ctk.CTkButton(
            formacao_actions,
            text="+ Adicionar Formação",
            command=self._add_formacao_block,
            fg_color="#2ecc71"
        )
        self.add_formacao_btn.grid(row=0, column=0, sticky="w")
        # adiciona um bloco inicial vazio
        self._add_formacao_block()
        
        # --- Seção de Experiência Profissional ---
        self._create_section_title("💼 Experiência Profissional", 25)
        self.experiencias = []
        self.experiencias_container = ctk.CTkFrame(self.scrollable_frame)
        self._place_element(self.experiencias_container)
        self.experiencias_container.grid_columnconfigure(0, weight=1)
        exp_actions = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        exp_actions.grid(row=self.row_counter, column=0, sticky="ew", padx=10, pady=10)
        self.row_counter += 1
        self.add_exp_btn = ctk.CTkButton(
            exp_actions,
            text="+ Adicionar Experiência",
            command=self._add_experiencia_block,
            fg_color="#3498db"
        )
        self.add_exp_btn.grid(row=0, column=0, sticky="w")
        self._add_experiencia_block()
        
        # --- Seção de Habilidades (Skills) ---
        self._create_section_title("💻 Habilidades", 30)
        # Uma única caixa para listar as habilidades separadas por vírgula
        self._add_input_field("habilidades_frontend", "Habilidades Frontend (Ex: HTML5, CSS3, React):", is_textbox=True)
        self._add_input_field("habilidades_backend", "Habilidades Backend (Ex: Node.js, Express, PostgreSQL):", is_textbox=True)
        self._add_input_field("habilidades_soft", "Soft Skills (Ex: Liderança, Comunicação):", is_textbox=True)


        self.back_button = ctk.CTkButton(
            self.scrollable_frame,
            text="Voltar ao Início", 
            command=lambda: controller.show_frame("WelcomeFrame"),
            height=40,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="gray"
        )
        self.back_button.grid(row=0, column=0, padx=10, sticky="e")

        # --- Botão de Navegação ---
        self._create_section_title("", 35) # Espaçamento
        self.next_button = ctk.CTkButton(
            self.scrollable_frame, 
            text="Próxima Etapa: Personalizar", 
            command=self._save_and_next,
            height=40,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self._place_element(self.next_button, pady=20)
        
        # Carregar dados salvos se existirem
        self._load_data()


    def _create_section_title(self, text, row_skip=0):
        """Cria um título de seção no formulário."""
        if row_skip > 0:
            self.row_counter += row_skip # Espaçamento
            
        title = ctk.CTkLabel(
            self.scrollable_frame, 
            text=text, 
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        self._place_element(title, pady=(20, 10))

    def _place_element(self, element, pady=(5, 5)):
        """Coloca um elemento no grid e incrementa o contador de linha."""
        element.grid(row=self.row_counter, column=0, padx=10, pady=pady, sticky="ew")
        self.row_counter += 1

    def _add_input_field(self, key, label_text, is_textbox=False):
        """Adiciona um rótulo e um campo de entrada (ou caixa de texto) ao formulário."""
        label = ctk.CTkLabel(self.scrollable_frame, text=label_text, anchor="w")
        self._place_element(label, pady=(10, 0))
        
        if is_textbox:
            field = ctk.CTkTextbox(self.scrollable_frame, height=80, width=400)
            self.fields[key] = field 
        else:
            field_var = ctk.StringVar()
            field = ctk.CTkEntry(self.scrollable_frame, textvariable=field_var, width=400)
            self.fields[key] = field_var
            
        self._place_element(field, pady=(0, 10))
    
    def _add_formacao_block(self):
        """Cria um bloco de campos de formação com opção de remoção."""
        idx = len(self.formacoes)
        block = ctk.CTkFrame(self.formacoes_container, corner_radius=8)
        block.grid(row=idx, column=0, sticky="ew", padx=5, pady=6)
        block.grid_columnconfigure(0, weight=1)

        # Campos
        curso_var = ctk.StringVar()
        inst_var = ctk.StringVar()
        periodo_var = ctk.StringVar()
        descricao_tb = ctk.CTkTextbox(block, height=60)

        ctk.CTkLabel(block, text=f"Curso/Grau #{idx+1}:").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
        ctk.CTkEntry(block, textvariable=curso_var).grid(row=1, column=0, sticky="ew", padx=8)
        ctk.CTkLabel(block, text="Instituição:").grid(row=2, column=0, sticky="w", padx=8, pady=(8, 2))
        ctk.CTkEntry(block, textvariable=inst_var).grid(row=3, column=0, sticky="ew", padx=8)
        ctk.CTkLabel(block, text="Período:").grid(row=4, column=0, sticky="w", padx=8, pady=(8, 2))
        ctk.CTkEntry(block, textvariable=periodo_var).grid(row=5, column=0, sticky="ew", padx=8)
        ctk.CTkLabel(block, text="Descrição:").grid(row=6, column=0, sticky="w", padx=8, pady=(8, 2))
        descricao_tb.grid(row=7, column=0, sticky="ew", padx=8, pady=(0, 8))

        # Remover
        remove_btn = ctk.CTkButton(block, text="Remover", fg_color="#e74c3c",
                                   command=lambda b=block: self._remove_formacao_block(b))
        remove_btn.grid(row=0, column=1, padx=8, pady=8)

        # Registrar refs
        self.formacoes.append({
            'block': block,
            'curso': curso_var,
            'instituicao': inst_var,
            'periodo': periodo_var,
            'descricao': descricao_tb
        })
    
    def _add_experiencia_block(self):
        """Cria um bloco de experiência com opção de remoção."""
        idx = len(self.experiencias)
        block = ctk.CTkFrame(self.experiencias_container, corner_radius=8)
        block.grid(row=idx, column=0, sticky="ew", padx=5, pady=6)
        block.grid_columnconfigure(0, weight=1)

        cargo_var = ctk.StringVar()
        empresa_var = ctk.StringVar()
        periodo_var = ctk.StringVar()
        resumo_tb = ctk.CTkTextbox(block, height=60)

        ctk.CTkLabel(block, text=f"Cargo #{idx+1}:").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
        ctk.CTkEntry(block, textvariable=cargo_var).grid(row=1, column=0, sticky="ew", padx=8)
        ctk.CTkLabel(block, text="Empresa/Local:").grid(row=2, column=0, sticky="w", padx=8, pady=(8, 2))
        ctk.CTkEntry(block, textvariable=empresa_var).grid(row=3, column=0, sticky="ew", padx=8)
        ctk.CTkLabel(block, text="Período:").grid(row=4, column=0, sticky="w", padx=8, pady=(8, 2))
        ctk.CTkEntry(block, textvariable=periodo_var).grid(row=5, column=0, sticky="ew", padx=8)
        ctk.CTkLabel(block, text="Resumo:").grid(row=6, column=0, sticky="w", padx=8, pady=(8, 2))
        resumo_tb.grid(row=7, column=0, sticky="ew", padx=8, pady=(0, 8))

        remove_btn = ctk.CTkButton(block, text="Remover", fg_color="#e74c3c",
                                   command=lambda b=block: self._remove_experiencia_block(b))
        remove_btn.grid(row=0, column=1, padx=8, pady=8)

        self.experiencias.append({
            'block': block,
            'cargo': cargo_var,
            'empresa': empresa_var,
            'periodo': periodo_var,
            'resumo': resumo_tb
        })
    
    def _remove_formacao_block(self, block):
        """Remove bloco de formação e reindexa grid."""
        for i, f in enumerate(self.formacoes):
            if f['block'] == block:
                f['block'].destroy()
                self.formacoes.pop(i)
                break
        # Reorganiza posições
        for idx, f in enumerate(self.formacoes):
            f['block'].grid_configure(row=idx)
    
    def _remove_experiencia_block(self, block):
        for i, e in enumerate(self.experiencias):
            if e['block'] == block:
                e['block'].destroy()
                self.experiencias.pop(i)
                break
        for idx, e in enumerate(self.experiencias):
            e['block'].grid_configure(row=idx)
        
    
    def _load_photo(self, path=None):
        """Abre a caixa de diálogo para selecionar uma imagem e a pré-visualiza. Se path for fornecido, carrega direto."""
        if path:
            file_path = path
        else:
            # Limita os tipos de arquivo
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg")]
            )
            
        if file_path and os.path.exists(file_path):
            # --- Salvar cópia localmente ---
            try:
                # Se não for carregamento automático (path=None), copia para uploads
                if not path:
                    upload_dir = "uploads"
                    if not os.path.exists(upload_dir):
                        os.makedirs(upload_dir)
                    
                    filename = os.path.basename(file_path)
                    destination_path = os.path.join(upload_dir, filename)
                    shutil.copy2(file_path, destination_path)
                    self.photo_path = os.path.abspath(destination_path)
                else:
                    self.photo_path = file_path # Já é o caminho salvo

                # --- Tratamento de Imagem com Pillow ---
                img = Image.open(self.photo_path)
                
                # Criar CTkImage (mantém alta qualidade em HighDPI)
                # Definimos o tamanho de exibição para 100x100, mas passamos a imagem original
                ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
                
                self.photo_preview.configure(
                    image=ctk_image, 
                    text="", 
                    compound="top"
                )
                # self.photo_preview.image = ctk_image # CTkLabel mantém a referência automaticamente
                
            except Exception as e:
                print(f"Erro ao carregar ou processar imagem: {e}")
                if not path: self.photo_path = None
                
    def _get_input_data(self):
        """Coleta todos os dados de todos os campos do formulário."""
        data = {}
        for key, field in self.fields.items():
            if isinstance(field, ctk.CTkTextbox):
                # Para Textbox, usamos .get("1.0", "end-1c") para obter todo o conteúdo
                data[key] = field.get("1.0", "end-1c").strip() 
            elif isinstance(field, ctk.StringVar):
                # Para Entry, usamos o valor da StringVar
                data[key] = field.get().strip()
                
        # Adiciona o caminho da foto
        data["photo_path"] = self.photo_path 
        return data

    def _save_data_to_json(self, data):
        """Salva os dados em um arquivo JSON."""
        try:
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erro ao salvar dados em JSON: {e}")

    def _load_data(self):
        """Carrega os dados do arquivo JSON se existir."""
        if not os.path.exists(self.json_file):
            return

        try:
            with open(self.json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Reset containers
            for f in list(self.formacoes):
                f['block'].destroy()
            self.formacoes.clear()
            for e in list(self.experiencias):
                e['block'].destroy()
            self.experiencias.clear()

            # Recria blocos conforme dados
            for item in data.get("formacoes_list", []) or []:
                self._add_formacao_block()
                f = self.formacoes[-1]
                f['curso'].set(item.get('curso', ''))
                f['instituicao'].set(item.get('instituicao', ''))
                f['periodo'].set(item.get('periodo', ''))
                f['descricao'].delete("1.0", "end")
                f['descricao'].insert("1.0", item.get('descricao', ''))

            if not self.formacoes:
                self._add_formacao_block()

            for item in data.get("experiencias_list", []) or []:
                self._add_experiencia_block()
                e = self.experiencias[-1]
                e['cargo'].set(item.get('cargo', ''))
                e['empresa'].set(item.get('empresa', ''))
                e['periodo'].set(item.get('periodo', ''))
                e['resumo'].delete("1.0", "end")
                e['resumo'].insert("1.0", item.get('resumo', ''))

            if not self.experiencias:
                self._add_experiencia_block()
            
            # Preenche os campos
            for key, value in data.items():
                if key in self.fields:
                    field = self.fields[key]
                    if isinstance(field, ctk.CTkTextbox):
                        field.delete("1.0", "end")
                        field.insert("1.0", value)
                    elif isinstance(field, ctk.StringVar):
                        field.set(value)
            
            # Carrega a foto
            if "photo_path" in data and data["photo_path"]:
                self._load_photo(path=data["photo_path"])
                
        except Exception as e:
            print(f"Erro ao carregar dados do JSON: {e}")

    def _save_and_next(self):
        """Salva os dados coletados no controlador e avança para a próxima tela."""
        collected_data = self._get_input_data()

        # Coleta formações dos blocos (apenas não vazias)
        collected_data['formacoes_list'] = []
        for f in self.formacoes:
            formacao = {
                'curso': f['curso'].get().strip(),
                'instituicao': f['instituicao'].get().strip(),
                'periodo': f['periodo'].get().strip(),
                'descricao': f['descricao'].get("1.0", "end-1c").strip()
            }
            if any(formacao.values()):
                collected_data['formacoes_list'].append(formacao)

        # Coleta experiências dos blocos (apenas não vazias)
        collected_data['experiencias_list'] = []
        for e in self.experiencias:
            experiencia = {
                'cargo': e['cargo'].get().strip(),
                'empresa': e['empresa'].get().strip(),
                'periodo': e['periodo'].get().strip(),
                'resumo': e['resumo'].get("1.0", "end-1c").strip()
            }
            if any(experiencia.values()):
                collected_data['experiencias_list'].append(experiencia)
        
        # Salva persistência
        self._save_data_to_json(collected_data)
        
        # Otimização para listas de habilidades
        for key in ["habilidades_frontend", "habilidades_backend", "habilidades_soft"]:
            if collected_data.get(key):
                collected_data[f"{key}_list"] = [item.strip() for item in collected_data[key].split(',')]
            else:
                collected_data[f"{key}_list"] = []

        self.controller.set_portfolio_data(collected_data)
        self.controller.show_frame("PersonalizacaoFrame")