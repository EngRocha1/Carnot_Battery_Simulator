import plotly.graph_objects as go
from dados_entrada import T_AMBIENTE
import numpy as np
# Módulos de Geração (Pacote geracao)
# from geracao import vis_pche
# from geracao import vis_turbine
# from geracao import vis_recuperadores
# from geracao import vis_compressores
# from geracao import vis_valvulas
# from geracao import vis_conexoes
# from geracao import vis_base

def plotar_campo_temperatura_3d(T_vetor,
                                malha,
                                raio,
                                altura,
                                esp_p,
                                esp_v,
                                material,
                                angulo_corte=4.71, # Valor padrão (~270°) caso não venha do slider
                                fator_densidade=1.0, # Valor padrão (100%) caso não venha do slider
                                T_amb=T_AMBIENTE
                                ):



    # --- AJUSTE DAS QUANTIDADES BASEADO NO FATOR ---
    num_n = int(3000 * fator_densidade)
    num_p = int(2500 * fator_densidade)
    num_t = int(1500 * fator_densidade)
    num_v = int(1500 * fator_densidade)

    """
    SESSÃO 1: MULTICAMADA COM CORTES FÍSICOS
    Representa o Núcleo, a Perlita Lateral, a Vermiculita (Base) e as fronteiras de tanques.
    """
    # --- 1. CONFIGURAÇÕES DE CORES ---
    # Correção de Sintaxe: yellow -> 0
    # Escala clássica de simulação térmica CFD (Azul-Amarelo-Vermelho)
    escala_termica_jet = [
        [0.0,  "rgb(0, 0, 50)"],       # 0% - Azul Marinho (Solo/Inicial)
        [0.1,  "rgb(0, 0, 131)"],      # 10% - Azul Royal
        [0.2,  "rgb(0, 100, 255)"],    # 20% - Azul Celeste (Transição fria)

        # --- NOVOS TONS: TRANSIÇÃO ROXO -> VERMELHO (NÚCLEO EM AQUECIMENTO) ---
        [0.3,  "rgb(75, 0, 130)"],     # 30% - Índigo/Roxo (Início da carga)
        [0.35, "rgb(102, 0, 102)"],    # 35% - Roxo Ameixa (NOVO)
        [0.4,  "rgb(153, 0, 153)"],    # 40% - Magenta Escuro (NOVO)
        [0.45, "rgb(204, 0, 102)"],    # 45% - Carmesim Profundo (NOVO)
        [0.5,  "rgb(220, 20, 60)"],    # 50% - Crimson/Cereja (NOVO)
        [0.55, "rgb(255, 0, 127)"],    # 55% - Rosa Choque Térmico (NOVO)

        # --- ZONA DE ALTA TEMPERATURA (NÚCLEO CARREGADO) ---
        [0.6,  "rgb(255, 0, 0)"],      # 60% - Vermelho Vivo
        [0.7,  "rgb(255, 69, 0)"],     # 70% - Laranja Avermelhado
        [0.8,  "rgb(255, 140, 0)"],    # 80% - Laranja (Saturação)
        [0.9,  "rgb(255, 255, 0)"],    # 90% - Amarelo Puro
        [1.0,  "rgb(255, 255, 255)"]   # 100% - Branco (Ponto de Carga 550°C)
    ]
    z_malha = np.linspace(0, altura, len(T_vetor))

    # --- 2. GERAÇÃO DE PARTÍCULAS (CALOR VINDO DO CENTRO) ---
    r_n = np.sqrt(np.random.rand(num_n)) * raio
    theta_n = np.random.rand(num_n) * angulo_corte
    z_n = np.random.rand(num_n) * altura

    # Mapeamento Radial:
    # O centro (r=0) é o ponto mais quente (T_vetor[0])
    # A borda (r=raio) é o ponto mais "frio" (T_vetor[-1])
    temp_n = np.interp(r_n, [0, raio], [T_vetor[0], T_vetor[-1]])
    x_n = r_n * np.cos(theta_n); y_n = r_n * np.sin(theta_n)

    # --- 3. CAMADA ANELAR: PERLITA EXPANDIDA (Isolamento Lateral e Topo) ---
    r_p = raio + (np.random.rand(num_p) * esp_p)
    theta_p = np.random.rand(num_p) * angulo_corte
    z_p = np.random.rand(num_p) * altura
    # T_vetor[-1] é a temperatura na borda do núcleo (raio)
    temp_p_lateral = np.interp(r_p, [raio, raio + esp_p], [T_vetor[-1], T_amb])

    # --- PERLITA DO TOPO (Calculada ANTES do uso) ---
    r_t = np.sqrt(np.random.rand(num_t)) * (raio + esp_p)
    theta_t = np.random.rand(num_t) * angulo_corte
    z_t = altura + (np.random.rand(num_t) * esp_p)
    # Gradiente Térmico do Topo
    temp_p_topo = np.interp(r_t, [0, raio + esp_p], [T_vetor[0], T_amb])

    # Gerando coordenadas para a lateral
    x_p = r_p * np.cos(theta_p)
    y_p = r_p * np.sin(theta_p)

    # Gerando coordenadas para o topo (Muitas vezes o erro está em esquecer estas duas)
    x_t = r_t * np.cos(theta_t)
    y_t = r_t * np.sin(theta_t)

    # --- 4. BASE ESTRUTURAL: VERMICULITA (Isolamento Basal) ---
    r_v = np.sqrt(np.random.rand(num_v)) * (raio + esp_p)
    theta_v = np.random.rand(num_v) * angulo_corte
    # Posicionada no volume negativo (abaixo do núcleo)
    z_v = - (np.random.rand(num_v) * esp_v)
    # Reflete a temperatura da base do núcleo dissipando para o solo
    # Simulação visual do gradiente de perda para o solo
    # O centro da base (r=0) recebe o calor da resistência, as bordas esfriam.
    temp_v = np.interp(r_v, [0, raio + esp_p], [T_vetor[0],T_amb])
    x_v = r_v * np.cos(theta_v); y_v = r_v * np.sin(theta_v)

    fig = go.Figure()

    # ADD: NÚCLEO (Ativando a Colorbar)
    fig.add_trace(go.Scatter3d(
        x=x_n, y=y_n, z=z_n,
        mode='markers',
        name=f"Núcleo de {material}",
        marker=dict(
            size=3.5,
            color=temp_n,
            colorscale=escala_termica_jet,
            opacity=1.0,
            cmin=303.15,           # Crava o azul em 30°C (Referência Solo/Ambiente)
            cmax=np.max(T_vetor),  # O branco/vermelho será a maior do momento
            showscale=True, # <--- ISSO FAZ A BARRA APARECER
            colorbar=dict(
                title="Temperatura (K)",
                thickness=20,
                titleside="right",
                outlinecolor="white",
                tickfont=dict(color="white"), # Melhora visibilidade no fundo escuro
                titlefont=dict(color="white")
            )
        )
    ))

    # 2. ADD PERLITA (Unindo Lateral + Topo para fechar o envelope)
    fig.add_trace(go.Scatter3d(
        x=np.concatenate([x_p, x_t]),
        y=np.concatenate([y_p, y_t]),
        z=np.concatenate([z_p, z_t]),
        mode='markers',
        name="Isolamento Perlita",
        marker=dict(
            size=2.5,
            color=np.concatenate([temp_p_lateral, temp_p_topo]),
            colorscale=escala_termica_jet,
            opacity=0.8,
            cmin=303.15,           # Crava o azul em 30°C (Referência Solo/Ambiente)
            cmax=np.max(T_vetor),  # O branco/vermelho será a maior do momento
            showscale=False
        )
    ))

    # ADD: VERMICULITA (Base estrutural com limites térmicos fixos)
    fig.add_trace(go.Scatter3d(
        x=x_v, y=y_v, z=z_v,
        mode='markers',
        name="Base Vermiculita",
        marker=dict(
            size=2.5,
            color=temp_v,
            colorscale=escala_termica_jet,
            cmin=303.15,           # Crava o azul em 30°C (Referência Solo/Ambiente)
            cmax=np.max(T_vetor),  # O branco/vermelho será a maior do momento
            opacity=0.8,
            showscale=False
        )
    ))



    # --- CAMADA DE AÇO (CARCAÇA EXTERNA - CORTES) ---
    # Gerando malhas cilíndricas translúcidas para as fronteiras de TANQUES
    th_range = np.linspace(0, 1.5 * np.pi, 50)

    # Corte 1: Tanque Interno / Interface Perlite (Raio = raio)
    z_tanque_int = np.linspace(0, altura, 20)
    th_grid, z_grid_int = np.meshgrid(th_range, z_tanque_int)

    fig.add_trace(go.Surface(
        x=raio * np.cos(th_grid), y=raio * np.sin(th_grid), z=z_grid_int,
        opacity=0.1, showscale=False, colorscale=[[0, '#dfe6e9'], [1, '#dfe6e9']], # Cinza Metalico sutil
        name="Tanque Interno (Aço/Núcleo)", hoverinfo='skip'
    ))

    # --- NOVO: TAMPA DO NÚCLEO INTERNO (DISCO EM z = altura) ---
    # Este disco sela o núcleo e tem o mesmo diâmetro variável 'raio'
    r_range_n = np.linspace(0, raio, 20)
    # th_range já está definido com o corte de 1.5 * np.pi
    RN_grid, THN_grid = np.meshgrid(r_range_n, th_range)

    fig.add_trace(go.Surface(
        x=RN_grid * np.cos(THN_grid),
        y=RN_grid * np.sin(THN_grid),
        z=np.full_like(RN_grid, altura), # Posicionado exatamente no topo do núcleo
        opacity=0.2,
        showscale=False,
        colorscale=[[0, '#dfe6e9'], [1, '#dfe6e9']], # Cinza metálico (mesmo do tanque interno)
        name="Tampa do Tanque Interno",
        hoverinfo='skip'
    ))

    # Corte 2: Casca Externa do Tanque (Raio total = raio + esp_p)
    z_casca_ext = np.linspace(-esp_v, altura + esp_p, 30) # Cobre da base ao topo
    th_grid, z_grid_ext = np.meshgrid(th_range, z_casca_ext)
    r_total = raio + esp_p

    fig.add_trace(go.Surface(
        x=r_total * np.cos(th_grid), y=r_total * np.sin(th_grid), z=z_grid_ext,
        opacity=0.15, showscale=False, colorscale=[[0, '#f5f6fa'], [1, '#f5f6fa']], # Aço Inox Claro
        name="Casca Externa de Aço", hoverinfo='skip'
    ))

    # --- NOVO: CORTE NO TOPO (DISCO DE FECHAMENTO SUPERIOR) ---
    # Define a tampa do tanque externo, respeitando o fatiamento de 270 graus
    r_range_topo = np.linspace(0, r_total, 20)
    # Usamos th_range (definido na linha 5 do seu trecho) para manter o corte
    RT_grid, TH_grid_topo = np.meshgrid(r_range_topo, th_range)

    fig.add_trace(go.Surface(
        x=RT_grid * np.cos(TH_grid_topo),
        y=RT_grid * np.sin(TH_grid_topo),
        z=np.full_like(RT_grid, altura + esp_p), # Posicionado no topo da Perlita
        opacity=0.2,
        showscale=False,
        colorscale=[[0, '#f5f6fa'], [1, '#f5f6fa']], # Mesmo tom do aço inox
        name="Tampa Superior (Corte)",
        hoverinfo='skip'
    ))


    # Corte 3: Fronteira Base / Núcleo (Disco Plano em z=0)
    # Mostra exatamente onde termina o concreto e começa o núcleo
    if esp_v > 0.01:
        th_range_full = np.linspace(0, 1.5*np.pi, 50)
        r_range = np.linspace(0, r_total, 20)
        r_grid, th_grid_disc = np.meshgrid(r_range, th_range_full)
        fig.add_trace(go.Surface(
            x=r_grid * np.cos(th_grid_disc), y=r_grid * np.sin(th_grid_disc),
            z=np.zeros_like(r_grid),
            opacity=0.1, showscale=False, colorscale=[[0, '#dfe6e9'], [1, '#dfe6e9']],
            name="Corte: Fronteira Base/Núcleo", hoverinfo='skip'
        ))

    # --- NOVO: FECHAMENTO DA BASE SÓLIDA (DISCO NO CHÃO) ---
    # Cria o fundo do reservatório no nível z = -esp_v
    th_range_full = np.linspace(0, 1.5*np.pi, 50)
    r_range_fundo = np.linspace(0, r_total, 20)
    rf_grid, thf_grid = np.meshgrid(r_range_fundo, th_range_full)

    fig.add_trace(go.Surface(
        x=rf_grid * np.cos(thf_grid), y=rf_grid * np.sin(thf_grid),
        z=np.full_like(rf_grid, -esp_v),
        opacity=0.3, showscale=False, colorscale=[[0, '#dfe6e9'], [1, '#dfe6e9']],
        name="Base Inferior", hoverinfo='skip'
    ))

    # --- NOVO: GRADE DE SOLO (GRID CINZA) ---
    # Desenha as linhas no chão para referência de profundidade
    grid_size = r_total * 2.5
    linhas = np.linspace(-grid_size, grid_size, 11)

    for val in linhas:
        # Linhas paralelas ao eixo X
        fig.add_trace(go.Scatter3d(
            x=[val, val], y=[-grid_size, grid_size], z=[-esp_v, -esp_v],
            mode='lines', line=dict(color='rgba(150,150,150,0.15)', width=1), showlegend=False
        ))
        # Linhas paralelas ao eixo Y
        fig.add_trace(go.Scatter3d(
            x=[-grid_size, grid_size], y=[val, val], z=[-esp_v, -esp_v],
            mode='lines', line=dict(color='rgba(150,150,150,0.15)', width=1), showlegend=False
        ))

    # --- CONFIGURAÇÃO DE CENA E PERSPECTIVA ---
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode='data',
            camera=dict(
                eye=dict(x=1.6, y=-1.6, z=1.1) # Perspectiva superior inclinada
            )
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )


    # --- ACOPLAMENTO DINÂMICO USODACARCAÇA ---
    # 1. Primeiro a Base (O "Chão" técnico)
    #     vis_base.add_vis_base(fig, raio, altura, esp_p)

    # 2. Depois os Componentes (Que agora usam Z=0 ou próximo de 0 para sentar na base)
    #     vis_pche.add_pche(fig, raio, altura, esp_p)
    #     vis_turbine.add_turbine(fig, raio, altura, esp_p)
    #     vis_recuperadores.add_recuperadores(fig, raio, altura, esp_p)
    #     vis_compressores.add_compressores(fig, raio, altura, esp_p)
    #     vis_valvulas.add_valvulas(fig, raio, altura, esp_p)
    #     vis_conexoes.add_conexoes(fig, raio, altura, esp_p)

    return fig