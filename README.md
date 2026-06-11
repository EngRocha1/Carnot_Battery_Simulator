# ⚡ Carnot Battery Multiescala (Gêmeo Digital)

Este projeto apresenta um **Gêmeo Digital** para análise térmica e econômica de Sistemas de Armazenamento de Energia Térmica (SAET), tecnicamente conhecidos como **Baterias de Carnot**.

O sistema utiliza modelagem de **Elementos Finitos (MEF)** transiente para prever o comportamento térmico em meios granulares e avaliar sua viabilidade financeira sob o novo **Marco Regulatório de Armazenamento no Brasil** (Lei 15.269/2025).


## 🔬 Fundamentação Científica

O motor de cálculo utiliza o **Método de Galerkin (MEF)** para discretização espacial e o esquema de **Euler Implícito** para a evolução temporal. A Equação Diferencial Parcial (EDP) de difusão não-linear é resolvida numericamente através do algoritmo iterativo de **Newton-Raphson**, garantindo estabilidade numérica e precisão quadrática na convergência das temperaturas nodais do sistema.



## 🛠️ Tecnologias Utilizadas

* **Backend Numérico:** `NumPy` e `SciPy` (solvers de matrizes esparsas).
* **Interface Dinâmica:** `Streamlit` para orquestração de cenários e interação em tempo real.
* **Visualização:** `Plotly` (modelagem 3D interativa) e `Matplotlib` (geração de memoriais técnicos).
* **Containerização:** `Docker` para garantir portabilidade e reprodutibilidade em ambientes de alta performance (HPC).

## 🚀 Como Executar

Certifique-se de ter o **Docker** instalado e configurado em sua máquina.

### 1. Build da Imagem
Execute o comando abaixo para construir o container do simulador:

#### ```bash
####    docker build -t carnotsim .

---

## 🏗️ Estrutura do Projeto

Abaixo, os principais módulos que compõem o Gêmeo Digital:

| Módulo | Descrição |
| :--- | :--- |
| `app.py` | Interface principal, *sidebars* dinâmicos e orquestração do Dashboard. |
| `mef_montagem.py` | Núcleo matemático: Jacobiana, Resíduos e montagem de matrizes (K, C). |
| `solucao_principal.py` | Motor de integração transiente e solver de Newton-Raphson. |
| `dados_entrada.py` | Banco de dados de materiais e constantes termofísicas. |
| `visualization_*.py` | Módulos especializados em memorial técnico e representação gráfica. |

---

## 🎓 Contexto Acadêmico

Projeto desenvolvido no âmbito do Programa de Pós-Graduação em Engenharia Elétrica (**PPGEE/UFPI**).

* **Pesquisador:** Tarcísio Dias da Rocha
* **Orientador:** Dr. Marcos Lira

Este software é voltado para pesquisa acadêmica e simulação de engenharia térmica aplicada a sistemas de armazenamento de energia.

---