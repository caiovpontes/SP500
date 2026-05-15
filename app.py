import pandas as pd
import plotly.express as px
import streamlit as st

# --- Configuração da página ---
st.set_page_config(page_title="S&P 500 Market Explorer", layout="wide")

# --- Leitura dos dados ---
df = pd.read_csv('sp500_companies.csv')
df['Marketcap_B'] = pd.to_numeric(df['Marketcap'], errors='coerce') / 1e9
df['Currentprice'] = pd.to_numeric(df['Currentprice'], errors='coerce')
df['Revenuegrowth'] = pd.to_numeric(df['Revenuegrowth'], errors='coerce')
df['Ebitda_B'] = pd.to_numeric(df['Ebitda'], errors='coerce') / 1e9
df = df.dropna(subset=['Marketcap_B', 'Sector'])

# --- Cabeçalho ---
st.header('S&P 500 Market Explorer')
st.write('''
Explore a composição e os fundamentos das 500 maiores empresas de capital aberto dos Estados Unidos.
Use as caixas de seleção abaixo para visualizar diferentes análises.
''')

st.divider()

# --- Filtro por setor ---
st.subheader('Filtros')
todos_setores = sorted(df['Sector'].dropna().unique())
setores_selecionados = st.multiselect(
    'Filtrar por setor:',
    options=todos_setores,
    default=todos_setores
)
df_filtrado = df[df['Sector'].isin(setores_selecionados)]
st.write(f'**{len(df_filtrado)}** empresas selecionadas')

st.divider()

# --- Checkbox 1: Histograma ---
st.subheader('1. Distribuição de Market Cap')
if st.checkbox('Mostrar histograma de Market Cap'):
    st.write('Distribuição das empresas por capitalização de mercado. O primeiro gráfico mostra todas as empresas, o segundo filtra abaixo de US$500B para revelar melhor a distribuição da maioria.')

    fig1a = px.histogram(
        df_filtrado.dropna(subset=['Marketcap_B']),
        x='Marketcap_B', nbins=50, color='Sector',
        title='Distribuição de Market Cap — todas as empresas',
        labels={'Marketcap_B': 'Market Cap (USD Bilhões)'}
    )
    st.plotly_chart(fig1a, use_container_width=True)

    fig1b = px.histogram(
        df_filtrado[df_filtrado['Marketcap_B'] < 500].dropna(subset=['Marketcap_B']),
        x='Marketcap_B', nbins=50, color='Sector',
        title='Distribuição de Market Cap — empresas abaixo de US$500B',
        labels={'Marketcap_B': 'Market Cap (USD Bilhões)'}
    )
    st.plotly_chart(fig1b, use_container_width=True)

st.divider()

# --- Checkbox 2: Scatter Market Cap vs Revenue Growth ---
st.subheader('2. Market Cap vs Crescimento de Receita')
if st.checkbox('Mostrar gráfico de dispersão: Market Cap vs Crescimento'):
    st.write('Relação entre tamanho da empresa e crescimento de receita. Empresas maiores tendem a crescer menos.')
    df_scatter = df_filtrado.dropna(subset=['Revenuegrowth'])
    fig2 = px.scatter(
        df_scatter,
        x='Marketcap_B', y='Revenuegrowth',
        color='Sector', hover_name='Shortname', opacity=0.7,
        title='Market Cap vs Crescimento de Receita por Setor',
        labels={'Marketcap_B': 'Market Cap (USD Bilhões)', 'Revenuegrowth': 'Crescimento de Receita'}
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --- Checkbox 3: Crescimento por setor ---
st.subheader('3. Crescimento Médio por Setor')
if st.checkbox('Mostrar crescimento médio por setor'):
    st.write('Crescimento médio de receita anual por setor (em formato decimal: 0.1 = 10%).')
    df_growth = df_filtrado.dropna(subset=['Revenuegrowth'])
    growth_by_sector = df_growth.groupby('Sector')['Revenuegrowth'].mean().reset_index()
    growth_by_sector = growth_by_sector.sort_values('Revenuegrowth', ascending=False)
    fig3 = px.bar(
        growth_by_sector,
        x='Sector', y='Revenuegrowth',
        title='Crescimento Médio de Receita por Setor',
        labels={'Revenuegrowth': 'Crescimento Médio de Receita', 'Sector': 'Setor'},
        color='Revenuegrowth', color_continuous_scale='RdYlGn'
    )
    fig3.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# --- Checkbox 4: Lucratividade por setor ---
st.subheader('4. Lucratividade por Setor')
if st.checkbox('Mostrar lucratividade por setor'):
    st.write('EBITDA médio absoluto por setor (volume de lucro) e múltiplo Market Cap/EBITDA (valuation).')

    df_ebitda = df_filtrado.dropna(subset=['Ebitda_B', 'Sector'])

    # EBITDA absoluto
    ebitda_by_sector = df_ebitda.groupby('Sector')['Ebitda_B'].mean().reset_index()
    ebitda_by_sector = ebitda_by_sector.sort_values('Ebitda_B', ascending=False)
    fig4a = px.bar(
        ebitda_by_sector,
        x='Sector', y='Ebitda_B',
        title='EBITDA Médio por Setor (USD Bilhões)',
        labels={'Ebitda_B': 'EBITDA Médio (USD Bilhões)', 'Sector': 'Setor'},
        color='Ebitda_B', color_continuous_scale='RdYlGn'
    )
    fig4a.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig4a, use_container_width=True)

    # Market Cap / EBITDA (excluindo Financial Services)
    df_multiple = df_ebitda[df_ebitda['Sector'] != 'Financial Services'].copy()
    df_multiple['Valuation_Multiple'] = df_multiple['Marketcap_B'] / df_multiple['Ebitda_B']
    multiple_by_sector = df_multiple.groupby('Sector')['Valuation_Multiple'].mean().reset_index()
    multiple_by_sector = multiple_by_sector.sort_values('Valuation_Multiple', ascending=False)
    fig4b = px.bar(
        multiple_by_sector,
        x='Sector', y='Valuation_Multiple',
        title='Valuation: Market Cap/EBITDA por Setor (excl. Financial Services)',
        labels={'Valuation_Multiple': 'Market Cap/EBITDA (múltiplo)', 'Sector': 'Setor'},
        color='Valuation_Multiple', color_continuous_scale='RdYlGn_r'
    )
    fig4b.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig4b, use_container_width=True)

st.divider()

# --- Checkbox 5: Concentração top 10 ---
st.subheader('5. Concentração do Índice')
if st.checkbox('Mostrar participação das Top 10 empresas'):
    st.write('Quanto do índice as 10 maiores empresas representam?')
    df_conc = df.dropna(subset=['Marketcap_B', 'Shortname']).sort_values('Marketcap_B', ascending=False)
    total = df_conc['Marketcap_B'].sum()
    top10 = df_conc.head(10).copy()
    top10['Participacao'] = (top10['Marketcap_B'] / total) * 100
    top10_pct = top10['Participacao'].sum()

    st.metric('Participação das Top 10 no índice', f'{top10_pct:.1f}%')

    fig5 = px.bar(
        top10, x='Shortname', y='Participacao',
        title='Participação das Top 10 Empresas no Market Cap Total (%)',
        labels={'Shortname': 'Empresa', 'Participacao': 'Participação (%)'},
        color='Participacao', color_continuous_scale='Blues'
    )
    fig5.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig5, use_container_width=True)

st.divider()

# --- Checkbox 6: Desigualdade interna por setor (box plot) ---
st.subheader('6. Desigualdade Interna por Setor')
if st.checkbox('Mostrar box plot de Market Cap por setor'):
    st.write('Quanto a distribuição de market cap varia dentro de cada setor? Quanto maior a caixa, mais desigual o setor.')
    df_box = df_filtrado.dropna(subset=['Marketcap_B'])
    fig6 = px.box(
        df_box, x='Sector', y='Marketcap_B',
        title='Distribuição de Market Cap por Setor',
        labels={'Marketcap_B': 'Market Cap (USD Bilhões)', 'Sector': 'Setor'},
        color='Sector'
    )
    fig6.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig6, use_container_width=True)

st.divider()

# --- Checkbox 7: Outliers ---
st.subheader('7. Outliers: High Growth Small Cap')
if st.checkbox('Mostrar empresas com alto crescimento e market cap baixo'):
    st.write('Empresas com crescimento de receita acima de 50% e market cap abaixo de US$100B.')
    df_outliers = df_filtrado.dropna(subset=['Marketcap_B', 'Revenuegrowth'])
    df_outliers = df_outliers.copy()
    df_outliers['Destaque'] = (
        (df_outliers['Revenuegrowth'] > 0.5) &
        (df_outliers['Marketcap_B'] < 100)
    )
    fig7 = px.scatter(
        df_outliers,
        x='Marketcap_B', y='Revenuegrowth',
        color='Destaque', hover_name='Shortname',
        hover_data={'Sector': True, 'Marketcap_B': True, 'Revenuegrowth': True},
        title='Outliers: Crescimento Alto + Market Cap Baixo',
        labels={'Marketcap_B': 'Market Cap (USD Bilhões)', 'Revenuegrowth': 'Crescimento de Receita', 'Destaque': 'High Growth Small Cap'},
        color_discrete_map={True: '#00CC96', False: '#636EFA'},
        opacity=0.7
    )
    fig7.add_hline(y=0.5, line_dash='dash', line_color='red', annotation_text='50% crescimento')
    fig7.add_vline(x=100, line_dash='dash', line_color='red', annotation_text='US$100B')
    st.plotly_chart(fig7, use_container_width=True)

    outliers = df_outliers[df_outliers['Destaque'] == True][
        ['Shortname', 'Symbol', 'Sector', 'Marketcap_B', 'Revenuegrowth']
    ].sort_values('Revenuegrowth', ascending=False).reset_index(drop=True)
    st.write(f'**{len(outliers)} empresas** identificadas:')
    st.dataframe(outliers, use_container_width=True)

st.divider()

# --- Checkbox 8: Geografia ---
st.subheader('8. Geografia: Market Cap por Estado')
if st.checkbox('Mostrar concentração de market cap por estado'):
    st.write('Quais estados americanos concentram mais valor de mercado no S&P 500?')
    df_geo = df_filtrado.dropna(subset=['State', 'Marketcap_B'])
    geo_by_state = df_geo.groupby('State')['Marketcap_B'].sum().reset_index()
    geo_by_state = geo_by_state.sort_values('Marketcap_B', ascending=False).head(15)
    fig8 = px.bar(
        geo_by_state, x='State', y='Marketcap_B',
        title='Top 15 Estados por Market Cap Total (USD Bilhões)',
        labels={'Marketcap_B': 'Market Cap Total (USD Bilhões)', 'State': 'Estado'},
        color='State', color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig8.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig8, use_container_width=True)

st.divider()
st.caption('Fonte: S&P 500 Companies Dataset — Kaggle')
