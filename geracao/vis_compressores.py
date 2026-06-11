import plotly.graph_objects as go
import numpy as np

def add_compressores(fig, raio, altura, esp_p):
    r_ext = raio + esp_p
    x_base = r_ext + 8.5
    h_viga = 0.35
    z_chao = h_viga + 0.2 # No topo do pedestal

    def criar_compressor_fechado(x_c, y_c, z_c, r_vol, l_mot, cor):
        # 1. VOLUTA (CORPO DO DISCO)
        theta = np.linspace(0, 2*np.pi, 40)
        z_v = np.linspace(z_c - 0.25, z_c + 0.25, 10)
        theta, z = np.meshgrid(theta, z_v)
        x = x_c + r_vol * np.cos(theta)
        y = y_c + r_vol * np.sin(theta)
        fig.add_trace(go.Surface(x=x, y=y, z=z, showscale=False, colorscale=[[0, cor], [1, '#1a5276']], showlegend=False))

        # TAMPAS DA VOLUTA (Discos em Z)
        r_d, th_d = np.meshgrid(np.linspace(0, r_vol, 10), np.linspace(0, 2*np.pi, 30))
        for z_edge in [z_c - 0.25, z_c + 0.25]:
            fig.add_trace(go.Surface(
                x=x_c + r_d * np.cos(th_d), y=y_c + r_d * np.sin(th_d), z=np.full(r_d.shape, z_edge),
                showscale=False, colorscale=[[0, cor], [1, cor]], showlegend=False
            ))

        # 2. MOTOR (CORPO CILÍNDRICO ATRÁS)
        m_theta = np.linspace(0, 2*np.pi, 30)
        m_x = np.linspace(x_c + 0.25, x_c + l_mot, 10)
        m_theta, m_x = np.meshgrid(m_theta, m_x)
        r_m = r_vol * 0.7
        m_y, m_z = y_c + r_m * np.cos(m_theta), z_c + r_m * np.sin(m_theta)
        fig.add_trace(go.Surface(x=m_x, y=m_y, z=m_z, showscale=False, colorscale=[[0, '#34495e'], [1, '#2c3e50']], showlegend=False))

        # TAMPA DO MOTOR (Disco em X na extremidade final)
        r_mt, th_mt = np.meshgrid(np.linspace(0, r_m, 10), np.linspace(0, 2*np.pi, 30))
        fig.add_trace(go.Surface(
            x=np.full(r_mt.shape, x_c + l_mot), y=y_c + r_mt * np.cos(th_mt), z=z_c + r_mt * np.sin(th_mt),
            showscale=False, colorscale=[[0, '#2c3e50'], [1, '#2c3e50']], showlegend=False
        ))

    # Plotando MC e RC
    criar_compressor_fechado(x_base, 2.5, z_chao + 0.6, 0.6, 1.5, '#2ecc71')
    criar_compressor_fechado(x_base, -2.5, z_chao + 0.6, 0.6, 1.5, '#27ae60')