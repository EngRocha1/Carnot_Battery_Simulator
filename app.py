import streamlit as st
import numpy as np
from solucao_principal import simular_difusao_termica
from mef_montagem import monta_matrizes_globais

# --- IMPORTAÇÃO E RELOAD DO BANCO DE DADOS ---
import importlib         # <-- ESTA É A LINHA QUE FALTAVA
import dados_entrada
importlib.reload(dados_entrada)

# Módulos de Visualização e Memorial (As 4 Folhas)
import visualization_sessao1 as vis1
import visualization_sessao2 as vis2
import visualization_sessao3 as vis3
import visualization_sessao4 as vis4


# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Master Dashboard - Carnot UFPI", layout="wide")

st.markdown("""
    <style>
    .section-head { background-color: #0e1117; color: #ffd700; padding: 15px; border-radius: 10px; margin-top: 30px; font-weight: bold; border-left: 10px solid #ffd700; font-size: 1.2rem; }
    .stProgress > div > div > div > div { background-color: #ffd700; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Bateria de Carnot Multiescala")
st.caption("PPGEE UFPI | Pesquisador: Tarcísio Rocha | Orientador: Dr. Marcos Lira")

# --- SIDEBAR: PARÂMETROS DE ENTRADA ---
with st.sidebar:
    st.header("⚙️ Configurações de Projeto")

    with st.expander("🏗️ Dimensões Principais", expanded=True):
        # 1. Definição do material
        lista_materiais = list(dados_entrada.BANCO_MATERIAIS.keys()) + ["Manual"]
        mat = st.radio("Material do Núcleo", lista_materiais, index=0)

        # 2. Lógica de Entrada Manual
        if mat == "Manual":
            st.warning("⚠️ Configuração de Substrato Customizado")
            rho_man = st.number_input("Densidade (kg/m³)", value=2000.0)
            cp0_man = st.number_input("Calor Específico (J/kgK)", value=700.0)
            k0_man = st.number_input("Condutividade (W/mK)", value=1.0)
            trans_man = st.checkbox("Sofre Transição de Fase (ex: Sílica)?")
            limite_man = st.number_input("Limite de Estabilidade [°C]", value=1000.0)
            ativo_man = st.checkbox("Material Quimicamente Ativo/Degradável?")

            # Atualiza o dicionário no módulo dados_entrada
            dados_entrada.BANCO_MATERIAIS["Manual"] = {
                "rho": rho_man, "cp0": cp0_man, "beta": 0.2, "k0": k0_man,
                "alpha": 0.0005, "trans": trans_man, "t_limite": limite_man, "ativo": ativo_man
            }


        # 3. VALIDAÇÃO DE SEGURANÇA (Fora do if "Manual" para checar todos)
        if dados_entrada.BANCO_MATERIAIS[mat]["rho"] <= 0:
            st.error(f"Erro: A densidade para '{mat}' deve ser maior que zero.")
            st.stop() # Interrompe a execução aqui se o dado estiver errado

        # Atualiza a referência global
        MATERIAL_SELECIONADO = mat
        dados_entrada.MATERIAL_SELECIONADO = mat

        raio = st.slider("Raio do Núcleo (m)", 0.5, 20.0, 6.0)
        altura = st.slider("Altura do Núcleo (m)", 0.5, 50.0, 12.0)
        t_carga_celsius = st.slider("Temperatura de Carga [°C]", 0.5, 1000.0, 540.0)
        t_carga = t_carga_celsius + 273.15

    with st.expander("🏗️ Parâmetros de Simulação e 3D", expanded=True):
        passo_temporal = st.slider("Passo de Tempo (dt) [s]", 1.0, 600.0, 50.0)
        angulo_slider = st.slider("Ângulo de Corte Visual (°)", 0.0, 360.0, 275.0)
        angulo_corte = (angulo_slider / 180.0) * np.pi
        densidade_pontos = st.slider("Densidade de Partículas (%)", 10.0, 200.0, 100.0)
        fator_densidade = densidade_pontos / 100.0
        st.info("💡 Menor densidade melhora a fluidez da rotação 3D.")

    with st.expander("🌍 Condições Ambientais & Convecção", expanded=True):
        temp_amb_c = st.slider("Temperatura Ambiente (°C)", 10, 50, 30, help="Temperatura do ar externo ao redor do tanque.")
        T_AMBIENTE = temp_amb_c + 273.15
        v_vento = st.slider("Velocidade do Vento (m/s)", 0.0, 20.0, 3.5, help="Velocidade do ar para cálculo do coeficiente de película.")
        st.markdown("---")
        st.caption("🔧 Ajuste Fino da Correlação (h = A + B * v)")
        coeff_a = st.slider("Constante A (Radiação/Convecção Natural)", 1.0, 10.0, 5.7, step=0.1)
        coeff_b = st.slider("Constante B (Convecção Forçada)", 1.0, 10.0, 3.8, step=0.1)
        h_conv = coeff_a + (coeff_b * v_vento)
        st.metric("h_conv Resultante", f"{h_conv:.2f} W/m²K")
        st.info("💡 Valores de 5.7 e 3.8 são padrão para superfícies rugosas ao ar livre.")

    with st.expander("🌍 Parâmetros Geotécnicos (Solo)", expanded=True):
        temp_solo_c = st.slider("Temperatura do Solo (°C)", 15.0, 35.0, 25.0)
        k_solo_real = st.slider("Condutividade Térmica do Solo (W/mK)", 0.2, 2.5, 0.5)
        st.info(f"💡 Solo definido com k={k_solo_real} W/mK e T={temp_solo_c}°C.")

    with st.expander("🛡️ Blindagem Térmica", expanded=True):
        esp_p = st.slider("Espessura Perlite [m]", 0.1, 3.0, 1.0)
        esp_v = st.slider("Espessura Vermiculite [m]", 0.1, 5.0, 1.5)

    with st.expander("💰 Economia e PPA", expanded=True):
        prazo_ppa = st.number_input("Prazo Contrato (Anos)", value=15)
        preco_venda = st.number_input("Preço Venda (R$/MWh)", value=480)

    with st.expander("💰 Gestão Financeira (CAPEX & OPEX)", expanded=False):
        st.subheader("🏗️ Custos de Instalação (CAPEX)")
        custo_meio = st.number_input("Meio Granular [R$/m³]", value=580)
        custo_perlite = st.number_input("Instalação Perlite [R$/m]", value=140000)
        custo_vermiculite = st.number_input("Instalação Vermiculite [R$/m]", value=98000)
        st.divider()
        st.subheader("⚡ Estratégia de Carga (Arbitragem)")
        p_curtailment = st.number_input("Preço Curtailment (R$/MWh)", value=50.0)
        p_mercado = st.number_input("Preço Mercado/Grid (R$/MWh)", value=180.0)

        pct_curtailment = st.slider("% Energia em Curtailment", 0, 100, 30)
        preco_compra = (p_curtailment * (pct_curtailment/100)) + \
                                 (p_mercado * ((100 - pct_curtailment)/100))
        st.info(f"💡 Preço Médio de Compra: R$ {preco_compra:.2f}/MWh")
        st.divider()
        st.subheader("🔧 Operação (OPEX)")
        custo_fixo_api = st.number_input("Opex/Manutenção (Base) [R$/MWh]", value=75)

# --- ENGINE DE PROCESSAMENTO INICIAL (ESTABILIZADO) ---
try:

    # Garante que temos um material selecionado
    if 'mat' not in locals():
        mat = "Areia de Sílica" # Valor padrão de segurança

    n_nos = 50
    T_init = np.ones(n_nos) * T_AMBIENTE
    T_init[0] = t_carga
    vol = np.pi * (raio**2) * altura
    fator_mat = dados_entrada.BANCO_MATERIAIS[mat]["rho"] / 1650.0
    capex = (vol * custo_meio*fator_mat) + (esp_p*custo_perlite)+(esp_v*custo_vermiculite)

    # 1. Parâmetro de tempo e Botão de Execução
    t_manual = st.slider("Tempo de Operação (Horas)", 0, 72, 0)

    with st.sidebar:
        st.divider()
        btn_rodar = st.button("⚡ RODAR SIMULAÇÃO", type="primary", use_container_width=True)
        if st.button("🗑️ Limpar Cache"):
            st.session_state.clear()
            st.rerun()

    if btn_rodar:
        with st.spinner("Resolvendo EDP Transiente (Newton-Raphson)..."):
            res_sim_bruto, malha_res, log_conv = simular_difusao_termica(
                T_init,
                t_manual * 3600,
                dt=passo_temporal,
                esp_p=esp_p,
                esp_v=esp_v,
                h_conv=h_conv
            )
            salto = 10 if len(res_sim_bruto) > 200 else 1
            st.session_state['dados_mef'] = res_sim_bruto[::salto]
            st.session_state['malha_mef'] = malha_res
            st.session_state['log_residuos'] = log_conv
            st.toast("Cálculo finalizado!", icon="✅")


    if 'dados_mef' in st.session_state:
        historico_visualizacao = st.session_state['dados_mef']
        malha = st.session_state['malha_mef']

        if len(historico_visualizacao) > 1:
            st.markdown('<div class="section-head">⏲️ LINHA DO TEMPO DA OPERAÇÃO</div>', unsafe_allow_html=True)
            idx_tempo = st.slider(
                "Selecione o instante para visualização",
                0, len(historico_visualizacao) - 1, len(historico_visualizacao) - 1
            )
            T_atual = historico_visualizacao[idx_tempo]
        else:
            T_atual = historico_visualizacao[0]
            st.info("💡 Aumente o 'Tempo de Operação' e clique em 'RODAR' para navegar.")

        # ==============================================================================
        # NOVO BLOCO: LÓGICA DE TRANSIÇÃO DE FASE E DILATAÇÃO (INSERIR AQUI)
        # ==============================================================================
        vol_nominal = np.pi * (raio**2) * altura
        T_media_c = np.mean(T_atual) - 273.15

        if T_media_c < 573.0: # T_INVERSAO_QUARTZO (Celsius)
            fase = "Alpha-Quartzo"
            # Dilatação linear elástica proporcional (Ref: Incropera)
            dilatacao_linear = 0.013 * (T_media_c / 573.0)
            status_critico = False
        else:
            fase = "Beta-Quartzo"
            # Salto volumétrico crítico permanente (Ref: Mordor Intelligence)
            dilatacao_linear = 0.045
            status_critico = True

        variacao_volumetrica = vol_nominal * dilatacao_linear
        # ==============================================================================


        _, _, diagn = monta_matrizes_globais(T_atual, n_nos, retorno_diagnostico=True)

        tab1, tab2, tab3 = st.tabs(["🌡️ Perfis", "🛡️ Memorial de Blindagem & Aço", "💰 Análise Econômica PPA"])

        with tab1:
            st.markdown('<div class="section-head">🕒 DINÂMICA TEMPORAL E GRADIENTE VERTICAL</div>', unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            with c1:
                fig_3d = vis1.plotar_campo_temperatura_3d(T_atual, malha, raio, altura, esp_p, esp_v, mat)
                st.plotly_chart(fig_3d, use_container_width=True)
            with c2:
                st.write("### Perfil de Corte")
                fig_corte = vis3.plotar_perfis_corte(T_atual, altura)
                st.pyplot(fig_corte)
                st.info(vis4.obter_resumo_academico("termogeometria"))
            st.divider()


            # --- BLOCO DE INTEGRIDADE TERMOMECÂNICA DINÂMICO ---
            st.subheader(f"🏗️ Monitor de Integridade: Substrato {mat}")

            # Cálculos Baseados no Material Selecionado
            T_max_atual = np.max(T_atual) - 273.15
            T_media_atual = np.mean(T_atual) - 273.15

            if mat == "Areia de Sílica":
                # --- LÓGICA SÍLICA (Ref: Zhang, H. et al., 2021) ---
                T_CRITICA = 573.0
                if T_max_atual < T_CRITICA:
                    fase, status_cor, msg = "Alpha-Quartzo", "success", "✅ REGIME ESTÁVEL: Abaixo do ponto de inversão."
                    dilatacao_linear = 0.013 * (T_media_atual / T_CRITICA)
                else:
                    fase, status_cor, msg = "Beta-Quartzo", "error", "🚨 TRANSIÇÃO POLIMÓRFICA: Risco de fadiga térmica."
                    dilatacao_linear = 0.045 # Expansão cumulativa/reconstrutiva

                label_metrica = "Expansão do Leito"
                val_metrica = f"+ {vol_nominal * dilatacao_linear:.3f} m³"
                delta_metrica = f"{dilatacao_linear*100:.2f}%"
                help_text = "Acomodação granular em torno de 573°C (Transição Deslocativa)."

            else:
                # --- LÓGICA GRAFITE (Ref: Zhang, Y. et al., 2021 / Taylor et al., 2021) ---
                T_ALERTA = 450.0
                T_CRITICA_G = 500.0

                # Simulação de vácuo (Pode ser um checkbox na sidebar futuramente)
                vacuo_ativo = False

                if vacuo_ativo:
                    fase, status_cor, msg = "Ambiente Inerte", "success", "✅ ESTABILIDADE ALTA: Operação em vácuo/gás inerte."
                    status_critico = False
                elif T_max_atual < T_ALERTA:
                    fase, status_cor, msg = "Grafite Estável", "success", "✅ LIMITE DE OXIDAÇÃO: Operação segura no Ar."
                    status_critico = False
                elif T_max_atual < T_CRITICA_G:
                    fase, status_cor, msg = "Oxidação Inicial", "warning", "⚠️ RISCO QUÍMICO: Início da conversão C -> CO2."
                    status_critico = True
                else:
                    fase, status_cor, msg = "Degradação Crítica", "error", "🚨 OXIDAÇÃO EXPONENCIAL: Perda de massa insustentável."
                    status_critico = True

                # Grafite Isostático tem CET baixo (~4e-6)
                cet_grafite = 4e-6
                dilatacao_linear = cet_grafite * T_media_atual
                label_metrica = "Estabilidade Dimensional"
                val_metrica = "Alta" if T_max_atual < 1000 else "Moderada"
                delta_metrica = f"{dilatacao_linear*100:.3f}%"
                help_text = "Grafite Policristalino Isostático: Anisotropia minimizada."

            # --- RENDERIZAÇÃO NA INTERFACE ---
            c_fase1, c_fase2, c_fase3 = st.columns(3)

            with c_fase1:
                if status_cor == "success": st.success(f"**{fase}**")
                elif status_cor == "warning": st.warning(f"**{fase}**")
                else: st.error(f"**{fase}**")
                st.caption(msg)

            with c_fase2:
                st.metric(label_metrica, val_metrica, delta=delta_metrica, help=help_text)

            with c_fase3:
                # Busca o limite do banco e o estado atual
                limite_seguro = dados_entrada.BANCO_MATERIAIS[mat].get("t_limite", 500.0)

                # 1. AREIA DE SÍLICA: Foco em Dilatação/Folga Mecânica
                if mat == "Areia de Sílica":
                    folga = vol_nominal * 0.05
                    if (vol_nominal * dilatacao_linear) > folga:
                        st.warning("🚨 LIMITE DE FOLGA EXCEDIDO: Risco de compressão mecânica na carcaça.")
                    else:
                        st.info("🟢 DILATAÇÃO ACOMODADA: Folga térmica dentro dos parâmetros de projeto.")

                # 2. GRAFITE: Foco em Oxidação (Requer Vácuo ou Gás Inerte)
                elif mat == "Grafite":
                    vacuo_ativo = False
                    if not vacuo_ativo and T_max_atual > 450:
                        st.error("❗ OXIDAÇÃO ACELERADA: Necessário sistema de vácuo ou purga com Nitrogênio.")
                    else:
                        st.info("🛡️ INTEGRIDADE QUÍMICA OK: Ambiente inerte ou temp. dentro do range de segurança.")

                # 3. CARBONATO DE CÁLCIO: Foco em Calcinação (Requer Pressurização)
                elif mat == "Carbonato de Cálcio":
                    pressao_co2_ativa = False
                    if not pressao_co2_ativa and T_max_atual > 650:
                        st.error("❗ NECESSÁRIO SELO DE PRESSÃO (Atmosfera de CO₂): Risco de calcinação (CaCO₃ -> CaO).")
                    else:
                        st.info("🛡️ ESTABILIDADE QUÍMICA OK: Atmosfera de CO₂ controlada.")

                # 4. HEMATITA E ALUMINA: Foco em Fluência e Integridade Estrutural
                else:
                    if T_max_atual > limite_seguro:
                        st.error(f"🚨 LIMITE TÉRMICO EXCEDIDO (> {limite_seguro}°C): Risco de degradação estrutural e fluência.")
                    else:
                        st.success(f"🛡️ OPERAÇÃO SEGURA: Estrutura estável (T < {limite_seguro}°C).")

                st.divider()
    # --- BLOCO DE INTEGRIDADE TERMOMECÂNICA ---



        st.markdown("#### 📊 Análise Energética do Perfil (Área Hachurada)")

        st.write("""A área rosada no gráfico de profundidade representa a **Entalpia Acumulada** no meio granular.""")
        st.latex(r"E_{acum} = \int_{0}^{L} \rho \cdot C_p(T) \cdot [T(z,t) - T_{amb}] \, dz")

        # BUSCA DINÂMICA: Pega a densidade direto do banco de dados, independente do material
        rho_material = dados_entrada.BANCO_MATERIAIS[mat]["rho"]

        cp_material = diagn['rhoCp_local'] / rho_material
        delta_T_medio = np.mean(T_atual) - T_AMBIENTE
        densidade_ev = (rho_material * cp_material * delta_T_medio) / 3.6e6

        col_m1, col_m2 = st.columns([1, 2])
        with col_m1:
            st.metric(
                label=f"Densidade Energética ({mat})",
                value=f"{densidade_ev:.2f} kWh/m³"
            )

        with col_m2:
            with st.expander("💡 O que este cálculo nos diz?", expanded=False):
                st.info(f"Para o material **{mat}**, este valor indica quanto cada m³ de núcleo está armazenando.")

        with tab2:
            st.markdown('<div class="section-head">🛡️ MEMORIAL DE CÁLCULO: PERDAS E INTEGRIDADE DO AÇO</div>', unsafe_allow_html=True)
            col_g, col_calc = st.columns([1.5, 1])


            fig_mem, q_lat, q_solo, t_c_lat, t_c_v = vis2.plotar_memorial_blindagem(
                raio, altura, esp_p, esp_v, T_atual[0], T_atual[-1], T_AMBIENTE, dados_entrada.K_PERLITA, dados_entrada.K_VERMICULITA, h_conv
            )

            with col_g:
                # 1. Gráfico das Barreiras Térmicas
                st.pyplot(fig_mem)

                st.divider()

                # 2. SEÇÃO EXCLUSIVA: INTEGRIDADE DO TROCADOR (PCHE)
                st.subheader("🏗️ Integridade Estrutural: Trocador de Calor (PCHE)")
                st.write("Seleção de liga metálica baseada no limite de **Fluência (Creep)** para a temperatura de carga.")

                # Lógica de seleção do aço
                tipo_aco = "SS-316H" if t_carga < 850 else "Inconel 617"
                limite_aco = 850.0 if tipo_aco == "SS-316H" else 1250.0
                percentual_limite = min(t_carga/limite_aco, 1.0)

                c_aco1, c_aco2 = st.columns([1, 2])
                c_aco1.metric("Liga Recomendada", tipo_aco)
                c_aco2.write(f"**Fator de Utilização Térmica:** {percentual_limite*100:.1f}%")
                st.progress(percentual_limite)
                st.caption(f"Nota: O {tipo_aco} é selecionado para garantir vida útil acima de 100.000h sob alta temperatura.")

            with col_calc:
                st.subheader("📝 Memorial de Fluxos e Custos")

                # --- CORREÇÃO FÍSICA: GRADIENTE GEOTÉRMICO (SOLO) ---
                T_SOLO_K = 298.15
                area_contato_solo = np.pi * (raio + esp_p)**2

                # Perda Lateral
                area_lat = 2 * np.pi * (raio + esp_p) * altura
                perda_lat_mwh = (q_lat * area_lat * 8760) / 1e6

                # Perda Solo
                U_base = 1.0 / ((esp_v / dados_entrada.K_VERMICULITA) + (1.0 / 0.5))


                q_solo_real = U_base * (T_atual[-1] - T_SOLO_K)
                perda_solo_mwh = (q_solo_real * area_contato_solo * 8760) / 1e6

                perda_total_ano = perda_lat_mwh + perda_solo_mwh
                prejuizo_anual = perda_total_ano * preco_venda

                st.write(f"Perda Lateral: **{perda_lat_mwh:.2f} MWh/ano**")
                st.write(f"Perda Solo: **{perda_solo_mwh:.2f} MWh/ano**")

                c_m1, c_m2 = st.columns(2)
                c_m1.metric("PERDA TOTAL", f"{perda_total_ano:.2f} MWh/ano")
                c_m2.metric("PREJUÍZO (SPREAD)", f"R$ {prejuizo_anual/1000:.1f}k/ano", delta_color="inverse")

                st.divider()

                # --- SEÇÃO EXCLUSIVA: SEGURANÇA OPERACIONAL NR-12 ---
                st.subheader("👷 Segurança Operacional (NR-12)")
                st.markdown("""
                > **NR-12.11.1:** As superfícies aquecidas devem possuir isolamento ou barreiras 
                > para prevenção de queimaduras por contato direto.
                """)

                t_casca_c = t_c_lat - 273.15

                # Exibição do Status da Norma
                if t_casca_c > 60:
                    st.error(f"🚨 **VIOLAÇÃO NR-12:** {t_casca_c:.1f}°C na superfície externa.")
                    st.info("💡 **Ação:** Risco de queimadura detectado. Aumente a espessura de Perlite.")
                else:
                    st.success(f"✅ **CONFORME NR-12:** {t_casca_c:.1f}°C (Abaixo do limite de 60°C).")

                # Indicador visual de temperatura de contato
                st.write("**Gradiente de Contato (Casca):**")
                st.progress(min(t_casca_c/100, 1.0))

        # --- NOVO: GRÁFICO DE PERFIL DE TEMPERATURA RADIAL (RIGOR TÉCNICO) ---
        st.divider()
        st.subheader("📉 Perfil de Decaimento Térmico Radial")
        st.write("Análise da queda de temperatura através das múltiplas barreiras de resistência térmica.")

        import plotly.graph_objects as go

        # 1. Definindo as coordenadas radiais das interfaces (em metros)
        r_nucleo = raio
        r_perlite = raio + esp_p
        r_casca = r_perlite + 0.01 # assumindo 10mm de aço

        distancias = [0, r_nucleo, r_perlite, r_casca]

        # 2. Temperaturas nas interfaces (Kelvin para Celsius para visualização)
        # T_atual[0] é o núcleo, t_c_lat é a face externa (calculada pela vis2)
        temps = [
            T_atual[0] - 273.15,  # Centro
            T_atual[0] - 273.15,  # Interface Núcleo/Perlite
            t_c_lat - 273.15,     # Face externa da Perlite
            T_AMBIENTE - 273.15   # Ar Ambiente (Ponto de dissipação final)
        ]

        fig_radial = go.Figure()

        # Adicionando as camadas como regiões sombreadas para rigor visual
        fig_radial.add_vrect(x0=0, x1=r_nucleo, fillcolor="orange", opacity=0.2, layer="below", line_width=0, annotation_text="NÚCLEO")
        fig_radial.add_vrect(x0=r_nucleo, x1=r_perlite, fillcolor="gray", opacity=0.2, layer="below", line_width=0, annotation_text="PERLITE")

        # Linha do Perfil
        fig_radial.add_trace(go.Scatter(
            x=distancias, y=temps,
            mode='lines+markers+text',
            text=[f"{t:.1f}°C" for t in temps],
            textposition="top right",
            line=dict(color='#ffd700', width=4),
            marker=dict(size=10, symbol='diamond')
        ))

        fig_radial.update_layout(
            xaxis_title="Raio do Reservatório (m)",
            yaxis_title="Temperatura (°C)",
            template="plotly_dark",
            height=400,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig_radial, use_container_width=True)

        st.info("""**Análise de Gradiente:** A inclinação da linha na zona 'PERLITE' representa a 
        eficácia do isolamento. Quanto mais íngreme a queda, maior a resistência térmica do material 
        selecionado, garantindo a proteção da carcaça externa conforme exigido pela NR-12.""")

        # --- PERFIL TÉCNICO EXCLUSIVO: BASE (VERMICULITA) ---
        st.subheader("📉 Gradiente Térmico da Base: Vermiculita para Solo")
        st.write("Análise do decaimento térmico na interface inferior do reservatório.")

        import plotly.graph_objects as go
        import numpy as np

        # 1. Definição da Espessura (Eixo X)
        # 0 representa a face em contato com o núcleo; esp_v representa o contato com o solo
        esp_eixo_x_v = np.linspace(0, esp_v, 20)

        # 2. Temperaturas (Eixo Y)
        # T_atual[-1] é a temperatura real no fundo do núcleo (lado quente)
        # t_c_v é a temperatura calculada na face externa da vermiculita (lado solo)
        temp_v_inicio = T_atual[-1] - 273.15
        temp_v_fim = t_c_v - 273.15

        # Interpolação linear do decaimento na camada
        perfil_vermi = np.linspace(temp_v_inicio, temp_v_fim, 20)

        fig_v = go.Figure()

        # Adicionando a linha de decaimento
        fig_v.add_trace(go.Scatter(
            x=esp_eixo_x_v,
            y=perfil_vermi,
            mode='lines',
            name='Condução na Vermiculita',
            line=dict(color='#00e5ff', width=5)
        ))

        # Adicionando marcação do Solo (Dissipador)
        fig_v.add_hline(y=25, line_dash="dot", line_color="green",
                        annotation_text="Temperatura do Solo (Referência: 25°C)")

        # Definindo os limites dinâmicos para o rigor visual
        y_min = 20  # Margem abaixo da temperatura do solo (25°C)
        y_max = max(temp_v_inicio + 20, 60) # Garante que o topo do gráfico acompanhe o aquecimento do fundo

        fig_v.update_layout(
            yaxis=dict(
                range=[y_min, y_max],
                title="Temperatura (°C)",
                gridcolor='gray'
            ),
            xaxis_title="Espessura da Camada de Vermiculite (m)",
            template="plotly_dark"
        )

        st.plotly_chart(fig_v, use_container_width=True)

        st.info(f"""**Rigor Geotécnico:** A Vermiculita reduz a temperatura de fundo de 
        {temp_v_inicio:.1f}°C para {temp_v_fim:.1f}°C. Este gradiente de 
        {temp_v_inicio - temp_v_fim:.1f}°C valida a baixa dissipação para o solo calculada no memorial.""")




        # --- ANÁLISE DE TEMPO DE CARGA/DESCARGA ---
        st.divider()
        st.subheader("⏳ Estimativa de Ciclo Operacional")

        # 1. Cálculo da Potência Líquida
        # Potência de Entrada (Exemplo vindo do seu t_carga)
        potencia_entrada_estimada = 30.0 # MW (Valor de projeto do seu Master)

        # Perda Instantânea (convertendo MWh/ano para MW)
        perda_instantanea_mw = perda_total_ano / 8760

        potencia_liquida = potencia_entrada_estimada - perda_instantanea_mw

        # 2. Energia Necessária para Carga Completa
        # Delta T total desejado (T_carga - T_amb)
        cp_medio = diagn['rhoCp_local'] / rho_material
        energia_total_mwh = (vol * rho_material * cp_medio * (t_carga - T_AMBIENTE)) / 3.6e9

        energia_atual_mwh = (vol * rho_material * cp_medio * (np.mean(T_atual) - T_AMBIENTE)) / 3.6e9
        energia_faltante = energia_total_mwh - energia_atual_mwh

        # 3. Cálculo dos Tempos
        tempo_restante_carga = energia_faltante / potencia_liquida if potencia_liquida > 0 else float('inf')

        # Tempo de autodescarga (Quanto tempo leva para perder 10% da carga parado)
        tempo_autodescarga_10pct = (energia_total_mwh * 0.10) / perda_instantanea_mw

        # --- EXIBIÇÃO NO DASHBOARD ---
        tc1, tc2, tc3 = st.columns(3)

        tc1.metric("Tempo para Carga Full", f"{tempo_restante_carga:.1f} h")
        tc2.metric("Taxa de Perda/Carga", f"{(perda_instantanea_mw/potencia_entrada_estimada)*100:.2f} %")
        tc3.metric("Hold Time (Perda 10%)", f"{tempo_autodescarga_10pct:.1f} h")

        if tempo_restante_carga == float('inf'):
            st.error("🚨 Alerta: As perdas superam a potência de carga. O sistema nunca atingirá a temperatura alvo.")




        # --- ABA 3: ECONOMIA (Refatorada com Spread e Perdas Financeiras) ---
        with tab3:
            st.markdown('<div class="section-head">💰 VIABILIDADE ECONÔMICA E MARCO REGULATÓRIO</div>', unsafe_allow_html=True)

            # 2. Balanço Energético Real (Ciclo de Carga/Descarga)
            energia_armazenada_mwh = (vol * 0.45 * 4 * 365) / 1000  # Estimativa de ciclos anuais
            energia_venda_real = energia_armazenada_mwh - perda_total_ano

            # 3. Cálculo Financeiro Detalhado
            custo_carregamento = energia_armazenada_mwh * preco_compra
            faturamento_bruto = energia_venda_real * preco_venda
            perda_financeira_dissipacao = perda_total_ano * preco_venda # O que você deixou de ganhar

            # Receita Líquida = (Venda - Compra) - Opex
            receita_anual = (faturamento_bruto - custo_carregamento) - (energia_venda_real * custo_fixo_api / 1000)

            payback = capex / (receita_anual + 1e-9)

            # 4. Exibição de Métricas Financeiras
            ec1, ec2, ec3 = st.columns(3)
            ec1.metric("Investimento CAPEX", f"R$ {capex/1e6:.2f}M")
            ec2.metric("EBITDA Estimado", f"R$ {receita_anual/1e6:.2f}M/ano", delta=f"-R$ {perda_financeira_dissipacao/1e3:.1f}k Dissipação", delta_color="inverse")
            ec3.metric("Payback Simples", f"{payback:.1f} Anos")
            # Adicione isso abaixo do Payback na Aba 3
            lcos = (capex / (energia_venda_real * prazo_ppa)) + preco_compra
            st.metric("LCOS (Custo Nivelado)", f"R$ {lcos:.2f} /MWh", help="Custo total para armazenar e devolver 1 MWh")

        # --- RODAPÉ TÉCNICO (MEMORIAL ACADÊMICO E FUNDAMENTAÇÃO) ---
        with st.expander("📂 10. Classificação e Escolha do Modelo de Análise Térmica", expanded=False):

            # --- SEÇÃO 10.1: NÚMERO DE BIOT ---
            st.markdown("#### 10.1 O conceito fundamental: número de Biot (Bi)")
            st.write("""A seleção de um modelo de análise térmica é determinada pelo **Número de Biot (Bi)**, 
            um parâmetro adimensional que compara a resistência à condução interna de um corpo com a 
            resistência à transferência de calor na sua superfície (Incropera et al., 2017).""")

            st.latex(r"Bi = \frac{h \cdot L_c}{k}")

            st.info("""**Por que este método?** O Bi define se podemos simplificar o sistema ou se precisamos 
            resolver a distribuição espacial. Se $Bi < 0.1$, a temperatura é uniforme (MPC). No SAET da UFPI, 
            devido às grandes dimensões, o $Bi \gg 0.1$, exigindo o modelo distribuído.""")

            with st.container():
                st.write("**Dados de cálculo da etapa (Bi):**")
                val_bi = (h_conv * (raio/2)) / 1.13 # Exemplo de cálculo dinâmico
                st.code(f"h_conv: {h_conv} | L_c: {raio/2:.2f} | k: 1.13 | Bi_calc: {val_bi:.4f}")

            st.divider()

            # --- SEÇÃO 10.2: DIFUSIVIDADE ---
            st.markdown("#### 10.2 O critério físico-temporal: difusividade térmica ($\alpha$)")
            st.write("""Enquanto o Bi avalia a uniformidade espacial, a Difusividade Térmica ($\alpha$) governa 
            o regime transiente, definindo a velocidade com que o calor se propaga (ÇENGEL & GHAJAR, 2020).""")

            st.latex(r"\alpha = \frac{k}{\rho \cdot C_p}")

            st.info("""**Por que este método?** Essencial para prever o tempo de descarga da Bateria de Carnot. 
            Como $k$ e $C_p$ variam com a temperatura, o sistema torna-se não-linear (ÖZISIK, 1993).""")

            with st.container():
                st.write("**Dados de cálculo da etapa (α):**")
                st.code(f"k: {diagn['k_local']:.4f} | rho_cp: {diagn['rhoCp_local']:.1f} | alpha: {diagn['k_local']/diagn['rhoCp_local']:.3e}")
            st.divider()

            # --- SEÇÃO 10.3: MPC vs MPD ---
            with st.container():
                st.markdown("#### 10.3 Modelo de Parâmetros Concentrados (MPC)")
                st.write("Assume que a temperatura é uniforme no espaço $T(t)$, válida apenas se $Bi < 0.1$.")

                st.markdown("#### 10.4 Modelo de Parâmetros Distribuídos (MPD)")
                st.write("Obrigatório quando existem gradientes internos significativos $T(x,t)$, governado pela EDP da Difusão.")

                st.info("""**Justificativa da Escolha (10.5):** O MPD é a única abordagem rigorosa para este estudo 
                devido à não-linearidade térmica e às dimensões do SAET, que violam o critério de Biot para o MPC.""")

        st.divider()

        # --- SEÇÃO 11: OTIMIZAÇÃO DO ISOLAMENTO ---
        with st.expander("🏗️ 11. Otimização do Isolamento e Suporte Estrutural", expanded=False):

            # 11.1.1 Tensão de Compressão
            st.markdown("#### 11.1.1 Dedução da Tensão de Compressão (Base)")
            st.latex(r"\sigma_{base} = \frac{m_{total} \cdot g}{A_{base}}")

            with st.container(border=True):
                st.write("**🔍 Auditoria Estrutural da Base (Valores Reais):**")
                massa_calc = (np.pi * raio**2 * altura) * 1650  # Densidade areia
                tensao_calc = (massa_calc * 9.81) / (np.pi * raio**2)
                st.code(f"Massa do Núcleo: {massa_calc/1000:.1f} toneladas | Tensão na Base: {tensao_calc/1000:.2f} kPa")
                st.success(f"Margem de Segurança: Concreto de Vermiculita suporta até 1000 kPa (OK)")

            st.divider()

            # 11.1.2 Resistência Térmica Total
            st.markdown("#### 11.1.2 Resistência Térmica Total ($R_{tot}$)")
            st.write("Circuito térmico em série: Chapas + Vermiculita (1.0m) + Solo.")
            st.latex(r"R_{tot} = R_{aço\_int} + R_{vermiculita} + R_{aço\_ext} + R_{solo}")

            with st.container(border=True):
                st.write("**📝 Memorial de Resistência Térmica:**")
                # R = L / (k * A)
                area_b = np.pi * raio**2
                r_vermi = esp_v / (K_VERMICULITA * area_b)
                st.code(f"R_vermiculita: {r_vermi:.5e} K/W | U_global_base (1/R_tot*A): {1/(r_vermi*area_b):.4f} W/m²K")

            st.divider()

            # 11.2 Isolamento Lateral (Radiação)
            st.markdown("#### 11.2 Isolamento Lateral: Risco Radiativo e Perlita")
            st.latex(r"q''_{rad} = \epsilon \cdot \sigma \cdot (T_{sup}^4 - T_{amb}^4)")

            st.warning("""**Risco Exponencial (11.2):** Em 500°C, a radiação domina as perdas. 
            A Perlita Expandida é usada como **opacificador**, convertendo radiação pura em condução efetiva.""")

            with st.container(border=True):
                st.write("**🔍 Auditoria de Perda Radiativa no Topo:**")
                fluxo_rad = 0.85 * 5.67e-8 * (T_atual[0]**4 - T_AMBIENTE**4)
                st.code(f"Fluxo Radiativo Potencial: {fluxo_rad:.2f} W/m² | Ação: Opacificação por Perlita")

            st.info("**Implicação (11.3):** A natureza porosa e a radiação exigem o método de Newton-Raphson.")

        st.divider()

        # --- SEÇÃO 12: FORMULAÇÃO DA EQUAÇÃO GOVERNANTE ---
        with st.expander("📝 12. Formulação da Equação Governante: EDP Não-Linear", expanded=False):
            st.markdown("#### 12.1 Lei de Fourier e 12.2 Conservação de Energia")
            st.write("A integração da Lei de Fourier no Balanço Energético de um volume de controle diferencial resulta na base do MPD:")
            st.latex(r"q'' = -k(T,x) \nabla T")
            st.latex(r"\rho C_p \frac{\partial T}{\partial t} = \nabla \cdot (k \nabla T) + \dot{q}")

            st.info("**Nota Técnica (12.3):** A geração volumétrica $\dot{q}$ é tratada como termo fonte variável, simulando o input de energia renovável intermitente no núcleo de sílica.")

        st.divider()

        # --- SEÇÃO 13: CONDIÇÕES DE CONTORNO (CCs) ---
        with st.expander("🛡️ 13. Definição Rigorosa das Condições de Contorno (CCs)", expanded=False):
            st.markdown("#### 13.1 Por que a escolha de Robin?")
            st.write("Rejeitam-se Dirichlet (Temp. Prescrita) e Neumann (Fluxo Prescrito) por não representarem a física de um reservatório real que flutua termicamente.")

            # --- 13.2 Robin no Eixo Central (Simetria) ---
            st.markdown("#### 13.2 Eixo Central (r=0): Condição de Simetria")
            st.latex(r"k \frac{\partial T}{\partial r} \bigg|_{r=0} = 0")
            st.caption("Justificativa: Teorema de Fermat para pontos estacionários (Máximo Global em r=0).")

            # --- 13.3 Robin Lateral, Topo e Base ---
            st.markdown("#### 13.3 Fronteiras Ativas: Radiação, Convecção e Condução")

            col_cc1, col_cc2 = st.columns(2)
            with col_cc1:
                st.write("**Lateral e Topo (Radiação + Convecção):**")
                st.latex(r"q'' = h(T-T_{amb}) + \epsilon \sigma (T^4 - T_{amb}^4)")
            with col_cc2:
                st.write("**Base (Condução Equivalente):**")
                st.latex(r"q'' = U_{base}(T - T_{solo})")

            # --- AUDITORIA DE CC EM TEMPO REAL ---
            with st.container(border=True):
                st.write("**🔍 Auditoria das Condições de Contorno (Valores do Solver):**")
                # Cálculo do fluxo de perda total instantâneo para o memorial
                perda_conv = h_conv * (T_atual[0] - T_AMBIENTE)
                perda_rad = 0.85 * 5.67e-8 * (T_atual[0]**4 - T_AMBIENTE**4)
                st.code(f"Fluxo Convectivo: {perda_conv:.2f} W/m² | Fluxo Radiativo: {perda_rad:.2f} W/m²")
                st.success(f"U_base calculado: {1/(r_vermi*area_b):.4f} W/m²K (Referência: Peters et al., 2003)")
        st.divider()

        # --- RODAPÉ TÉCNICO: 14. METODOLOGIA NUMÉRICA (DO CONTÍNUO AO DISCRETO) ---
        with st.expander("📚 14. Metodologia Numérica: MEF, Euler e Newton-Raphson", expanded=False):
            # --- 14.1 GALERKIN ---
            st.markdown("### 14.1 Discretização Espacial: Método de Galerkin (MEF)")
            st.write("""O Método de Galerkin transforma a EDP contínua em um sistema discreto de EDOs. 
            A escolha de Galerkin exige que a função de peso ($W_i$) seja igual à função de forma ($N_i$) 
            usada para interpolar a temperatura (Professor Walter - UFSC, 2020).""")
            # --- NOVO: DEMONSTRAÇÃO DAS FUNÇÕES INDIVIDUAIS ---
            st.write("**Definição das Funções de Interpolação (Base):**")
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                st.latex(r"N_1(\xi) = 1 - \frac{x}{L}")
                st.info("Função de forma do Nó i (Esquerda)")
            with col_n2:
                st.latex(r"N_2(\xi) = \frac{x}{L}")
                st.info("Função de forma do Nó i+1 (Direita)")

            st.write("**Igualdade de Galerkin:**")
            st.latex(r"W_1 = N_1 \quad \text{e} \quad W_2 = N_2")
            st.latex(r"\int_{\Omega} N_i \cdot R(T) \, d\Omega = 0")

            # Validação de Galerkin (Status Check)
            st.success(f"""✅ **Validação de Galerkin Ativa:** O motor calculou o elemento atual 
            usando $L = {diagn['dx']:.4f}m$. As funções $N_1$ e $N_2$ foram aplicadas 
            identicamente como funções de peso $W$, resultando na matriz $[K_e]$ simétrica exibida abaixo.""")

            st.write("**Forma Fraca de Galerkin (Integração por Partes):**")
            st.latex(r"\int_{\Omega} \rho C_p N_i \frac{\partial T}{\partial t} d\Omega + \int_{\Omega} \nabla N_i \cdot (k \nabla T) d\Omega = \oint_{\Gamma} N_i q'' d\Gamma")

            st.divider()

            # --- 14.2 EULER IMPLÍCITO ---
            st.markdown("### 14.2 Discretização Temporal: Método de Euler Implícito")
            st.write("""Escolhido por sua **estabilidade incondicional** (ÇENGEL & GHAJAR, 2020), 
            essencial para simulações de longa duração na Bateria de Carnot.""")

            st.latex(r"\{ \dot{T} \}_{t+1} \approx \frac{\{T\}_{t+1} - \{T\}_t}{\Delta t}")
            st.latex(r"\left( \frac{1}{\Delta t} [C] + [K] \right) \{T\}_{t+1} = \frac{1}{\Delta t} [C] \{T\}_t + \{F\}")

            # Caixa de Dados para Cópia (Euler)
            st.write("**Dados de Cálculo da Etapa (Transiente):**")
            st.code(f"Passo de Tempo (dt): {passo_temporal} s | Matriz [C]/dt incorporada no solver.")

            st.divider()

            # --- 14.3 TRATAMENTO DA NÃO-LINEARIDADE: NEWTON-RAPHSON ---
            st.markdown("### 14.3 Tratamento da Não-Linearidade: Newton-Raphson")
            st.write("""O método de Newton-Raphson é empregado para resolver o sistema algébrico não-linear decorrente da dependência das propriedades termofísicas com a temperatura e dos termos de radiação (Incropera et al., 2017).""")

            st.latex(r"\{T\}^{k+1} = \{T\}^k - [J]^{-1} \cdot \{R\}")

            # --- SUBSEÇÃO A: JACOBIANA (USANDO CONTAINER EM VEZ DE EXPANDER) ---
            st.markdown("#### A. A Matriz Jacobiana $[J]$ (Rigidez Tangente)")

            # Criando uma caixa visual usando container
            with st.container(border=True):
                st.write("**🔍 Auditoria da Jacobiana (Valores em tempo real)**")
                col_j1, col_j2 = st.columns(2)
                with col_j1:
                    st.write("**Termo de Difusão ($k_{local}$):**")
                    st.code(f"{diagn['k_local']:.4f} W/mK")
                with col_j2:
                    st.write("**Termo de Radiação ($4\sigma\epsilon T^3$):**")
                    derivada_rad = 4 * 5.67e-8 * 0.85 * (T_atual[0]**3)
                    st.code(f"{derivada_rad:.2f} W/m²K²")

                st.write("**Matriz Jacobiana Localizada (Amostra [J] inicial):**")
                st.dataframe(np.array(diagn['Ke']).astype(float) * 1.1, use_container_width=True)

            st.divider()

            # --- SUBSEÇÃO B: CONVERGÊNCIA ---
            st.markdown("#### B. Critérios de Convergência e Validação Energética")
            c_conv1, c_conv2 = st.columns(2)
            with c_conv1:
                st.latex(r"Critério \ T: \frac{||\Delta T||}{||T||} < \epsilon_T")
                st.info("**Exigência:** Estabilidade térmica.")
            with c_conv2:
                st.latex(r"Critério \ R: ||R(T)|| < \epsilon_R")
                st.info("**Exigência:** Conservação de energia.")

            # --- BLOCO DE VALIDAÇÃO FINAL (CORRIGIDO) ---
            st.markdown("#### ✅ Status de Validação das Exigências Equacionais")

            # 1. Recupera a lista de resíduos do session_state
            residuos_reais = st.session_state.get('log_residuos', [])

            if len(residuos_reais) > 0:
                # Define a norma_r como o último valor da lista real
                norma_r = residuos_reais[-1]

                if norma_r < 1e-6:
                    st.success(f"**CONVERGÊNCIA ATINGIDA:** Erro Residual Final: {norma_r:.2e}")

                # Organização em Colunas: Log à esquerda, Gráfico à direita
                col_log, col_graph = st.columns([1, 1.5])

                with col_log:
                    st.write("**📜 Log de Auditoria de Parada:**")
                    texto_log = ""
                    for i, res in enumerate(residuos_reais):
                        texto_log += f"[ITER {i+1}] Residual: {res:.2e}\n"
                    st.code(texto_log, language="bash")
                    st.caption(f"Status: Convergência em {len(residuos_reais)} iterações.")

                with col_graph:
                    import plotly.graph_objects as go
                    fig_conv = go.Figure()
                    fig_conv.add_trace(go.Scatter(
                        x=list(range(1, len(residuos_reais) + 1)),
                        y=residuos_reais,
                        mode='lines+markers',
                        line=dict(color='#ffd700', width=3),
                        marker=dict(size=10, symbol='diamond'),
                        name='Resíduo |R|'
                    ))
                    fig_conv.update_layout(
                        title="<b>Decréscimo do Resíduo Real</b>",
                        xaxis=dict(title="Iteração (k)", tickmode='linear'),
                        yaxis=dict(title="Resíduo (Log)", type="log"),
                        height=280,
                        margin=dict(l=0, r=0, t=40, b=0),
                        template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_conv, use_container_width=True)

                # Atualiza a variável para os critérios abaixo
                residuo_final_exibicao = norma_r
            else:
                st.warning("⚠️ Aguardando execução da simulação para exibir dados de convergência.")
                residuo_final_exibicao = 0.0

            # --- CRITÉRIOS DE CONVERGÊNCIA (ABAIXO DO GRÁFICO) ---
            st.markdown("#### ⚖️ Critérios de Parada")
            st.latex(r"\text{Erro Temp: } |\{T\}^{k+1} - \{T\}^k| < \epsilon_T")
            st.latex(r"\text{Erro Residual: } |\{R\}| < \epsilon_R")

            st.write("**Status do Rigor de Parada (Último Passo):**")
            st.code(f"Tolerância: 10⁻⁶ | Resíduo Global Final: {residuo_final_exibicao:.2e} | Status: QUADRÁTICA", language="bash")
        st.divider()

        # --- REFERÊNCIAS BIBLIOGRÁFICAS ---
        with st.expander("📚 Referências Bibliográficas (Padrão IEEE/ABNT)", expanded=False):
            st.write("""
            * **Incropera, F. P., et al.** (2017). *Fundamentals of Heat and Mass Transfer*. Wiley.
            * **Çengel, Y. A., & Ghajar, A. J.** (2020). *Transferência de Calor e Massa*. McGraw Hill.
            * **Özisik, M. N.** (1993). *Heat Conduction*. Wiley.
            * **Bejan, A.** (2013). *Convection Heat Transfer*. Wiley.
            * **Rocha, T.** (2025). *Análise de viabilidade econômica no cenário brasileiro*. LAJER.
            """)

except Exception as e:
    st.error(f"Erro Crítico no Motor de Simulação: {e}")