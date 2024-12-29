import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
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

# Função para formatar o CNPJ
def formatar_cnpj(cnpj):
    cnpj = str(cnpj).replace(",", "").replace(".", "").replace("-", "").replace("/", "").strip()
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj

# Função para carregar dados do Google Sheets
def load_google_sheet(sheet_id, sheet_name='NFE_DONUTS'):
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(
        st.secrets["gcloud"],  # Carregar as credenciais do secrets.toml
        scopes=scope
    )
    try:
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        data = sheet.get_all_records()
        if not data:
            logging.warning("A planilha não contém dados.")
            return None, "A planilha não contém dados."
        df = pd.DataFrame(data)
        if "CNPJ" in df.columns:
            df["CNPJ"] = df["CNPJ"].apply(formatar_cnpj)
        return df, None
    except Exception as e:
        logging.error(f"Erro ao abrir a planilha: {e}")
        return None, f"Erro ao abrir a planilha: {e}"

# Função para filtrar dados da planilha
def filtrar_dados(df, query):
    try:
        query = query.strip().lower()
        filtered_df = df[df.apply(
            lambda row: query in str(row.get("Cliente", "")).lower()
                        or query in str(row.get("CNPJ", "")).lower()
                        or query in str(row.get("N° NFE", "")).lower(), axis=1
        )]
        return filtered_df, None
    except Exception as e:
        logging.error("Erro ao filtrar dados: %s", e)
        return None, "Erro ao filtrar dados."

# Interface do Streamlit
st.set_page_config(page_title="Consulta de Notas e Rastreamento", layout="wide")

# Configuração de estilo
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        background-color: black;
        color: white;
    }
    .stApp {
        background-color: black;
        padding: 20px;
        border-radius: 15px;
    }
    .stMarkdown {
        color: white !important;
    }
    .stDataFrame {
        color: white !important;
        background-color: rgba(34, 34, 34, 0.9) !important;
    }
    header {
        background-color: rgba(0, 0, 0, 0.3) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Adicionar logo
st.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <img src='https://i.ibb.co/nLkLD0f/GRUPO-NICOPEL-1.png' alt='Logo' style='width: 200px;'>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='color:white;'>📄 Consulta de Notas e Rastreamento</h1>", unsafe_allow_html=True)

sheet_id = "1gXMG571pgj2YSKo2LKAqLLZWxd_jyo_xhs4s-bg6bSo"
df, error = load_google_sheet(sheet_id, "donuts")

if error:
    st.error(error)
else:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h3 style='color:white;'>Pesquisar Notas Fiscais</h3>", unsafe_allow_html=True)
        query = st.text_input("", value="", key="query_field")
        if st.button("Buscar Nota Fiscal"):
            if query:
                filtered_df, filter_error = filtrar_dados(df, query)
                if filter_error:
                    st.error(filter_error)
                elif filtered_df.empty:
                    st.warning("Nenhum resultado encontrado.")
                else:
                    st.success(f"{len(filtered_df)} resultado(s) encontrado(s).")
                    st.dataframe(filtered_df)
    with col2:
        st.markdown("<h3 style='color:white;'>Rastrear NF</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:white;'>Clique abaixo:</p>", unsafe_allow_html=True)
        st.markdown(
            """
            <a href='https://rodonaves.com.br/rastreio-de-mercadoria' target='_blank'>
                <button style='background-color: blue; color: white; padding: 10px 20px; border-radius: 5px;'>
                    Rastrear Transportadora
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )
