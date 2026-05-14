# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Sanova Analytics - Gestão Comercial",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Customizada
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00B4D8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-title {
        color: #90E0EF;
        font-size: 14px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 28px;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #00B4D8;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# FUNÇÕES DE CARREGAMENTO E PROCESSAMENTO
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    file_path = "Dados - Estudo Micromedição.xlsx"
    df = pd.read_excel(file_path)
    
    # Limpeza e Padronização
    df['SIT._LIG_AGUA'] = df['SIT._LIG_AGUA'].fillna('Desconhecida').str.strip()
    df['SIT._LIG_ESGOTO'] = df['SIT._LIG_ESGOTO'].fillna('Desconhecida').str.strip()
    df['CATEGORIA_PRINCIPAL'] = df['CATEGORIA_PRINCIPAL'].fillna('Desconhecida').str.strip()
    
    # Preenchendo nulos em colunas numéricas chave
    num_cols = ['VOLUME_LIDO', 'VOLUME_REAL', 'VOLUME_FATURADO', 'VALOR_TOTAL', 'VALOR_AGUA']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Tratamento de Hidrômetros
    hidro_cols = ['MARCA_HIDROMETRO', 'TIPO_HIDROMETRO', 'CLASSE_METROLOGICA', 'CAPACIDADE_HIDROMETRO']
    for col in hidro_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Não Informado').astype(str)

    # Tratamento de Economias
    eco_cols = ['NUMERO_ECONOMIAS_RES', 'NUMERO_ECONOMIAS_COM', 'NUMERO_ECONOMIAS_IND', 'NUMERO_ECONOMIAS_PUB']
    for col in eco_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # Tratamento de Volumes Históricos
    vol_cols = [f'VOLUME_LIDO_{str(i).zfill(2)}' for i in range(1, 13)]
    for col in vol_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # Criação de colunas de Análise e Regras de Negócio
    
    # 1. Hidrômetro Parado (Ligação Ativa com 0 consumo medido, mas com faturamento mínimo ou 0)
    df['HIDROMETRO_PARADO'] = (df['SIT._LIG_AGUA'].str.upper() == 'ATIVA') & (df['VOLUME_LIDO'] == 0)
    
    # 2. Ligação Clandestina / Irregular (Ligação inativa registrando consumo)
    df['POSSIVEL_CLANDESTINA'] = (df['SIT._LIG_AGUA'].str.upper() != 'ATIVA') & (df['VOLUME_LIDO'] > 0)
    
    # 3. Anomalia de Categoria (Residencial com altíssimo consumo)
    df['ANOMALIA_CATEGORIA'] = (df['CATEGORIA_PRINCIPAL'].str.upper() == 'RESIDENCIAL') & (df['VOLUME_LIDO'] > 50)
    
    # 4. Incongruência Esgoto (Esgoto Ativo, Água não Ativa)
    df['INCONGRUENCIA_ESGOTO'] = (df['SIT._LIG_ESGOTO'].str.upper() == 'ATIVA') & (df['SIT._LIG_AGUA'].str.upper() != 'ATIVA')
    
    # 5. Idade do Hidrômetro (Mais de 5 anos -> 1825 dias)
    from datetime import datetime
    if 'DATA_INSTALACAO_HIDROMETRO' in df.columns:
        df['DATA_INSTALACAO_HIDROMETRO'] = pd.to_datetime(df['DATA_INSTALACAO_HIDROMETRO'], errors='coerce')
        idade_dias = (datetime.now() - df['DATA_INSTALACAO_HIDROMETRO']).dt.days
        df['SUBMEDICAO_IDADE'] = idade_dias > (5 * 365)
    else:
        df['SUBMEDICAO_IDADE'] = False
        
    # 6. Queda Brusca de Consumo (Caiu > 50% em relacao a media historica)
    df['MEDIA_HISTORICA'] = df[vol_cols].mean(axis=1)
    df['QUEDA_BRUSCA_CONSUMO'] = (df['MEDIA_HISTORICA'] > 10) & (df['VOLUME_LIDO'] < (df['MEDIA_HISTORICA'] * 0.5))
    
    # Calcular Tarifa Média Estimada (R$ / m³) para quem consumiu e pagou
    df_valid = df[(df['VOLUME_FATURADO'] > 0) & (df['VALOR_AGUA'] > 0)]
    tarifa_media = (df_valid['VALOR_AGUA'] / df_valid['VOLUME_FATURADO']).mean() if not df_valid.empty else 5.0
    
    # Estimativa de Perda Financeira Mensal (Ganhos Potenciais)
    df['PERDA_ESTIMADA_R$'] = 0.0
    
    # Regras de estimativa de perda
    df.loc[df['HIDROMETRO_PARADO'], 'PERDA_ESTIMADA_R$'] = (15 * tarifa_media - df.loc[df['HIDROMETRO_PARADO'], 'VALOR_AGUA']).clip(lower=0)
    df.loc[df['POSSIVEL_CLANDESTINA'], 'PERDA_ESTIMADA_R$'] = df.loc[df['POSSIVEL_CLANDESTINA'], 'VOLUME_LIDO'] * tarifa_media
    df.loc[df['ANOMALIA_CATEGORIA'], 'PERDA_ESTIMADA_R$'] = (df.loc[df['ANOMALIA_CATEGORIA'], 'VOLUME_LIDO'] * tarifa_media) * 0.50
    df.loc[df['INCONGRUENCIA_ESGOTO'], 'PERDA_ESTIMADA_R$'] = 15 * tarifa_media  # Considera-se consumo irregular não faturado
    df.loc[df['SUBMEDICAO_IDADE'], 'PERDA_ESTIMADA_R$'] = 5 * tarifa_media
    df.loc[df['QUEDA_BRUSCA_CONSUMO'], 'PERDA_ESTIMADA_R$'] = (df.loc[df['QUEDA_BRUSCA_CONSUMO'], 'MEDIA_HISTORICA'] - df.loc[df['QUEDA_BRUSCA_CONSUMO'], 'VOLUME_LIDO']) * tarifa_media
    
    return df, tarifa_media

df, tarifa_media = load_data()

# -------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR)
# -------------------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3264/3264147.png", width=80)
st.sidebar.title("Sanova Analytics")
st.sidebar.markdown("Gestão Comercial e Combate a Perdas")
st.sidebar.divider()

st.sidebar.subheader("Filtros Globais")
sit_agua_filter = st.sidebar.multiselect("Situação da Ligação (Água)", df['SIT._LIG_AGUA'].unique(), default=df['SIT._LIG_AGUA'].unique())
cat_filter = st.sidebar.multiselect("Categoria", df['CATEGORIA_PRINCIPAL'].unique(), default=df['CATEGORIA_PRINCIPAL'].unique())

df_filtered = df[(df['SIT._LIG_AGUA'].isin(sit_agua_filter)) & (df['CATEGORIA_PRINCIPAL'].isin(cat_filter))]

# -------------------------------------------------------------------
# CORPO PRINCIPAL - TABS
# -------------------------------------------------------------------
st.title("📊 Painel Estratégico de Saneamento")
st.markdown("Análise técnica e estratégica para identificação de melhorias operacionais, recuperação de receitas e mitigação de perdas comerciais.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Resumo Executivo", 
    "🚨 Anomalias & Fraudes", 
    "💰 Recuperação de Receita", 
    "🎯 Plano de Ação e Payback",
    "⚙️ Parque de Hidrômetros"
])

# ==========================================
# TAB 1: RESUMO EXECUTIVO
# ==========================================
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total de Ligações</div>
            <div class="metric-value">{len(df_filtered):,}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Faturamento Total (Mês)</div>
            <div class="metric-value">R$ {df_filtered['VALOR_TOTAL'].sum():,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Volume Faturado</div>
            <div class="metric-value">{df_filtered['VOLUME_FATURADO'].sum():,.0f} m³</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Tarifa Média Estimada</div>
            <div class="metric-value">R$ {tarifa_media:,.2f} /m³</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Distribuição por Categoria")
        fig_cat = px.pie(df_filtered, names='CATEGORIA_PRINCIPAL', hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
        fig_cat.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with colB:
        st.subheader("Tendência Histórica de Volume")
        # Calc mean for each past month
        vol_cols = [f'VOLUME_LIDO_{str(i).zfill(2)}' for i in range(1, 13)]
        means = []
        months = []
        for idx, col in enumerate(vol_cols, 1):
            if col in df_filtered.columns:
                means.append(df_filtered[col].mean())
                months.append(f"Mês -{idx}")
        if means:
            fig_hist = px.line(x=months, y=means, markers=True, title="Volume Médio Lido (m³) por Mês Retroativo")
            fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="Volume Médio (m³)")
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Dados históricos indisponíveis.")

    colC, colD = st.columns(2)
    with colC:
        st.subheader("Distribuição de Economias")
        eco_sum = {
            'Residencial': df_filtered['NUMERO_ECONOMIAS_RES'].sum() if 'NUMERO_ECONOMIAS_RES' in df_filtered.columns else 0,
            'Comercial': df_filtered['NUMERO_ECONOMIAS_COM'].sum() if 'NUMERO_ECONOMIAS_COM' in df_filtered.columns else 0,
            'Industrial': df_filtered['NUMERO_ECONOMIAS_IND'].sum() if 'NUMERO_ECONOMIAS_IND' in df_filtered.columns else 0,
            'Pública': df_filtered['NUMERO_ECONOMIAS_PUB'].sum() if 'NUMERO_ECONOMIAS_PUB' in df_filtered.columns else 0
        }
        fig_eco = px.bar(x=list(eco_sum.keys()), y=list(eco_sum.values()), color=list(eco_sum.keys()), text_auto='.2s')
        fig_eco.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title="Tipo de Economia", yaxis_title="Total", showlegend=False)
        st.plotly_chart(fig_eco, use_container_width=True)

    with colD:
        st.subheader("Top 10 Maiores Consumidores")
        top_10 = df_filtered.nlargest(10, 'VOLUME_LIDO')[['MATRICULA', 'CATEGORIA_PRINCIPAL', 'VOLUME_LIDO', 'VALOR_TOTAL']]
        st.dataframe(top_10, use_container_width=True, hide_index=True)

# ==========================================
# TAB 2: ANOMALIAS E FRAUDES
# ==========================================
with tab2:
    st.subheader("Detecção de Comportamentos Suspeitos")
    st.markdown("O sistema analisa os dados do último mês e identifica padrões atípicos que geram perdas comerciais.")
    
    # Contabilização
    qtd_parados = df_filtered['HIDROMETRO_PARADO'].sum()
    qtd_cland = df_filtered['POSSIVEL_CLANDESTINA'].sum()
    qtd_anom = df_filtered['ANOMALIA_CATEGORIA'].sum()
    qtd_esg = df_filtered['INCONGRUENCIA_ESGOTO'].sum()
    qtd_idade = df_filtered['SUBMEDICAO_IDADE'].sum()
    qtd_queda = df_filtered['QUEDA_BRUSCA_CONSUMO'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🛑 Hidrômetros Parados", f"{qtd_parados}", help="Ligações ativas que não registraram consumo.")
    col2.metric("⚠️ Clandestinas", f"{qtd_cland}", help="Ligações inativas/cortadas que registraram volume lido.")
    col3.metric("🏢 Anomalia Categoria", f"{qtd_anom}", help="Residências com consumo de grande porte (>50m³).")
    
    col4, col5, col6 = st.columns(3)
    col4.metric("🚽 Incongruência Esgoto", f"{qtd_esg}", help="Ligações com Esgoto ativo mas Água inativa.")
    col5.metric("⏳ Submedição (Idade)", f"{qtd_idade}", help="Hidrômetros com mais de 5 anos de instalação.")
    col6.metric("📉 Queda Brusca", f"{qtd_queda}", help="Consumo caiu >50% em relação à média de 12 meses.")
    
    st.divider()
    st.markdown("### Detalhamento das Ligações Críticas")
    
    tipo_anomalia = st.selectbox("Selecione a anomalia para visualizar:", 
                                 ["Hidrômetros Parados", "Possíveis Clandestinas", "Anomalia de Categoria", "Incongruência Esgoto", "Submedição por Idade", "Queda Brusca de Consumo"])
    
    if tipo_anomalia == "Hidrômetros Parados":
        st.dataframe(df_filtered[df_filtered['HIDROMETRO_PARADO']][['MATRICULA', 'SIT._LIG_AGUA', 'CATEGORIA_PRINCIPAL', 'VOLUME_LIDO', 'VOLUME_FATURADO', 'VALOR_TOTAL', 'DATA_INSTALACAO_HIDROMETRO']], hide_index=True)
    elif tipo_anomalia == "Possíveis Clandestinas":
        st.dataframe(df_filtered[df_filtered['POSSIVEL_CLANDESTINA']][['MATRICULA', 'SIT._LIG_AGUA', 'VOLUME_LIDO', 'VOLUME_FATURADO', 'VALOR_TOTAL']], hide_index=True)
    elif tipo_anomalia == "Anomalia de Categoria":
        st.dataframe(df_filtered[df_filtered['ANOMALIA_CATEGORIA']][['MATRICULA', 'CATEGORIA_PRINCIPAL', 'VOLUME_LIDO', 'VALOR_TOTAL']], hide_index=True)
    elif tipo_anomalia == "Incongruência Esgoto":
        st.dataframe(df_filtered[df_filtered['INCONGRUENCIA_ESGOTO']][['MATRICULA', 'SIT._LIG_AGUA', 'SIT._LIG_ESGOTO', 'VOLUME_LIDO', 'VALOR_TOTAL']], hide_index=True)
    elif tipo_anomalia == "Submedição por Idade":
        st.dataframe(df_filtered[df_filtered['SUBMEDICAO_IDADE']][['MATRICULA', 'DATA_INSTALACAO_HIDROMETRO', 'VOLUME_LIDO', 'VOLUME_FATURADO', 'VALOR_TOTAL']], hide_index=True)
    else:
        st.dataframe(df_filtered[df_filtered['QUEDA_BRUSCA_CONSUMO']][['MATRICULA', 'MEDIA_HISTORICA', 'VOLUME_LIDO', 'VOLUME_FATURADO', 'VALOR_TOTAL']], hide_index=True)

# ==========================================
# TAB 3: RECUPERAÇÃO DE RECEITA
# ==========================================
with tab3:
    st.subheader("Estimativa de Ganhos Financeiros")
    
    total_perda = df_filtered['PERDA_ESTIMADA_R$'].sum()
    st.success(f"📈 Potencial Total de Recuperação Mensal: **R$ {total_perda:,.2f}**")
    
    df_perdas = pd.DataFrame({
        'Tipo de Anomalia': ['Hidrômetros Parados', 'Clandestinas', 'Atualização Cadastral', 'Incongruência Esgoto', 'Submedição (Idade)', 'Queda Brusca'],
        'Perda Financeira (R$)': [
            df_filtered[df_filtered['HIDROMETRO_PARADO']]['PERDA_ESTIMADA_R$'].sum(),
            df_filtered[df_filtered['POSSIVEL_CLANDESTINA']]['PERDA_ESTIMADA_R$'].sum(),
            df_filtered[df_filtered['ANOMALIA_CATEGORIA']]['PERDA_ESTIMADA_R$'].sum(),
            df_filtered[df_filtered['INCONGRUENCIA_ESGOTO']]['PERDA_ESTIMADA_R$'].sum(),
            df_filtered[df_filtered['SUBMEDICAO_IDADE']]['PERDA_ESTIMADA_R$'].sum(),
            df_filtered[df_filtered['QUEDA_BRUSCA_CONSUMO']]['PERDA_ESTIMADA_R$'].sum()
        ]
    })
    
    colA, colB = st.columns(2)
    with colA:
        fig_perdas = px.bar(df_perdas, x='Tipo de Anomalia', y='Perda Financeira (R$)', 
                            color='Tipo de Anomalia', text_auto='.2s',
                            title='Potencial de Recuperação por Causa')
        fig_perdas.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_perdas, use_container_width=True)
        
    with colB:
        st.markdown("### Metodologia de Cálculo")
        st.info("""
        - **Hidrômetros Parados**: Calculou-se a diferença entre a tarifa de um consumo médio saudável (15m³) e o valor atualmente faturado.
        - **Clandestinas**: Multiplicação do volume real lido pela tarifa média, considerando que a ligação deveria estar pagando.
        - **Atualização Cadastral**: Estima-se um ganho de 50% de ágio na tarifa caso uma ligação residencial de altíssimo consumo seja reclassificada.
        - **Incongruência Esgoto**: Estima-se a cobrança correspondente a um consumo de 15m³ que provavelmente está sendo desviado e descartado na rede.
        - **Submedição (Idade)**: Estima-se uma perda de 5m³ por ligação devido à perda de sensibilidade do hidrômetro antigo.
        - **Queda Brusca**: Estima-se a recuperação da diferença entre o consumo médio histórico do cliente e o consumo atipicamente baixo do mês atual.
        """)

# ==========================================
# TAB 4: PLANO DE AÇÃO E PAYBACK
# ==========================================
with tab4:
    st.subheader("Priorização e Estudo de Viabilidade (Payback)")
    
    # Definição de custos operacionais (Premissas)
    custo_troca_hidrometro = st.number_input("Custo de Troca de Hidrômetro (R$)", value=150.0)
    custo_inspecao = st.number_input("Custo de Inspeção de Fraude/Vistoria (R$)", value=100.0)
    
    # Criando o plano de ação
    acoes = []
    
    # Ação 1: Trocar hidrômetros parados
    if qtd_parados > 0:
        ganho = df_filtered[df_filtered['HIDROMETRO_PARADO']]['PERDA_ESTIMADA_R$'].sum()
        custo = qtd_parados * custo_troca_hidrometro
        payback = custo / ganho if ganho > 0 else 0
        acoes.append({"Ação": "Substituição de Hidrômetros Parados", "Qtd OS": qtd_parados, "Custo Total (R$)": custo, "Retorno Mensal (R$)": ganho, "Payback (Meses)": payback})
        
    # Ação 2: Inspecionar clandestinas
    if qtd_cland > 0:
        ganho = df_filtered[df_filtered['POSSIVEL_CLANDESTINA']]['PERDA_ESTIMADA_R$'].sum()
        custo = qtd_cland * custo_inspecao
        payback = custo / ganho if ganho > 0 else 0
        acoes.append({"Ação": "Inspeção e Corte/Regularização (Clandestinas)", "Qtd OS": qtd_cland, "Custo Total (R$)": custo, "Retorno Mensal (R$)": ganho, "Payback (Meses)": payback})
        
    # Ação 3: Fiscalização Cadastral
    if qtd_anom > 0:
        ganho = df_filtered[df_filtered['ANOMALIA_CATEGORIA']]['PERDA_ESTIMADA_R$'].sum()
        custo = qtd_anom * custo_inspecao
        payback = custo / ganho if ganho > 0 else 0
        acoes.append({"Ação": "Fiscalização de Categoria Comercial", "Qtd OS": qtd_anom, "Custo Total (R$)": custo, "Retorno Mensal (R$)": ganho, "Payback (Meses)": payback})
        
    # Ação 4: Vistoria Incongruência Esgoto
    if qtd_esg > 0:
        ganho = df_filtered[df_filtered['INCONGRUENCIA_ESGOTO']]['PERDA_ESTIMADA_R$'].sum()
        custo = qtd_esg * custo_inspecao
        payback = custo / ganho if ganho > 0 else 0
        acoes.append({"Ação": "Vistoria de Incongruência Esgoto", "Qtd OS": qtd_esg, "Custo Total (R$)": custo, "Retorno Mensal (R$)": ganho, "Payback (Meses)": payback})
        
    # Ação 5: Troca Preventiva por Idade
    if qtd_idade > 0:
        ganho = df_filtered[df_filtered['SUBMEDICAO_IDADE']]['PERDA_ESTIMADA_R$'].sum()
        custo = qtd_idade * custo_troca_hidrometro
        payback = custo / ganho if ganho > 0 else 0
        acoes.append({"Ação": "Substituição Preventiva (Idade > 5 anos)", "Qtd OS": qtd_idade, "Custo Total (R$)": custo, "Retorno Mensal (R$)": ganho, "Payback (Meses)": payback})

    # Ação 6: Inspeção de Queda Brusca
    if qtd_queda > 0:
        ganho = df_filtered[df_filtered['QUEDA_BRUSCA_CONSUMO']]['PERDA_ESTIMADA_R$'].sum()
        custo = qtd_queda * custo_inspecao
        payback = custo / ganho if ganho > 0 else 0
        acoes.append({"Ação": "Inspeção por Queda Brusca de Consumo", "Qtd OS": qtd_queda, "Custo Total (R$)": custo, "Retorno Mensal (R$)": ganho, "Payback (Meses)": payback})
        
    df_acoes = pd.DataFrame(acoes)
    
    if not df_acoes.empty:
        # Ordenar por Payback (menor é melhor)
        df_acoes = df_acoes.sort_values('Payback (Meses)')
        
        st.dataframe(
            df_acoes.style.format({
                "Custo Total (R$)": "R$ {:.2f}", 
                "Retorno Mensal (R$)": "R$ {:.2f}", 
                "Payback (Meses)": "{:.1f} meses"
            }),
            use_container_width=True, hide_index=True
        )
        
        st.markdown("### Conclusão Estratégica")
        melhor_acao = df_acoes.iloc[0]['Ação']
        st.success(f"A ação com o retorno mais rápido é a **{melhor_acao}**, apresentando o menor tempo de payback. Recomenda-se direcionar a equipe de campo primariamente para esta frente, maximizando o ROI da concessionária de saneamento.")
    else:
        st.info("Nenhuma anomalia identificada para geração de plano de ação.")

# ==========================================
# TAB 5: PARQUE DE HIDRÔMETROS
# ==========================================
with tab5:
    st.subheader("Análise do Parque de Hidrômetros")
    st.markdown("Visão geral sobre os equipamentos medidores em operação na área de concessão.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Marcas de Hidrômetro**")
        fig_marcas = px.bar(df_filtered['MARCA_HIDROMETRO'].value_counts().reset_index(), x='MARCA_HIDROMETRO', y='count', text_auto=True, color_discrete_sequence=['#48CAE4'])
        fig_marcas.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title="Marca", yaxis_title="Quantidade")
        st.plotly_chart(fig_marcas, use_container_width=True)
        
    with col2:
        st.markdown("**Tipos de Hidrômetro**")
        fig_tipos = px.pie(df_filtered, names='TIPO_HIDROMETRO', hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
        fig_tipos.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_tipos, use_container_width=True)
        
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Classes Metrológicas**")
        fig_classes = px.bar(df_filtered['CLASSE_METROLOGICA'].value_counts().reset_index(), x='CLASSE_METROLOGICA', y='count', text_auto=True, color_discrete_sequence=['#0077B6'])
        fig_classes.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title="Classe", yaxis_title="Quantidade")
        st.plotly_chart(fig_classes, use_container_width=True)
        
    with col4:
        st.markdown("**Capacidades**")
        fig_cap = px.bar(df_filtered['CAPACIDADE_HIDROMETRO'].value_counts().reset_index(), x='CAPACIDADE_HIDROMETRO', y='count', text_auto=True, color_discrete_sequence=['#023E8A'])
        fig_cap.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title="Capacidade", yaxis_title="Quantidade")
        st.plotly_chart(fig_cap, use_container_width=True)
        
