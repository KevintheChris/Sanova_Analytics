# 💧 Sanova Analytics - Gestão Comercial e Mitigação de Perdas

**🔗 [Acesse o Dashboard Interativo Aqui](https://sanovaanalytics-gfmappnrr9.streamlit.app/)** 

---

### 📖 O Desafio & A Abordagem Estratégica (Storytelling)
Para resolver este estudo de caso de micromedição, decidi ir além das ferramentas tradicionais de relatórios corporativos (como o Power BI). Desenvolvi uma aplicação interativa e escalável estruturada inteiramente em **Python, Pandas e Streamlit**. 

O objetivo dessa escolha arquitetural reflete o direcionamento da nova fase do mercado de dados:
1. **Flexibilidade e Além do BI Tradicional:** Enquanto ferramentas de BI possuem limitações em customizações complexas e licenciamento, a stack em Python proporciona flexibilidade total para tratamento de dados, automação e escalabilidade.
2. **Integração Nativa com Inteligência Artificial:** Ao estruturar os dados e o dashboard em Python, o terreno fica imediatamente preparado para acoplar modelos preditivos de Machine Learning (para prever evasão ou fraudes em tempo real) e integrações com Agentes de IA (GenAI) para consulta de dados em linguagem natural. Essa transição seria engessada e dependente de plugins em um sistema BI fechado.

Ao analisar a base de dados, meu foco foi muito além da visualização: busquei identificar os gargalos operacionais que geram perdas aparentes e transformá-los em oportunidades financeiras reais. O dashboard foi construído para entregar **decisões**, saindo de dados brutos diretamente para Planos de Ação otimizados.

---

## 🎯 Objetivos da Análise
O dashboard tem como foco responder aos seguintes pontos do case:
1. **Identificação de oportunidades de recuperação de receitas**: Cálculo do impacto financeiro de clientes que não estão sendo cobrados adequadamente.
2. **Detecção de possíveis fraudes, inconsistências ou anomalias**: Regras aplicadas para descobrir "gatos", hidrômetros parados ou cadastros incorretos.
3. **Visibilidade Operacional**: Análise completa do parque de hidrômetros e tendências históricas de consumo.
4. **Priorização de ações**: Geração de um Plano de Ação ordenado pelo tempo de retorno financeiro (Payback).

## 📊 Regras de Negócio de Anomalias Implementadas
1. **Hidrômetro Parado**: Ligação ATIVA que possui Volume Lido igual a 0.
2. **Possível Clandestina ("Gato")**: Ligação INATIVA/CORTADA que ainda assim registra Volume Lido maior que 0.
3. **Anomalia de Categoria**: Ligações com categoria RESIDENCIAL, mas com consumos muito elevados (acima de 50m³), indicando possível uso COMERCIAL clandestino.
4. **Incongruência de Esgoto**: Ligações com taxa de esgoto ATIVA, porém com água INATIVA. Indica que o cliente está gerando efluentes provindos de fontes alternativas ou ligações irregulares de água, devendo ser cobrado pelo serviço.

## 🛠️ Tecnologias Utilizadas
- **Linguagem**: Python
- **Análise de Dados**: Pandas
- **Dashboard e UI**: Streamlit
- **Gráficos**: Plotly Express e Graph Objects

## 💡 Premissas e Metodologia (Cálculo de ROI)
Para priorizar as ações com o melhor *Payback*, as seguintes premissas foram adotadas (e podem ser simuladas no próprio dashboard):
- **Custo de Troca de Hidrômetro**: Assumido em R$ 150,00 por ordem de serviço.
- **Custo de Inspeção de Fraude**: Assumido em R$ 100,00 por deslocamento/fiscalização.
- **Tarifa Média Estimada**: Calculada automaticamente pela relação (`VALOR_AGUA / VOLUME_FATURADO`) com base nos clientes válidos e pagantes.
- **Consumo Saudável Estimado**: Para calcular o que foi "perdido" em irregularidades (como hidrômetros parados e esgoto sem água), estimou-se um consumo basal de 15m³.

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
