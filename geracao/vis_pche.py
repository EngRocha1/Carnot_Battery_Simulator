import plotly.graph_objects as go
import numpy as np

def add_pche(fig, raio, altura, esp_p):
    """
    Representação CAD-Like do PCHE fatiado.
    Mostra a carcaça externa em Inox e o núcleo de microcanais interno.
    """
    r_ext = raio + esp_p
    dx, dy, dz = 1.4, 1.8, 2.0  # Dimensões industriais
    z_topo = altura * 0.9       # Ponto de extração térmica superior

    # --- 1. GEOMETRIA DA CARCAÇA FATIADA (ESTILO CAD) ---
    # Criamos um bloco com um "entalhe" que revela o interior
    # Vértices para um paralelepípedo com corte frontal
    x_shell = [
        r_ext, r_ext+dx, r_ext+dx, r_ext,         # Base (z_min)
        r_ext, r_ext+dx, r_ext+dx, r_ext,         # Topo (z_max)
        r_ext, r_ext+dx/2, r_ext+dx/2, r_ext      # Corte intermediário
    ]
    y_shell = [
        -dy/2, -dy/2, dy/2, dy/2,
        -dy/2, -dy/2, dy/2, dy/2,
        0, 0, dy/2, dy/2
    ]
    z_shell = [
        z_topo-dz/2, z_topo-dz/2, z_topo-dz/2, z_topo-dz/2,
        z_topo+dz/2, z_topo+dz/2, z_topo+dz/2, z_topo+dz/2,
        z_topo, z_topo, z_topo, z_topo
    ]

    # Malha externa (Inox Escovado)
    fig.add_trace(go.Mesh3d(
        x=x_shell, y=y_shell, z=z_shell,
        color='#dfe6e9',
        opacity=1.0,
        flatshading=True,
        name="PCHE (Carcaça SS-316H)",
        lighting=dict(specular=1.5, roughness=0.1, ambient=0.5)
    ))

    # --- 2. ESTRUTURA INTERNA DE MICROCANAIS (O "FATIADO") ---
    # Adicionamos camadas densas para simular as placas da imagem de referência
    n_placas = 15
    for i in range(n_placas):
        z_layer = (z_topo - dz/2) + (i * (dz/n_placas))
        # Linhas que representam o relevo das placas gravadas quimicamente
        fig.add_trace(go.Scatter3d(
            x=[r_ext, r_ext + dx/2],
            y=[0, 0],
            z=[z_layer, z_layer],
            mode='lines',
            line=dict(color='#2d3436', width=2),
            showlegend=False,
            hoverinfo='skip'
        ))

    # --- 3. CONECTORES DE FLUIDO (FLANGES) ---
    # Representação simplificada das entradas e saídas de sCO2
    fig.add_trace(go.Scatter3d(
        x=[r_ext + dx/2, r_ext + dx/2],
        y=[dy/2, -dy/2],
        z=[z_topo, z_topo],
        mode='markers',
        marker=dict(size=6, symbol='square', color='#636e72'),
        name="Conexões de Processo"
    ))

    # --- 4. IDENTIFICAÇÃO TÉCNICA ---
    fig.add_trace(go.Scatter3d(
        x=[r_ext + dx], y=[0], z=[z_topo + dz*0.6],
        mode='text',
        text=["PCHE: Diffusion Bonded"],
        textfont=dict(color="#ffd700", size=10, family="Arial Black"),
        showlegend=False
    ))