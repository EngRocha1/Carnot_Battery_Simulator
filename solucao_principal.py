import numpy as np
from scipy.sparse.linalg import spsolve
from dados_entrada import *
from mef_montagem import calcula_residuos_e_jacobiana, monta_matrizes_globais

class EstruturaMalha:
    """
    Representação topológica da malha de Elementos Finitos 1D.
    Reflete o eixo vertical/profundidade do núcleo de armazenamento.
    """
    def __init__(self, num_nos):
        self.num_nos = num_nos
        # Nós de fronteira: 0 (Topo/Carga sCO2) e num_nos - 1 (Fundo/Solo)
        self.nos_fronteira = [0, num_nos - 1]

    def e_no_de_contorno(self, i):
        return i in self.nos_fronteira

    def area_associada(self, i):
        return 1.0

def simular_difusao_termica(T_inicial, tempo_total, dt, esp_p, esp_v, h_conv, T_amb, T_solo, k_solo):
    """
    Motor de cálculo original PRESERVADO, apenas com adição da lista de resíduos
    para alimentar o gráfico dinâmico de convergência.
    """
    # Mantém sua lógica de dt original
    passo_h = dt if dt is not None else TEMPO_PASSO

    M_global = EstruturaMalha(len(T_inicial))
    T_passado = np.copy(T_inicial)
    T_carga_fixa = T_inicial[0]

    tempos_simulados = np.arange(0, tempo_total + passo_h, passo_h)
    resultados_simulacao = []

    # NOVA VARIÁVEL: Apenas para carregar os dados para a UI
    historico_convergencia = []

    for t_step, tempo_atual in enumerate(tempos_simulados):
        T_futuro_k = np.copy(T_passado)
        residuos_k = [] # Lista temporária para o passo atual

        for k in range(MAX_ITERACOES):
            K_global, C_global = monta_matrizes_globais(T_futuro_k, M_global.num_nos)

            # Mantém sua chamada com os 9 argumentos exatamente como está
            R_vetor, J_matriz = calcula_residuos_e_jacobiana(
                T_futuro_k, T_passado, K_global, C_global, M_global,
                passo_h, esp_p, esp_v, h_conv, T_amb, T_solo, k_solo
            )

            J_matriz[0, :] = 0.0
            J_matriz[0, 0] = 1.0
            R_vetor[0] = 0.0

            # 3. Verificação de Convergência (Sua lógica original)
            norma_residuos = np.linalg.norm(R_vetor)
            residuos_k.append(norma_residuos) # Captura sem alterar o fluxo

            if norma_residuos < TOLERANCIA_NEWTON:
                # Salva o log do último passo para o Dashboard antes de sair do loop
                historico_convergencia = residuos_k
                break

            try:
                vetor_correcao = spsolve(J_matriz.tocsr(), -R_vetor)
            except Exception:
                raise RuntimeError(f"Falha na inversão da Matriz Jacobiana no t={tempo_atual}s.")

            T_futuro_k += vetor_correcao
            T_futuro_k[0] = T_carga_fixa
        else:
            raise ValueError(f"O algoritmo de Newton-Raphson não convergiu após {MAX_ITERACOES} iterações.")

        T_passado = np.copy(T_futuro_k)
        resultados_simulacao.append(np.copy(T_passado))

    # O ÚNICO ajuste na assinatura de retorno para o Dashboard funcionar:
    return resultados_simulacao, M_global, historico_convergencia