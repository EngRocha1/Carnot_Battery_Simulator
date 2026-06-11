import plotly.graph_objects as go
import numpy as np

def add_recuperadores(fig, raio, altura, esp_p):
    """
    Desenha os recuperadores HTR e LTR como vasos de pressão cilíndricos.
    Reposicionados para ficarem LADO A LADO no lado negativo do eixo Y,
    evitando a colisão com o Turbogerador.
    """
    r_ext = raio + esp_p
    # Mantemos o X para alinhar com o centro do skid de máquinas
    x_pos = r_ext + 6.5
    h_viga = 0.35        # Referência do topo da viga I do Skid

    def criar_vaso_com_suporte(x_c, y_c, z_min, z_max, r, cor, nome):
        # --- 1. O CORPO DO VASO (CILINDRO FECHADO) ---
        z_range = np.linspace(z_min, z_max, 20)
        theta = np.linspace(0, 2*np.pi, 30)
        theta, z = np.meshgrid(theta, z_range)
        x, y = x_c + r * np.cos(theta), y_c + r * np.sin(theta)

        fig.add_trace(go.Surface(
            x=x, y=y, z=z,
            showscale=False, colorscale=[[0, cor], [1, '#1b4f72']],
            name=nome, lighting=dict(specular=1.5, roughness=0.2),
            opacity=1.0
        ))

        # Tampas (Topo e Base do Vaso)
        r_d, th_d = np.meshgrid(np.linspace(0, r, 10), np.linspace(0, 2*np.pi, 30))
        for z_edge in [z_min, z_max]:
            fig.add_trace(go.Surface(
                x=x_c + r_d * np.cos(th_d), y=y_c + r_d * np.sin(th_d), z=np.full(r_d.shape, z_edge),
                showscale=False, colorscale=[[0, cor], [1, cor]], showlegend=False,
                opacity=1.0
            ))

        # --- 2. O SUPORTE (SKIRT) ---
        # Conecta a base do vaso ao Skid
        z_skirt_coords = np.linspace(h_viga, z_min, 10)
        th_skirt = np.linspace(0, 2*np.pi, 30)
        th_skirt, z_skirt = np.meshgrid(th_skirt, z_skirt_coords)

        r_s = r * 0.95
        x_s = x_c + r_s * np.cos(th_skirt)
        y_s = y_c + r_s * np.sin(th_skirt)

        fig.add_trace(go.Surface(
            x=x_s, y=y_s, z=z_skirt,
            showscale=False, colorscale=[[0, '#7f8c8d'], [1, '#95a5a6']],
            name=f"Suporte {nome}", opacity=1.0, lighting=dict(ambient=0.6),
            showlegend=False
        ))

    # --- LTR: Posicionado na borda externa (Lado frio) ---
    y_ltr = -3.2
    z_base_ltr = h_viga + 0.6
    z_topo_ltr = z_base_ltr + (altura * 0.3)
    criar_vaso_com_suporte(x_pos, y_ltr, z_base_ltr, z_topo_ltr, 0.7, '#34495e', "LTR")

    # --- HTR: Posicionado LADO A LADO com o LTR ---
    # Agora em Y = -1.5, liberando o corredor Y = 2.0 para o Turbogerador
    y_htr = -1.5
    z_base_htr = h_viga + 0.6
    z_topo_htr = z_base_htr + (altura * 0.35)
    criar_vaso_com_suporte(x_pos, y_htr, z_base_htr, z_topo_htr, 0.7, '#2980b9', "HTR")

    return fig