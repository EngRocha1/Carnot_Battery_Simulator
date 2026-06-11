import matplotlib.pyplot as plt
import numpy as np

def plotar_perfis_corte(T_vetor, altura=10.0):
    """
    SESSÃO 3: ANÁLISE DE GRADIENTE VERTICAL
    Exibe a distribuição de temperatura ao longo da profundidade (z) do núcleo.
    """
    z = np.linspace(0, altura, len(T_vetor))
    fig, ax = plt.subplots(figsize=(5, 8)) # Formato vertical para simular o tanque
    
    # Plotagem do Perfil Térmico (MEF)
    ax.plot(T_vetor, z, color='#d63031', linewidth=3, label='Gradiente Térmico')
    
    # Preenchimento estético (Incandescência lateral)
    ax.fill_betweenx(z, T_vetor, T_vetor.min(), color='#fab1a0', alpha=0.3)
    
    # Inverter o eixo Y para o topo (0m) ficar em cima
    ax.invert_yaxis()
    
    # Detalhes Acadêmicos
    ax.set_title('Perfil Térmico de Profundidade', fontsize=12, fontweight='bold')
    ax.set_xlabel('Temperatura (K)', fontsize=10)
    ax.set_ylabel('Profundidade (m)', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Linha indicativa de temperatura média
    t_media = np.mean(T_vetor)
    ax.axvline(t_media, color='black', linestyle=':', label=f'T_méd: {t_media:.1f}K')
    
    ax.legend(loc='lower left', fontsize='small')
    plt.tight_layout()
    
    return fig
