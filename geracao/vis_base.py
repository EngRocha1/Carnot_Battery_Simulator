import plotly.graph_objects as go
import numpy as np

def add_vis_base(fig, raio, altura, esp_p):
    """
    Cria a infraestrutura de geração:
    O Painel agora está montado EXATAMENTE sobre a viga 'I' do Skid.
    """
    r_ext = raio + esp_p
    x0 = r_ext + 1.0

    # Dimensões e Parâmetros
    larg_base, prof_base, esp_concreto = 14.0, 10.0, 0.6
    h_viga, w_flange, t_flange, t_alma = 0.35, 0.25, 0.03, 0.03

    # --- 1. FUNDAÇÃO DE CONCRETO (Z < 0) ---
    fig.add_trace(go.Mesh3d(
        x=[x0, x0+larg_base, x0+larg_base, x0, x0, x0+larg_base, x0+larg_base, x0],
        y=[-prof_base/2, -prof_base/2, prof_base/2, prof_base/2, -prof_base/2, -prof_base/2, prof_base/2, prof_base/2],
        z=[0, 0, 0, 0, -esp_concreto, -esp_concreto, -esp_concreto, -esp_concreto],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        color='#95a5a6', opacity=1.0, flatshading=True, name="Base de Concreto", showlegend=False
    ))

    # --- 2. SKID DE AÇO (VIGAS I) ---
    cor_aco = '#2c3e50'
    # Coordenadas Y das vigas: [-4.2, 0, 4.2] considerando prof_base=10
    offsets_y = [-prof_base/2 + 0.8, 0, prof_base/2 - 0.8]

    for oy in offsets_y:
        # Aba Inferior
        fig.add_trace(go.Mesh3d(
            x=[x0, x0+larg_base, x0+larg_base, x0, x0, x0+larg_base, x0+larg_base, x0],
            y=[oy-w_flange/2, oy-w_flange/2, oy+w_flange/2, oy+w_flange/2, oy-w_flange/2, oy-w_flange/2, oy+w_flange/2, oy+w_flange/2],
            z=[t_flange, t_flange, t_flange, t_flange, 0, 0, 0, 0],
            color=cor_aco, opacity=1.0, flatshading=True, showlegend=False
        ))
        # Alma
        fig.add_trace(go.Mesh3d(
            x=[x0, x0+larg_base, x0+larg_base, x0, x0, x0+larg_base, x0+larg_base, x0],
            y=[oy-t_alma/2, oy-t_alma/2, oy+t_alma/2, oy+t_alma/2, oy-t_alma/2, oy-t_alma/2, oy+t_alma/2, oy+t_alma/2],
            z=[h_viga-t_flange, h_viga-t_flange, h_viga-t_flange, h_viga-t_flange, t_flange, t_flange, t_flange, t_flange],
            color=cor_aco, opacity=1.0, flatshading=True, showlegend=False
        ))
        # Aba Superior
        fig.add_trace(go.Mesh3d(
            x=[x0, x0+larg_base, x0+larg_base, x0, x0, x0+larg_base, x0+larg_base, x0],
            y=[oy-w_flange/2, oy-w_flange/2, oy+w_flange/2, oy+w_flange/2, oy-w_flange/2, oy-w_flange/2, oy+w_flange/2, oy+w_flange/2],
            z=[h_viga, h_viga, h_viga, h_viga, h_viga-t_flange, h_viga-t_flange, h_viga-t_flange, h_viga-t_flange],
            color=cor_aco, opacity=1.0, flatshading=True, showlegend=False
        ))

    # --- 3. PEDESTAIS ---
    locais = [(x0 + 4.0, 2.0), (x0 + 8.0, 1.5), (x0 + 8.0, -1.5)]
    for px, py in locais:
        fig.add_trace(go.Mesh3d(
            x=[px-0.6, px+0.6, px+0.6, px-0.6, px-0.6, px+0.6, px+0.6, px-0.6],
            y=[py-0.6, py-0.6, py+0.6, py+0.6, py-0.6, py-0.6, py+0.6, py+0.6],
            z=[h_viga + 0.2, h_viga + 0.2, h_viga + 0.2, h_viga + 0.2, h_viga, h_viga, h_viga, h_viga],
            color='#bdc3c7', opacity=1.0, flatshading=True, showlegend=False
        ))

    # --- 4. ARMÁRIO MASTER ALINHADO AO SKID ---
    # Posicionamento: Exatamente sobre a viga lateral superior
    px_armario = x0 + 0.5
    py_armario = prof_base/2 - 0.8  # ALINHADO COM O EIXO DA VIGA
    dx_arm, dy_arm, dz_arm = 0.6, 0.8, 2.0
    z0_arm = h_viga  # ASSENTADO NO TOPO DO AÇO

    # Caixa do Armário
    fig.add_trace(go.Mesh3d(
        x=[px_armario, px_armario+dx_arm, px_armario+dx_arm, px_armario, px_armario, px_armario+dx_arm, px_armario+dx_arm, px_armario],
        y=[py_armario-dy_arm/2, py_armario-dy_arm/2, py_armario+dy_arm/2, py_armario+dy_arm/2,
           py_armario-dy_arm/2, py_armario-dy_arm/2, py_armario+dy_arm/2, py_armario+dy_arm/2],
        z=[z0_arm+dz_arm, z0_arm+dz_arm, z0_arm+dz_arm, z0_arm+dz_arm, z0_arm, z0_arm, z0_arm, z0_arm],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        color='#E1D9C1', opacity=1.0, flatshading=True, name="Painel Controle (Skid-Mounted)"
    ))

    # Elementos da Face (IHM e Botões) - Ajustados para a nova altura Z
    face_x = px_armario + dx_arm + 0.01

    # Tela IHM
    fig.add_trace(go.Mesh3d(
        x=[face_x]*4, y=[py_armario-0.25, py_armario+0.25, py_armario+0.25, py_armario-0.25],
        z=[z0_arm+1.7, z0_arm+1.7, z0_arm+1.3, z0_arm+1.3],
        color='#1a1a1a', opacity=1.0, showlegend=False
    ))

    # Botoeiras
    fig.add_trace(go.Scatter3d(
        x=[face_x]*4, y=[py_armario-0.15, py_armario-0.15, py_armario+0.15, py_armario+0.15],
        z=[z0_arm+0.8, z0_arm+0.6, z0_arm+0.8, z0_arm+0.6],
        mode='markers', marker=dict(size=8, color=['#27ae60', '#c0392b', '#f1c40f', '#f1c40f']),
        showlegend=False
    ))

    return fig