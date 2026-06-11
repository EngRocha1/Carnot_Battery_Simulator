import plotly.graph_objects as go
import numpy as np

def add_painel_controle(fig, x_pos, y_pos):
    """
    Cria o Armário de Controle Master (Bege Cemar).
    x_pos, y_pos: Coordenadas de ancoragem no Skid.
    """
    # Dimensões do Armário Industrial
    dx_arm, dy_arm, dz_arm = 0.6, 1.2, 2.0
    cor_bege = '#E1D9C1' # Bege Industrial Cemar (Padrão)

    # --- 1. CORPO DO ARMÁRIO (SÓLIDO FECHADO) ---
    fig.add_trace(go.Mesh3d(
        x=[x_pos, x_pos+dx_arm, x_pos+dx_arm, x_pos, x_pos, x_pos+dx_arm, x_pos+dx_arm, x_pos],
        y=[y_pos-dy_arm/2, y_pos-dy_arm/2, y_pos+dy_arm/2, y_pos+dy_arm/2,
           y_pos-dy_arm/2, y_pos-dy_arm/2, y_pos+dy_arm/2, y_pos+dy_arm/2],
        z=[dz_arm, dz_arm, dz_arm, dz_arm, 0, 0, 0, 0],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        color=cor_bege, opacity=1.0, flatshading=True, name="Painel Cemar - Controle sCO2",
        lighting=dict(ambient=0.6, diffuse=0.8, roughness=0.5)
    ))

    # --- 2. INTERFACE FRONTAL (IHM E ACIONAMENTOS) ---
    face_x = x_pos + dx_arm + 0.01

    # Tela IHM (Monitoramento de Barramento)
    fig.add_trace(go.Mesh3d(
        x=[face_x, face_x, face_x, face_x],
        y=[y_pos-0.35, y_pos+0.35, y_pos+0.35, y_pos-0.35],
        z=[dz_arm-0.3, dz_arm-0.3, dz_arm-0.8, dz_arm-0.8],
        color='#1a1a1a', opacity=1.0, name="IHM Display"
    ))

    # Botoeiras (LIGA/VERDE, DESLIGA/VERMELHO, FALHA/AMARELO, TESTE/AMARELO)
    b_y = [y_pos-0.2, y_pos-0.2, y_pos+0.2, y_pos+0.2]
    b_z = [dz_arm-1.2, dz_arm-1.4, dz_arm-1.2, dz_arm-1.4]
    b_cols = ['#27ae60', '#c0392b', '#f1c40f', '#f1c40f']
    b_labels = ["LIGA", "DESLIGA", "FALHA CHAMA", "TESTE SENSOR"]

    fig.add_trace(go.Scatter3d(
        x=[face_x]*4, y=b_y, z=b_z,
        mode='markers+text',
        marker=dict(size=9, color=b_cols, line=dict(color='black', width=1)),
        text=b_labels, textposition="middle right",
        textfont=dict(size=9, color="black", family="Arial Black"),
        name="Comandos Painel"
    ))

    # Botão de Emergência (Mushroom)
    fig.add_trace(go.Scatter3d(
        x=[face_x], y=[y_pos], z=[dz_arm-0.15],
        mode='markers', marker=dict(size=18, color='#e74c3c', symbol='diamond'),
        name="EMERGÊNCIA"
    ))