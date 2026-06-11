import numpy as np

# ==============================================================================
# MÓDULO 1: DADOS DE ENTRADA (FÍSICA, MATERIAIS E ECONOMIA)
# Ref: Otimização Multiescala de Baterias de Carnot (sCO2)
# ==============================================================================

# ============== 1. PARÂMETROS DO SOLUCIONADOR (MEF / NEWTON-RAPHSON) ==============
TEMPO_PASSO = 1.0        # Delta t (s) - Ajustado para a inércia térmica de armazenamento longo
TOLERANCIA_NEWTON = 1e-6 # Epsilon - Critério rigoroso de convergência do resíduo
MAX_ITERACOES = 50       # Número máximo de iterações por passo no domínio do tempo

# ============== 2. CONSTANTES FÍSICAS E CONDIÇÕES DE CONTORNO (PIAUÍ) ==============
T_AMBIENTE = 311.15      # 38°C em Kelvin (Refletindo o clima de Teresina-PI para perdas)
COEF_CONVECCAO = 10.0    # h_res [W/m²K] - Convecção natural na casca externa do tanque
STEFAN_BOLTZMANN = 5.670373e-8 # Constante de Stefan-Boltzmann [W/m²K⁴]
EMISSIVIDADE = 0.85      # Epsilon para superfícies metálicas oxidadas ou pintadas

# ============== 3. PROPRIEDADES DE BLINDAGEM TÉRMICA (ISOLANTES) ==============
# Valores calibrados conforme Seção 11.1.2 e Mordor Intelligence (2025)
K_PERLITA = 0.045        # [W/mK] (Inalterado - Correto conforme Incropera)
K_VERMICULITA = 0.08     # [W/mK] (AJUSTADO: Conforme seu texto da Seção 11.1.2)
K_SOLO = 0.5             # [W/mK] (AJUSTADO: Conforme referência Euronem no seu texto)
T_SOLO = 293.15          #  20°C em Kelvin


# ============== 4. LIMITES TERMOMECÂNICOS E CUSTOS (MESO E MACROESCALA) ==============
# Dados para cálculo de falha de fluência (creep) e impacto no CAPEX
LIMITES_ACO = {
    "SS-316H": {
        "T_max": 823.15,      # Limite seguro de operação (aprox. 550°C)
        "Custo_Base": 1.0     # Fator de custo normalizado de referência
    },
    "Inconel 617": {
        "T_max": 1223.15,     # Suporta ciclos supercríticos sCO2 até 950°C
        "Custo_Base": 4.5     # Elevado custo de investimento (Reflete no LCOE)
    }
}

# ============== 2. BANCO DE DADOS UNIFICADO ==============
# Aqui estão todos os seus materiais. Se quiser adicionar outro, basta uma linha aqui.
BANCO_MATERIAIS = {
    "Areia de Sílica": {
        "rho": 1650.0, "cp0": 700.0, "beta": 0.4, "k0": 0.5,
        "alpha": 0.0008, "trans": True, "t_limite": 1500.0, "ativo": False
    },
    "Grafite":         {
        "rho": 1700.0, "cp0": 710.0, "beta": 0.3, "k0": 25.0,
        "alpha": -0.01, "trans": False, "t_limite": 450.0, "ativo": True
    },
    "Hematita": {
        "rho": 3120.0, "cp0": 650.0, "beta": 0.2, "k0": 1.2,
        "alpha": 0.0005, "trans": False, "t_limite": 1200.0, "ativo": False
    },
    "Alumina": {
        "rho": 2380.0, "cp0": 880.0, "beta": 0.25, "k0": 3.5,
        "alpha": 0.0003, "trans": False, "t_limite": 1600.0, "ativo": False
    },
    "Carbonato de Cálcio": {
        "rho": 1630.0, "cp0": 820.0, "beta": 0.25, "k0": 1.5,
        "alpha": 0.0004, "trans": False, "t_limite": 700.0, "ativo": True
    }
}

# Esta variável deve ser setada pelo app.py
MATERIAL_SELECIONADO = "Areia de Sílica"

# ============== FUNÇÕES DINÂMICAS ==============
def condutividade_termica(T):
    mat = BANCO_MATERIAIS[MATERIAL_SELECIONADO]
    return mat["k0"] + mat["alpha"] * T

def calor_especifico_rho(T):
    mat = BANCO_MATERIAIS[MATERIAL_SELECIONADO]
    return mat["rho"] * (mat["cp0"] + mat["beta"] * T)

def derivada_propriedades_material(T):
    mat = BANCO_MATERIAIS[MATERIAL_SELECIONADO]
    return mat["alpha"], mat["rho"] * mat["beta"]


# ============== 6. PARÂMETROS DE TRANSIÇÃO DE FASE (QUARTZO/SÍLICA) ==============
T_INVERSAO_QUARTZO = 846.15  # 573°C (Ponto crítico de transição Alpha -> Beta)
DILATACAO_VOL_BETA = 0.045   # 4.5% de aumento volumétrico permanente na fase Beta
RESISTENCIA_VERMICULITA_KPA = 1000.0 # Limite de compressão conforme Seção 11.1.1