import matplotlib
matplotlib.use('Agg') # Define o backend não-interativo para evitar erros de thread
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os
import hashlib

class GeradorRelatorios:
    """
    Classe responsável por gerar gráficos para o portfólio.
    """
    def __init__(self, output_dir="uploads"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_radar_chart(self, categories, values, filename="radar_chart.png", color="#3498db"):
        """
        Gera um gráfico de radar (teia) para as categorias e valores fornecidos.
        Values deve ser uma lista de números (0-10 ou 0-100).
        """
        try:
            # Número de variáveis
            N = len(categories)
            if N < 3: return None # Precisa de pelo menos 3 para um radar

            # O que faremos é repetir o primeiro valor no final para fechar o círculo
            values += values[:1]
            
            # Calcula os ângulos para cada eixo
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]

            # Inicializa o plot polar com fundo branco
            fig = plt.figure(figsize=(6, 6), facecolor='white')
            ax = fig.add_subplot(111, polar=True, facecolor='white')
            
            # Desenha uma linha por fora e preenche
            ax.plot(angles, values, color=color, linewidth=5, linestyle='solid', marker='o', markersize=8)
            ax.fill(angles, values, color=color, alpha=0.3)
            
            # Ajusta os labels das categorias - PRETO SÓLIDO
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, color='#000000', size=16, weight='bold', fontfamily='sans-serif')
            
            # Ajusta o eixo Y - NÚMEROS PRETOS SÓLIDOS
            ax.set_rlabel_position(0)  # type: ignore
            ax.set_yticks([25, 50, 75, 100])
            ax.set_yticklabels(["25", "50", "75", "100"], color="#000000", size=13, weight='bold', fontfamily='sans-serif')
            ax.set_ylim(0, 100)
            
            # Grade mais visível
            ax.grid(linewidth=2, color='#000000', alpha=0.2, linestyle='-')
            
            # Remove o círculo externo
            ax.spines['polar'].set_visible(False)

            # Salva com fundo branco sólido
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, facecolor='white', edgecolor='none', bbox_inches='tight', dpi=200)
            plt.close()
            
            return os.path.abspath(filepath)
        except Exception as e:
            print(f"Erro ao gerar gráfico de radar: {e}")
            return None

    def generate_bar_chart(self, categories, values, filename="bar_chart.png", color="#3498db"):
        """
        Gera um gráfico de barras horizontais.
        """
        try:
            fig, ax = plt.subplots(figsize=(8, 4))
            
            # Cria as barras
            y_pos = np.arange(len(categories))
            ax.barh(y_pos, values, align='center', color=color, alpha=0.8)
            
            # Labels e Títulos
            ax.set_yticks(y_pos)
            ax.set_yticklabels(categories)
            ax.invert_yaxis()  # Labels de cima para baixo
            ax.set_xlabel('Proficiência (%)')
            ax.set_xlim(0, 100)
            
            # Remove bordas desnecessárias para um look mais clean
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_color('#CCCCCC')
            
            # Adiciona grid vertical suave
            ax.xaxis.grid(True, linestyle='--', alpha=0.5)
            ax.set_axisbelow(True)

            # Salva
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, transparent=True, bbox_inches='tight', dpi=100)
            plt.close()
            
            return os.path.abspath(filepath)
        except Exception as e:
            print(f"Erro ao gerar gráfico de barras: {e}")
            return None
    
    def generate_mini_bar_chart(self, categories, values, filename="mini_bar.png", color="#3498db"):
        """
        Gera um gráfico de donut moderno para cards.
        """
        try:
            if not categories or not values:
                return None
            
            # Paleta de cores moderna baseada na cor principal
            import matplotlib.colors as mcolors
            base_color = mcolors.to_rgb(color)
            colors = [
                color,
                mcolors.to_hex([base_color[0]*0.7, base_color[1]*0.7, base_color[2]*0.7]),
                mcolors.to_hex([base_color[0]*0.5, base_color[1]*0.5, base_color[2]*0.5])
            ]
            colors = colors[:len(values)]
            
            # Cria figura com fundo branco
            fig, ax = plt.subplots(figsize=(3, 2), facecolor='white')
            ax.set_facecolor('white')
            
            # Cria o donut chart
            wedges, texts, autotexts = ax.pie(
                values, 
                labels=categories,
                colors=colors,
                autopct='%1.0f',
                startangle=90,
                pctdistance=0.85,
                wedgeprops=dict(width=0.4, edgecolor='white', linewidth=3),
                textprops=dict(color='#2c3e50', weight='bold', fontsize=9)
            )
            
            # Estiliza os textos de porcentagem
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(10)
                autotext.set_weight('bold')
            
            # Adiciona círculo central para efeito donut
            centre_circle = plt.Circle((0, 0), 0.60, fc='white', linewidth=0)
            ax.add_artist(centre_circle)
            
            # Adiciona texto central
            total = sum(values)
            ax.text(0, 0, f'{total}\nSkills', ha='center', va='center',
                   fontsize=11, weight='bold', color='#2c3e50')
            
            ax.axis('equal')
            plt.tight_layout()
            
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, facecolor='white', bbox_inches='tight', dpi=120)
            plt.close()
            
            return os.path.abspath(filepath)
        except Exception as e:
            print(f"Erro ao gerar mini gráfico: {e}")
            return None
