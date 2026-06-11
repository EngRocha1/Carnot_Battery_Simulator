import plotly.graph_objects as go
import numpy as np

def add_turbine(fig, raio, altura, esp_p):
    """
    Cria o conjunto Turbogerador completo e fechado:
    1. Turbina sCO2
    2. Eixo e Mancal
    3. Gerador Elétrico com Caixa de Bornes
    """
    r_ext = raio + esp_p
    x_pos = r_ext + 4.0
    y_pos = 2.0
    h_viga = 0.35
    z_base = h_viga + 0.2

    r_turb = 0.5
    l_turb = 0.8
    z_centro = z_base + r_turb + 0.1

    def criar_cilindro_fechado(x_c, y_c, z_c, r, l, cor, nome):
        # 1. CASCA
        phi = np.linspace(0, 2*np.pi, 30)
        x_range = np.linspace(x_c - l/2, x_c + l/2, 10)
        phi, x = np.meshgrid(phi, x_range)
        y, z = y_c + r * np.cos(phi), z_c + r * np.sin(phi)

        fig.add_trace(go.Surface(
            x=x, y=y, z=z, showscale=False,
            colorscale=[[0, cor], [1, '#7f8c8d']],
            name=nome, lighting=dict(specular=1.5), opacity=1.0
        ))

        # 2. TAMPAS (CIRCUNFERÊNCIAS)
        r_d, ph_d = np.meshgrid(np.linspace(0, r, 10), np.linspace(0, 2*np.pi, 30))
        for x_edge in [x_c - l/2, x_c + l/2]:
            fig.add_trace(go.Surface(
                x=np.full(r_d.shape, x_edge),
                y=y_c + r_d * np.cos(ph_d),
                z=z_c + r_d * np.sin(ph_d),
                showscale=False, colorscale=[[0, cor], [1, cor]], showlegend=False
            ))

    # --- 1. TURBINA ---
    criar_cilindro_fechado(x_pos, y_pos, z_centro, r_turb, l_turb, '#95a5a6', "Turbina sCO2")

    # --- 2. EIXO E MANCAL ---
    r_eixo, l_eixo = 0.12, 0.6
    x_eixo = x_pos + l_turb/2 + l_eixo/2
    criar_cilindro_fechado(x_eixo, y_pos, z_centro, r_eixo, l_eixo, '#2c3e50', "Eixo")

    # Bloco do Mancal
    fig.add_trace(go.Mesh3d(
        x=[x_eixo-0.15, x_eixo+0.15, x_eixo+0.15, x_eixo-0.15, x_eixo-0.15, x_eixo+0.15, x_eixo+0.15, x_eixo-0.15],
        y=[y_pos-0.2, y_pos-0.2, y_pos+0.2, y_pos+0.2, y_pos-0.2, y_pos-0.2, y_pos+0.2, y_pos+0.2],
        z=[z_centro, z_centro, z_centro, z_centro, h_viga, h_viga, h_viga, h_viga],
        color='#7f8c8d', opacity=1.0, flatshading=True, name="Mancal"
    ))

    # --- 3. GERADOR ELÉTRICO ---
    r_gen, l_gen = 0.65, 1.4
    x_gen = x_eixo + l_eixo/2 + l_gen/2
    criar_cilindro_fechado(x_gen, y_pos, z_centro, r_gen, l_gen, '#2980b9', "Gerador")

    # Caixa de Bornes (CORRIGIDO: r_centro alterado para r_gen)
    fig.add_trace(go.Mesh3d(
        x=[x_gen-0.3, x_gen+0.3, x_gen+0.3, x_gen-0.3, x_gen-0.3, x_gen+0.3, x_gen+0.3, x_gen-0.3],
        y=[y_pos-0.3, y_pos-0.3, y_pos+0.3, y_pos+0.3, y_pos-0.3, y_pos-0.3, y_pos+0.3, y_pos+0.3],
        z=[z_centro+r_gen+0.2, z_centro+r_gen+0.2, z_centro+r_gen+0.2, z_centro+r_gen+0.2,
           z_centro+r_gen, z_centro+r_gen, z_centro+r_gen, z_centro+r_gen],
        color='#34495e', opacity=1.0, flatshading=True, name="Caixa de Bornes"
    ))

    # --- 4. PEDESTAL DO GERADOR ---
    fig.add_trace(go.Mesh3d(
        x=[x_gen-0.6, x_gen+0.6, x_gen+0.6, x_gen-0.6, x_gen-0.6, x_gen+0.6, x_gen+0.6, x_gen-0.6],
        y=[y_pos-0.6, y_pos-0.6, y_pos+0.6, y_pos+0.6, y_pos-0.6, y_pos-0.6, y_pos+0.6, y_pos+0.6],
        z=[z_centro-r_gen+0.2, z_centro-r_gen+0.2, z_centro-r_gen+0.2, z_centro-r_gen+0.2, h_viga, h_viga, h_viga, h_viga],
        color='#bdc3c7', opacity=1.0, flatshading=True, showlegend=False
    ))

    return fig