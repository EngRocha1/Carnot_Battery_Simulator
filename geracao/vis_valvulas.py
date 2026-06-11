import plotly.graph_objects as go
import numpy as np

def add_valvulas(fig, raio, altura, esp_p):
    """
    Cria válvulas de controle industriais realistas com corpo e atuador.
    Posicionadas estrategicamente próximas aos recuperadores e compressores.
    """
    r_ext = raio + esp_p
    x_pos = r_ext + 7.5  # Posicionadas no Skid, entre componentes
    h_viga = 0.35

    def criar_valvula_industrial(x_c, y_c, z_c, cor, nome):
        # --- 1. CORPO DA VÁLVULA (ESFERA/ELIPSOIDE CENTRAL) ---
        nb = 20
        phi = np.linspace(0, 2*np.pi, nb)
        theta = np.linspace(0, np.pi, nb)
        phi, theta = np.meshgrid(phi, theta)

        r_body = 0.25
        x = x_c + r_body * np.sin(theta) * np.cos(phi)
        y = y_c + r_body * np.sin(theta) * np.sin(phi)
        z = z_c + r_body * np.cos(theta)

        fig.add_trace(go.Surface(
            x=x, y=y, z=z, showscale=False,
            colorscale=[[0, cor], [1, '#c0392b']],
            name=f"Corpo {nome}", lighting=dict(specular=1.5)
        ))

        # --- 2. ATUADOR (O "CHAPÉU" DA VÁLVULA) ---
        # Haste (Cilindro Fino)
        z_haste = np.linspace(z_c + r_body, z_c + r_body + 0.3, 5)
        phi_h = np.linspace(0, 2*np.pi, 20)
        phi_h, z_h = np.meshgrid(phi_h, z_haste)
        r_h = 0.05
        fig.add_trace(go.Surface(
            x=x_c + r_h * np.cos(phi_h), y=y_c + r_h * np.sin(phi_h), z=z_h,
            showscale=False, colorscale=[[0, '#bdc3c7'], [1, '#7f8c8d']], showlegend=False
        ))

        # Atuador Superior (Cilindro Largo - Diafragma)
        z_top = np.linspace(z_c + r_body + 0.3, z_c + r_body + 0.6, 5)
        phi_t, z_t = np.meshgrid(phi_h, z_top)
        r_t = 0.25
        fig.add_trace(go.Surface(
            x=x_c + r_t * np.cos(phi_t), y=y_c + r_t * np.sin(phi_t), z=z_t,
            showscale=False, colorscale=[[0, '#34495e'], [1, '#2c3e50']], showlegend=False
        ))

        # Tampa do Atuador
        r_d, ph_d = np.meshgrid(np.linspace(0, r_t, 10), np.linspace(0, 2*np.pi, 20))
        fig.add_trace(go.Surface(
            x=x_c + r_d * np.cos(ph_d), y=y_c + r_d * np.sin(ph_d), z=np.full(r_d.shape, z_c + r_body + 0.6),
            showscale=False, colorscale=[[0, '#2c3e50'], [1, '#2c3e50']], showlegend=False
        ))

    # Válvula de Bypass (Próxima ao HTR - Alta Temperatura)
    criar_valvula_industrial(x_pos, 0.5, altura * 0.45, '#e74c3c', "Válvula Bypass")

    # Válvula de Inventário (Próxima ao MC/Recalque)
    criar_valvula_industrial(x_pos, -0.5, h_viga + 0.6, '#e67e22', "Válvula de Inventário")

    # --- TAGS DE TEXTO ---
    fig.add_trace(go.Scatter3d(
        x=[x_pos, x_pos], y=[0.5, -0.5], z=[altura*0.55, h_viga + 1.3],
        mode='text', text=["Válvula Bypass", "Válvula Inventário"],
        textfont=dict(color="white", size=10, family="Arial Black"),
        showlegend=False
    ))