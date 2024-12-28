import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
import toml
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

# Função para carregar credenciais a partir de um arquivo TOML
def load_credentials_from_toml(toml_file):
    """
    Carrega credenciais do arquivo TOML.
    """
    try:
        with open(toml_file, "r") as file:
            config = toml.load(file)
            return config["service_account"]
    except Exception as e:
        logging.error(f"Erro ao carregar credenciais: {e}")
        return None

# Função para formatar o CNPJ
def formatar_cnpj(cnpj):
    """
    Formata um número de CNPJ no formato 00.000.000/0000-00.
    """
    cnpj = str(cnpj).replace(",", "").replace(".", "").replace("-", "").replace("/", "").strip()
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj

# Função para carregar dados do Google Sheets
def load_google_sheet(sheet_id, sheet_name='NFE_DONUTS', credentials=None):
    """
    Carrega os dados de uma planilha do Google Sheets.
    """
    if not credentials:
        return None, "Credenciais não fornecidas."

    try:
        creds = Credentials.from_service_account_info(credentials)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        data = sheet.get_all_records()

        if not data:
            logging.warning("A planilha não contém dados.")
            return None, "A planilha não contém dados."

        # Converte os dados para DataFrame e formata os CNPJs
        df = pd.DataFrame(data)
        if "CNPJ" in df.columns:
            df["CNPJ"] = df["CNPJ"].apply(formatar_cnpj)

        return df, None
    except Exception as e:
        logging.error(f"Erro ao abrir a planilha: {e}")
        return None, f"Erro ao abrir a planilha: {e}"

# Função para filtrar dados da planilha
def filtrar_dados(df, query):
    """
    Filtra os dados com base na consulta fornecida.
    """
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

st.markdown("<h1 style='color:white;'>📄 Consulta de Notas e Rastreamento - THE BEST AÇAI - DONUTS</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:white;'>Bem-vindo ao sistema de consulta de notas e rastreamento da The Best Açai - Donuts.</p>", unsafe_allow_html=True)

# Carregar credenciais do arquivo TOML
credentials = load_credentials_from_toml("credentials.toml")
if not credentials:
    st.error("Erro ao carregar credenciais. Verifique o arquivo TOML.")
else:
    # Carregar planilha do Google Sheets
    sheet_id = "1gXMG571pgj2YSKo2LKAqLLZWxd_jyo_xhs4s-bg6bSo"
    df, error = load_google_sheet(sheet_id, "donuts", credentials)

    if error:
        st.error(error)
    else:
        st.markdown("<h3 style='color:white;'>Pesquisar Notas Fiscais</h3>", unsafe_allow_html=True)
        query = st.text_input("Digite o CNPJ (formato: 00.000.000/0000-00):")

        if st.button("Buscar Nota Fiscal"):
            if query:
                filtered_df, filter_error = filtrar_dados(df, query)
                if filter_error:
                    st.error(filter_error)
                elif filtered_df.empty:
                    st.warning("Nenhum resultado encontrado para a consulta.")
                else:
                    st.success(f"{len(filtered_df)} resultado(s) encontrado(s).")
                    st.dataframe(filtered_df)

        # Adicionar botão para rastrear NF
        st.markdown("<h3 style='color:white; text-align:center;'>Rastrear NF</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:white; text-align:center;'>Clique abaixo para Rastrear Pedido:</p>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='text-align: center; margin-top: 20px;'>
                <a href='https://rodonaves.com.br/rastreio-de-mercadoria' target='_blank'>
                    <button style='background-color: blue; color: white; padding: 10px 20px; border: none; border-radius: 5px;'>
                        <img src='https://i.ibb.co/nnvt26n/logo-header-1.png' alt='Rastrear' style='width: 30px; vertical-align: middle;'> Rastrear Transportadora
                    </button>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
