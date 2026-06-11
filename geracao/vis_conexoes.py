import plotly.graph_objects as go

def add_conexoes(fig, raio, altura, esp_p):
    """
    Roteia a tubulação do ciclo sCO2 seguindo o layout do Skid.
    Utiliza pontos intermediários para criar curvas em 90 graus (Piping CAD).
    """
    r_ext = raio + esp_p
    h_viga = 0.35
    z_skid_top = h_viga + 0.2 # Nível de base das máquinas

    # --- COORDENADAS DE ENGATE (SINCRONIA TOTAL COM OS MÓDULOS CAD) ---
    pche_out = [r_ext + 0.7, 0, altura * 0.9]

    # Turbina (Corpo central)
    turb_in  = [r_ext + 4.0, 1.5, h_viga + 0.8] # Admissão lateral
    turb_out = [r_ext + 4.6, 2.0, h_viga + 0.8] # Saída axial

    # Recuperadores (Vasos Verticais)
    htr_top = [r_ext + 6.5, 2.0, altura * 0.75]
    htr_bot = [r_ext + 6.5, 2.0, altura * 0.55]
    ltr_top = [r_ext + 6.5, -2.0, altura * 0.35]
    ltr_bot = [r_ext + 6.5, -2.0, h_viga + 0.5]

    # Compressores (Volutas)
    mc_in = [r_ext + 8.5, 2.5, h_viga + 0.8]
    rc_in = [r_ext + 8.5, -2.5, h_viga + 0.8]

    # --- FUNÇÃO PARA TUBOS COM CURVAS EM 'L' ---
    def add_industrial_pipe(points, name, color, width=6):
        # Desempacota os pontos para criar a linha contínua
        x, y, z = [], [], []
        for p in points:
            x.append(p[0]); y.append(p[1]); z.append(p[2])

        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines', name=name,
            line=dict(color=color, width=width),
            hoverinfo='name', showlegend=False
        ))

    # --- ROTEAMENTO DO FLUIDO (TRAÇADO TÉCNICO) ---

    # 1. PCHE -> TURBINA (Vapor Vivo - Alta Energia)
    # Rota: Sai do tanque, desce um pouco e entra na lateral da turbina
    add_industrial_pipe([
        pche_out,
        [pche_out[0] + 1.5, 0, pche_out[2]], # Afasta do tanque
        [pche_out[0] + 1.5, 1.5, turb_in[2]], # Alinha com entrada turbina
        turb_in
    ], "Linha de Vapor Vivo", '#e74c3c', width=10)

    # 2. TURBINA -> HTR (Exaustão)
    add_industrial_pipe([
        turb_out,
        [r_ext + 5.5, 2.0, turb_out[2]], # Caminho pelo skid
        htr_top
    ], "Exaustão Turbina", '#e67e22')

    # 3. HTR -> LTR (Série de Recuperação)
    # O fluido sai por baixo do HTR e entra por cima do LTR (precisa cruzar o eixo Y)
    add_industrial_pipe([
        htr_bot,
        [htr_bot[0], 0, htr_bot[2]], # Ponto central
        [htr_bot[0], -2.0, htr_bot[2]], # Alinha com LTR
        ltr_top
    ], "Transferência Recuperadores", '#f39c12')

    # 4. LTR -> MC (Ramo Principal Frio)
    add_industrial_pipe([
        ltr_bot,
        [r_ext + 8.5, -2.0, ltr_bot[2]], # Segue pelo skid
        [r_ext + 8.5, 2.5, ltr_bot[2]], # Cruza para o compressor MC
        mc_in
    ], "Linha Fria (Sucção MC)", '#3498db')

    # 5. HTR -> RC (Bypass de Recompressão)
    # O "Split" acontece no HTR e vai para o recompressor
    add_industrial_pipe([
        htr_bot,
        [r_ext + 7.5, 2.0, htr_bot[2]],
        [r_ext + 7.5, -2.5, rc_in[2]],
        rc_in
    ], "Ramo Recompressão", '#2ecc71')

    # 6. RETORNO PARA O TANQUE (Fechamento do Ciclo)
    # Do compressor de volta para a entrada do PCHE (por baixo)
    add_industrial_pipe([
        mc_in,
        [r_ext + 10.0, 2.5, h_viga], # Ponto de retorno no fundo
        [r_ext + 10.0, 0, h_viga],
        [r_ext + 0.7, 0, h_viga], # Volta para a base do PCHE
        [r_ext + 0.7, 0, altura * 0.8] # Sobe para o PCHE
    ], "Retorno de Pressão", '#95a5a6')

    return fig
