import streamlit as st
import pandas as pd
import logging

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Caminho do arquivo CSV offline
CSV_FILE_PATH = "notas_the_best.csv"  # Substitua pelo caminho correto do arquivo CSV

# Função para carregar dados do CSV offline
def carregar_dados_csv_offline(caminho):
    """
    Lê dados de um arquivo CSV local.
    """
    try:
        df = pd.read_csv(caminho, sep=';', encoding='utf-8')  # Adicionado separador e encoding
        return df, None
    except Exception as e:
        return None, f"Erro ao carregar dados do arquivo CSV: {e}"

# Interface do Streamlit
st.set_page_config(page_title="Consulta de Notas e Rastreamento", layout="wide")

# Configuração do fundo preto em toda a tela e barra transparente
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        background-color: black;
        color: white;
    }
    .stApp {
        background-color: black; /* Fundo preto sólido */
        padding: 20px;
        border-radius: 15px;
    }
    .stMarkdown {
        color: white !important; /* Garante que todos os textos sejam exibidos em branco */
    }
    .stDataFrame {
        color: white !important;
        background-color: rgba(34, 34, 34, 0.9) !important; /* Fundo escuro para contraste */
    }
    header { 
        background-color: rgba(0, 0, 0, 0.3) !important; /* Torna a barra de cabeçalho transparente */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Adicionar logo centralizada na barra
st.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <img src='https://i.ibb.co/nLkLD0f/GRUPO-NICOPEL-1.png' alt='Logo Campanha Donuts' style='width: 200px;'>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='color:white;'>📄 Consulta de Notas e Rastreamento - CAMPANHA DONUTS - The Best Açai</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:white;'>Bem-vindo ao sistema de consulta de notas e rastreamento da The Best Açai - Donuts.</p>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white;'>Modo de Consulta:</h3>", unsafe_allow_html=True)
st.markdown("<p style='color:white;'>1. Localize a nota fiscal pelo CNPJ.</p>", unsafe_allow_html=True)
st.markdown("<p style='color:white;'>2. Copie a Nota Fiscal.</p>", unsafe_allow_html=True)
st.markdown("<p style='color:white;'>3. Clique no logo da transportadora RODONAVES ao lado do 'pesquisar nota fiscal'. </p>", unsafe_allow_html=True)
st.markdown("<p style='color:white;'>4. Após copiar a NF, copie o CNPJ do Remetente - 10.815.855/0001-24 : Nicopel Embalagens e rastreie seu pedido!</p>", unsafe_allow_html=True)

# Carregar os dados
df, error = carregar_dados_csv_offline(CSV_FILE_PATH)

if error:
    st.error(f"Erro: {error}")
else:
    # Verificar se as colunas esperadas estão presentes
    required_columns = ["DATA DE ENVIO", "CNPJ", "NOME", "NF", "TRANSPORTADORA"]
    if not all(col in df.columns for col in required_columns):
        st.error(f"O arquivo CSV não contém as colunas necessárias: {', '.join(required_columns)}")
    else:
        # Converter as colunas necessárias para string
        for col in required_columns:
            df[col] = df[col].astype(str)

        # Remover o sufixo .0 da coluna NF, se aplicável
        if "NF" in df.columns:
            df["NF"] = df["NF"].str.replace(r"\.0$", "", regex=True)

        col1, col2 = st.columns([3, 1])

        with col1:
            # Campo de busca
            st.markdown("<h3 style='color:white;'>Pesquisar Notas Fiscais</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color:white;'>Digite o CNPJ para buscar :</p>", unsafe_allow_html=True)
            query = st.text_input("", value="", key="query_field")  # Campo de texto sem título embutido

            if st.button("Buscar Nota Fiscal"):
                if query:
                    query = query.strip().lower()
                    filtered_df = df[(df["DATA DE ENVIO"].str.lower().str.contains(query, na=False)) |
                                     (df["CNPJ"].str.lower().str.contains(query, na=False)) |
                                     (df["NOME"].str.lower().str.contains(query, na=False)) |
                                     (df["NF"].str.lower().str.contains(query, na=False)) |
                                     (df["TRANSPORTADORA"].str.lower().str.contains(query, na=False))]

                    if filtered_df.empty:
                        st.warning("Nenhum resultado encontrado para a consulta.")
                    else:
                        st.success(f"{len(filtered_df)} resultado(s) encontrado(s).")
                        st.dataframe(filtered_df)

        with col2:
            st.markdown("<h3 style='color:white; text-align:center;'>Rastrear NF</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color:white; text-align:center;'>Clique abaixo para rastrear:</p>", unsafe_allow_html=True)
            st.markdown(
                """
                <div style='text-align: center; margin-top: 20px;'>
                    <a href='https://rodonaves.com.br/rastreio-de-mercadoria' target='_blank'>
                        <button style='background-color: blue; color: white; padding: 10px 20px; border: none; border-radius: 5px;'>
                            <img src='https://i.ibb.co/nnvt26n/logo-header-1.png' alt='Rastrear' style='width: 150px; vertical-align: middle;'>
                        </button>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )
