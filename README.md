# 💧 Sanova Analytics - Gestão Comercial e Mitigação de Perdas

**🔗 [Acesse o Dashboard Interativo Aqui](https://seu-app-saneamento.streamlit.app)** 

---

## 🎯 Resumo Executivo
Este projeto é uma solução analítica focada em **resultados operacionais e aumento de receita** para o setor de saneamento. Indo além da simples visualização de dados, a aplicação identifica ativamente gargalos comerciais, cruza inconsistências de faturamento e gera um **Plano de Ação priorizado por Payback**, indicando exatamente onde a concessionária deve alocar suas equipes de campo para obter o retorno financeiro mais rápido.

---

## 📖 O Desafio & A Abordagem Estratégica
O escopo do desafio sugeria o uso de ferramentas tradicionais de BI (como o Power BI). No entanto, para resolver este estudo de caso de micromedição com foco no futuro da operação, decidi arquitetar uma aplicação interativa e escalável estruturada inteiramente em **Python, Pandas e Streamlit**. 

Esta decisão técnica reflete uma decisão de negócios:
1. **Flexibilidade Analítica:** Ferramentas de BI tradicionais são excelentes para relatórios consolidados, mas possuem limites de customização e licenciamento. O ecossistema Python oferece flexibilidade total para manipulação de dados em larga escala e redução do tempo de análise operacional.
2. **Arquitetura Pronta para IA e Machine Learning:** Ao estruturar o *pipeline* e o dashboard em Python, o ecossistema abandona o formato engessado de relatórios estáticos e se torna um ambiente dinâmico. O terreno já está nativamente preparado para integrar modelos preditivos (como detecção de fraudes em tempo real via Machine Learning) ou Agentes de IA (LLMs) para consultas operacionais diretas. 

O objetivo primário desta análise não é apenas plotar gráficos, mas sim transformar dados brutos em **decisões estratégicas e métricas de impacto financeiro**.

---

## 📊 Regras de Negócio e Detecção de Anomalias
Para garantir a recuperação de receitas e a mitigação de perdas, os dados foram submetidos a regras de negócio rigorosas para identificar:

1. **Hidrômetro Parado**: Ligação ATIVA que possui Volume Lido igual a 0.
2. **Possível Clandestina ("Gato")**: Ligação INATIVA/CORTADA que ainda assim registra Volume Lido maior que 0.
3. **Anomalia de Categoria**: Ligações com categoria RESIDENCIAL, mas com consumos elevadíssimos (acima de 50m³), indicando possível uso COMERCIAL clandestino.
4. **Incongruência de Esgoto**: Ligações com taxa de esgoto ATIVA, porém com água INATIVA. Indica que o cliente está gerando efluentes provenientes de fontes alternativas (ou irregulares) de água, devendo ser tarifado adequadamente.

## 💡 Metodologia de Cálculo de ROI e Payback
Para garantir que as ações propostas sejam viáveis e tragam retorno rápido, as seguintes premissas operacionais foram modeladas (e podem ser simuladas dinamicamente no painel):

*   **Custo de Troca de Hidrômetro**: R$ 150,00 por ordem de serviço.
*   **Custo de Inspeção de Fraude**: R$ 100,00 por deslocamento/fiscalização da equipe de campo.
*   **Tarifa Média Estimada**: Calculada de forma dinâmica (`VALOR_AGUA / VOLUME_FATURADO`) com base na base de clientes pagantes.
*   **Consumo Saudável Estimado**: Para calcular o volume financeiro "perdido" em irregularidades (como hidrômetros parados e incongruências de esgoto), estimou-se um consumo basal conservador de 15m³.

## 🛠️ Stack Tecnológica
*   **Linguagem & Lógica**: Python
*   **Tratamento e Modelagem de Dados**: Pandas
*   **Desenvolvimento da Interface (UI)**: Streamlit
*   **Visualização de Dados**: Plotly Express e Graph Objects

## 🚀 Como Executar o Projeto Localmente

1. Certifique-se de possuir o Python instalado (recomendado Python 3.10 ou superior).
2. Instale as bibliotecas necessárias presentes no `requirements.txt`:
```bash
pip install -r requirements.txt
```
3. Execute o dashboard via Streamlit:
```bash
streamlit run app.py
```

## 📈 Conclusão Estratégica
O painel foi desenhado não apenas para mostrar gráficos, mas para gerar **insights acionáveis**. A aba "Plano de Ação e Payback" cruza o custo de operação com os ganhos potenciais mensais previstos, orientando a tomada de decisão da gestão para alocar as equipes de campo nas frentes de maior e mais rápido retorno (ROI).
