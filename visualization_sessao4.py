def obter_resumo_academico(escala):
    """
    SESSÃO 4: BASE DE CONHECIMENTO E FUNDAMENTAÇÃO
    Centraliza as justificativas teóricas para cada escala de análise.
    """
    resumos = {
        "termogeometria": (
            "Escala Macro: Gêmeo Digital fatiado em 270°. Utiliza um motor de Elementos Finitos (MEF) "
            "com solução transiente via Newton-Raphson para prever a evolução do campo térmico "
            "em meios granulares (Areia/Grafite)."
        ),
        "blindagem": (
            "Escala de Segurança: Memorial de Cálculo de resistências térmicas série-paralelo. "
            "Analisa independentemente as perdas para o solo e para a atmosfera, validando o projeto "
            "frente à norma NR-12 (Limite de 60°C para contato humano)."
        ),
        "materiais": (
            "Escala Micro: Análise de limites termomecânicos. Avalia a estabilidade das ligas metálicas "
            "(SS-316H e Inconel 617) sob condições de fluência e estresse térmico cíclico."
        ),
        "ppa": (
            "Escala Econômica: Viabilidade baseada no Novo Marco Regulatório (Lei 15.269/2025). "
            "Calcula o Stack de Receitas via Arbitragem de PLD e Leilão de Reserva de Capacidade (LRC)."
        )
    }
    return resumos.get(escala, "Informação não disponível para esta escala.")

def obter_memorial_formulas():
    """Retorna as fórmulas principais para exibição no Dashboard."""
    formulas = {
        "conducao": r"q = -k \cdot \nabla T",
        "conveccao": r"q = h(T_{casca} - T_{amb})",
        "payback": r"Payback = \frac{CAPEX}{Receita_{liq} - OPEX}"
    }
    return formulas
