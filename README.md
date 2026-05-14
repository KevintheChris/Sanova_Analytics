# 💧 Sanova Analytics - Plataforma de Gestão Comercial e Mitigação de Perdas

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-2.x-150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/)

**🔗 [Acesse o Dashboard Interativo Aqui](https://sanovaanalytics-gfmappnrr9.streamlit.app/)** 

---

## 🎯 Resumo Executivo
O **Sanova Analytics** é uma solução de inteligência de dados desenvolvida para o setor de saneamento, com foco na **recuperação de receitas e redução de perdas comerciais**. Utilizando análise de dados avançada, a aplicação cruza faturamentos, consumos históricos e dados cadastrais para identificar anomalias, possíveis fraudes e ineficiências operacionais. 

O diferencial desta ferramenta é a sua capacidade de **ir além da visualização de dados**, gerando automaticamente um **Plano de Ação priorizado pelo tempo de Retorno sobre Investimento (Payback)**, permitindo que as equipes de campo sejam direcionadas para as frentes mais lucrativas primeiro.

---

## 📖 O Desafio & A Abordagem Estratégica
Para resolver este estudo de caso de micromedição, optei por desenvolver uma aplicação interativa e escalável estruturada inteiramente em **Python, Pandas e Streamlit**, em vez de utilizar ferramentas tradicionais de BI (como Power BI ou Tableau).

A escolha arquitetural reflete o direcionamento da nova fase do mercado de dados:
1. **Flexibilidade Analítica:** Ferramentas de BI possuem limitações em customizações estatísticas complexas. A stack em Python proporciona flexibilidade total para limpeza avançada, regras de negócio encadeadas e automação.
2. **Integração Nativa com Inteligência Artificial:** Ao estruturar o pipeline em Python, o ecossistema fica imediatamente preparado para acoplar modelos preditivos de *Machine Learning* (ex: prever risco de fraude por clusterização) e Agentes de IA Generativa para consulta em linguagem natural. Em um sistema BI fechado, essa transição seria engessada e cara.

---

## 📊 Regras de Negócio e Anomalias Detectadas
A inteligência do sistema baseia-se na detecção automatizada das seguintes ocorrências:

1. 🛑 **Hidrômetro Parado (Submedição):** Ligação ATIVA que possui Volume Lido igual a 0, mas com faturamento. Indica medidor travado ou danificado.
2. ⚠️ **Possível Clandestina ("Gato"):** Ligação INATIVA ou CORTADA que ainda assim registra Volume Lido maior que 0.
3. 🏢 **Anomalia de Categoria:** Ligações com categoria RESIDENCIAL, mas com consumos muito elevados (acima de 50m³), indicando possível uso COMERCIAL (república, pequeno comércio disfarçado).
4. 🚽 **Incongruência de Esgoto:** Ligações com taxa de esgoto ATIVA, porém com água INATIVA. Indica que o cliente pode estar gerando efluentes provindos de fontes alternativas (poços artesianos irregulares) ou ligações clandestinas de água.

> 💡 **Próxima Evolução (Roadmap):** *Implementação de regras para **Idade do Hidrômetro** (substituição preventiva para evitar submedição por depreciação técnica) e **Queda Brusca de Consumo** (comparação com a média histórica dos últimos 12 meses).*

---

## 💰 Cálculo de ROI e Priorização de Ações
Para entregar valor real ao negócio, o dashboard não apenas aponta o problema, mas **calcula a viabilidade financeira da solução**. As seguintes premissas (ajustáveis na ferramenta) são adotadas:

- **Custo Operacional:** Custo estimado de troca de hidrômetro (R$ 150) e taxa de deslocamento/inspeção (R$ 100).
- **Tarifa Média Dinâmica:** Calculada automaticamente pela relação `Valor Água / Volume Faturado` da base de clientes adimplentes.
- **Consumo Basal:** Estimativa de 15m³ para calcular o volume "perdido" em irregularidades não medidas.

O sistema cruza o **Custo da Ação** com o **Ganho Mensal Estimado** e ordena as ordens de serviço pelo **Payback (em meses)**, maximizando a eficiência da operação.

---

## 🛠️ Tecnologias Utilizadas
- **Linguagem**: Python 3.10+
- **Processamento de Dados**: Pandas & NumPy
- **Frontend & UI**: Streamlit
- **Visualização de Dados**: Plotly Express & Graph Objects

---

## 🚀 Como Executar Localmente

1. Clone este repositório e acesse a pasta do projeto.
2. Recomenda-se a criação de um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. Instale as dependências listadas no `requirements.txt`:
```bash
pip install -r requirements.txt
```
4. Execute a aplicação web:
```bash
streamlit run app.py
```
