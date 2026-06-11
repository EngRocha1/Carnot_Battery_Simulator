import numpy as np
from scipy.sparse import lil_matrix
import dados_entrada

def monta_matrizes_globais(T_nodal,
                           num_nos,
                           retorno_diagnostico=False):
    """
    Monta as matrizes globais K e C usando LIL_MATRIX para máxima performance
    """
    K_global = lil_matrix((num_nos, num_nos))
    C_global = lil_matrix((num_nos, num_nos))
    dx = 1.0 / (num_nos - 1)

    amostra_mef = {}

    for i in range(num_nos - 1):
        T_med = (T_nodal[i] + T_nodal[i+1]) / 2.0
        k_val = dados_entrada.condutividade_termica(T_med)
        cp_rho_val = dados_entrada.calor_especifico_rho(T_med)

        # Matriz de Rigidez Local [Ke] (Difusão)
        ke = (k_val / dx) * np.array([[1.0, -1.0], [-1.0, 1.0]])

        # Matriz de Capacitância Local [Ce] (Massa Consistente)
        ce = (cp_rho_val * dx / 6.0) * np.array([[2.0, 1.0], [1.0, 2.0]])

        if i == 0 and retorno_diagnostico:
            amostra_mef = {
                "Ke": ke.tolist(),
                "Ce": ce.tolist(),
                "k_local": k_val,
                "rhoCp_local": cp_rho_val,
                "dx": dx
            }

        # Assembleia Global
        for row in range(2):
            for col in range(2):
                K_global[i+row, i+col] += ke[row, col]
                C_global[i+row, i+col] += ce[row, col]

    if retorno_diagnostico:
        return K_global.tocsr(), C_global.tocsr(), amostra_mef
    return K_global.tocsr(), C_global.tocsr()

def calcula_residuos_e_jacobiana(T_k,
                                 T_passado,
                                 K_global,
                                 C_global,
                                 M_global,
                                 dt,
                                 esp_p,
                                 esp_v,
                                 h_conv,
                                 T_amb,
                                 T_solo,
                                 k_solo):

    """
    Calcula o Resíduo {R} e a Jacobiana [J] para o Newton-Raphson.
    Agora utiliza o 'dt' dinâmico vindo do slider do App.
    """
    # Matriz Secante A = [1/dt * C + K]
    # Substituído TEMPO_PASSO por dt
    A_matriz = (1.0 / dt) * C_global + K_global

    # Termo de Carga Temporal B = [1/dt * C]{T_passado}
    B_vetor = (1.0 / dt) * C_global.dot(T_passado)

    # Vetor de Carga Não-Linear (Fronteira Robin/Radiação)
    F_carga = calcula_vetor_carga_nao_linear(T_k, M_global, esp_p, esp_v, h_conv, T_amb, T_solo, k_solo)

    # Resíduo: {R} = [A]{T_k} - {B} + {F_carga}
    R_vetor = A_matriz.dot(T_k) - B_vetor + F_carga

    # Jacobiana Inicial (Baseada na matriz secante)
    J_matriz = lil_matrix(A_matriz)

    # Termo Tangente da Radiação (Derivada dR/dT para Newton-Raphson)
    for i in range(len(T_k)):
            if M_global.e_no_de_contorno(i):
                T_i = T_k[i]
                # Para MEF 1D, a área da seção transversal é assumida como 1.0
                # para ser consistente com a montagem de K_global
                area_mef = 1.0

                if i == 0: # TOPO
                    derivada_rad = 4.0 * dados_entrada.EMISSIVIDADE * dados_entrada.STEFAN_BOLTZMANN * (T_i**3) * area_mef
                    J_matriz[i, i] += derivada_rad

                elif i == len(T_k) - 1: # BASE
                    # Derivada do termo convectivo/condutivo da base
                    U_base = 1.0 / ((esp_v / dados_entrada.K_VERMICULITA) + (1.0 / k_solo))
                    J_matriz[i, i] += U_base * area_mef

    return R_vetor, J_matriz.tocsr()

def calcula_vetor_carga_nao_linear(T_nodal, M_global, esp_p, esp_v, h_conv, T_amb, T_solo, k_solo):
    """
    Monta o vetor de carga {F} aplicando as resistências da Perlita e Vermiculita.
    """
    num_nos = len(T_nodal)
    F_carga = np.zeros(num_nos)

    for i in range(num_nos):
        if M_global.e_no_de_contorno(i):
            T_i = T_nodal[i]
            area_nodal = 1.0

            if i == 0:  # TOPO/LATERAL
                U_eff = 1.0 / ((esp_p / dados_entrada.K_PERLITA) + (1.0 / h_conv))
                fluxo_rad = dados_entrada.EMISSIVIDADE * dados_entrada.STEFAN_BOLTZMANN * (T_i**4 - T_amb**4)
                fluxo_conv = U_eff * (T_i - T_amb)
                F_carga[i] += (fluxo_rad + fluxo_conv) * area_nodal

            elif i == num_nos - 1:  # BASE
                # Agora usa os valores injetados pelo usuário
                U_base = 1.0 / ((esp_v / dados_entrada.K_VERMICULITA) + (1.0 / k_solo))
                fluxo_base = U_base * (T_i - (T_solo + 273.15))
                F_carga[i] += fluxo_base * area_nodal

    return F_carga