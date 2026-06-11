import matplotlib.pyplot as plt
import numpy as np

def plotar_memorial_blindagem(raio, altura, esp_p, esp_v, T_topo, T_fundo, T_amb, k_p, k_v, h_conv):
    """
    SESSÃO 2: MEMORIAL DE CÁLCULO E SEGURANÇA (NR-12)
    Gera o esquema técnico 2D com fluxos de calor independentes e 
    gradientes de temperatura para a lateral e para o solo.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # 1. Desenho Geométrico das Camadas (Escala Real)
    # Núcleo (Meio Granular)
    ax.add_patch(plt.Rectangle((-raio, 0), 2*raio, altura, color='#ffeaa7', label='Núcleo Térmico (Areia/Grafite)'))
    
    # Camada Lateral (Perlite Expandida)
    ax.add_patch(plt.Rectangle((-raio-esp_p, 0), esp_p, altura, color='#dfe6e9', alpha=0.9, label='Isolamento Perlite (Lateral)'))
    ax.add_patch(plt.Rectangle((raio, 0), esp_p, altura, color='#dfe6e9', alpha=0.9))
    
    # Camada de Base (Vermiculite)
    ax.add_patch(plt.Rectangle((-raio-esp_p, -esp_v), (raio+esp_p)*2, esp_v, color='#b2bec3', label='Base Vermiculite (Solo)'))

    # 2. CÁLCULOS TÉRMICOS DE FRONTEIRA (Independentes)
    # Fluxo Lateral (Condução + Convecção Externa)
    # q = (T_int - T_amb) / (esp/k + 1/h)
    R_p = esp_p / k_p
    R_conv = 1 / h_conv
    q_lat = (T_topo - T_amb) / (R_p + R_conv)
    # Temperatura na interface externa da casca lateral
    t_casca_lat = T_amb + (q_lat * R_conv)
    
    # Fluxo p/ o Solo (Considerando resistência da base)
    R_v = esp_v / k_v
    q_solo = (T_fundo - T_amb) / (R_v + R_conv)
    # Temperatura na interface fundo/solo
    t_casca_solo = T_amb + (q_solo * R_conv)

    # 3. ANOTAÇÕES TÉCNICAS E VETORES DE FLUXO
    # Vetor de Perda Lateral
    ax.annotate(f'FUGA LATERAL\n{q_lat:.2f} W/m²\n{t_casca_lat-273.15:.1f}°C', 
                xy=(raio + esp_p/2, altura/2), xytext=(raio + esp_p + 3, altura/2),
                arrowprops=dict(facecolor='#d63031', shrink=0.05, width=2), 
                fontsize=10, fontweight='bold', color='#c0392b')
    
    # Vetor de Perda p/ Solo
    ax.annotate(f'FUGA P/ SOLO\n{q_solo:.2f} W/m²\n{t_casca_solo-273.15:.1f}°C', 
                xy=(0, -esp_v/2), xytext=(0, -esp_v - 3),
                arrowprops=dict(facecolor='#0984e3', shrink=0.05, width=2), 
                ha='center', fontsize=10, fontweight='bold', color='#2980b9')

    # Cotas de Espessura (Auxilia na conferência visual)
    ax.text(raio + esp_p/4, -0.5, f'{esp_p}m', fontsize=8, ha='center')
    ax.text(-(raio+esp_p+0.5), -esp_v/2, f'{esp_v}m', fontsize=8, va='center', rotation=90)

    # 4. Ajustes de Eixo Acadêmico
    lim_x = raio + esp_p + 5
    lim_y = altura + 3
    ax.set_xlim(-lim_x, lim_x)
    ax.set_ylim(-esp_v - 5, lim_y)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='black')
    
    plt.title("MEMORIAL TÉCNICO DE BARREIRAS E FLUXO TÉRMICO (NR-12)", fontsize=14, fontweight='bold', pad=20)
    
    return fig, q_lat, q_solo, t_casca_lat, t_casca_solo
