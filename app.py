import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

from database import execute, get_connection
from auth import autenticar

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Gestão de Contratos", layout="wide")

# ---------------- SESSION ----------------
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ---------------- LISTAS ----------------
INSTALACOES = [
    "PAMBUJUI", "CAUÍPE", "ICÓ", "QUIXADÁ", "ARACATI",
    "RUSSAS", "SOBRAL", "TAUÁ", "MILAGRES"
]

MUNICIPIOS = [
    "Fortaleza", "Caucaia", "Icó", "Quixadá", "Aracati",
    "Russas", "Sobral", "Tauá", "Milagres"
]

UFS = ["CE", "PI"]

# ---------------- LOGIN ----------------
def tela_login():
    st.title("🔐 Acesso ao Sistema")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = autenticar(usuario, senha)
        if user:
            st.session_state.usuario = user[1]
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

# ---------------- CADASTRO ----------------
def tela_cadastro():
    st.title("📝 Cadastro de Contratos")

    with st.form("form_contrato", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        empresa = col1.text_input("Empresa")
        instalacao = col2.selectbox("Instalação / Ativo", INSTALACOES)
        municipio = col3.selectbox("Município", MUNICIPIOS)
        uf = col1.selectbox("UF", UFS)

        area_total = col2.number_input("Área Total (m²)", min_value=0.0)

        acessante = col3.selectbox("Acessante", ["Sim", "Não"])
        videomonitoramento = col1.selectbox("Videomonitoramento", ["Sim", "Não"])
        controle_acesso = col2.selectbox("Controle de Acesso", ["Sim", "Não"])
        registro_ronda = col3.selectbox("Registro de Ronda", ["Sim", "Não"])

        pedido_sap = col1.text_input("Pedido SAP")
        servico = col2.selectbox("Serviço Contratado", ["Portaria", "Vigilância"])
        horario = col3.selectbox("Horário do Posto", ["12h", "24h"])

        dt_inicio = col1.date_input("Data Início")
        dt_fim = col2.date_input("Data Fim")

        qtd_postos = col1.number_input("Qtd de Postos", min_value=1, step=1)
        qtd_agentes = col2.number_input("Qtd de Agentes", min_value=0, step=1)

        st.markdown("### 💰 Valores")

        colv1, colv2, colv3 = st.columns(3)

        vlr_unit_agente = colv1.number_input(
            "Vlr. Unit Agente",
            min_value=0.0,
            step=0.01,
            format="%.2f"
        )

        vlr_mensal_atual = qtd_agentes * vlr_unit_agente
        vlr_unit_posto = vlr_mensal_atual / qtd_postos if qtd_postos > 0 else 0

        colv2.metric("Vlr. Mensal Atual (automático)", f"R$ {vlr_mensal_atual:,.2f}")
        colv3.metric("Vlr. Unit Posto (automático)", f"R$ {vlr_unit_posto:,.2f}")

        salvar = st.form_submit_button("💾 Salvar Contrato")

        if salvar:
            if not empresa or not pedido_sap:
                st.error("Empresa e Pedido SAP são obrigatórios.")
                return

            execute("""
                INSERT INTO contratos (
                    empresa, instalacao, municipio, uf,
                    area_total, acessante, videomonitoramento,
                    controle_acesso, registro_ronda,
                    pedido_sap, servico_contratado, horario_posto,
                    dt_inicio, dt_fim,
                    qtd_postos, qtd_agentes,
                    vlr_unit_agente, vlr_unit_posto, vlr_mensal_atual,
                    usuario_cadastro, criado_em
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                empresa, instalacao, municipio, uf,
                area_total, acessante, videomonitoramento,
                controle_acesso, registro_ronda,
                pedido_sap, servico, horario,
                dt_inicio, dt_fim,
                qtd_postos, qtd_agentes,
                vlr_unit_agente, vlr_unit_posto, vlr_mensal_atual,
                st.session_state.usuario, datetime.now()
            ))

            st.success("✅ Contrato cadastrado com sucesso!")

# ---------------- FILTROS COMPLETOS ----------------
def aplicar_filtros(df):
    with st.sidebar:
        st.header("🔎 Filtros")

        # -------- PERÍODO --------
        st.subheader("📅 Período")
        ini = st.date_input("Data início (de)", value=None)
        fim = st.date_input("Data início (até)", value=None)
        if ini:
            df = df[df["dt_inicio"] >= pd.Timestamp(ini)]
        if fim:
            df = df[df["dt_inicio"] <= pd.Timestamp(fim)]

        ini_f = st.date_input("Data fim (de)", value=None, key="fim_de")
        fim_f = st.date_input("Data fim (até)", value=None, key="fim_ate")
        if ini_f:
            df = df[df["dt_fim"] >= pd.Timestamp(ini_f)]
        if fim_f:
            df = df[df["dt_fim"] <= pd.Timestamp(fim_f)]

        # -------- TODAS AS COLUNAS --------
        for col in df.columns:
            if df[col].dtype == "object" and col != "usuario_cadastro":
                valores = st.multiselect(col, sorted(df[col].dropna().unique()))
                if valores:
                    df = df[df[col].isin(valores)]

        # -------- USUÁRIO (MANTIDO) --------
        usuarios = st.multiselect(
            "usuario_cadastro",
            sorted(df["usuario_cadastro"].dropna().unique())
        )
        if usuarios:
            df = df[df["usuario_cadastro"].isin(usuarios)]

        # -------- AÇÕES --------
        if st.button("📤 Exportar filtros para Excel"):
            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            st.download_button(
                "⬇️ Download",
                buffer.getvalue(),
                "contratos_filtrados.xlsx"
            )

        if st.button("🚪 Sair da aplicação"):
            st.session_state.usuario = None
            st.rerun()

    return df

# ---------------- VISUALIZAÇÃO ----------------
def tela_visualizacao():
    st.title("📋 Contratos")

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM contratos", conn)
    conn.close()

    if df.empty:
        st.warning("Nenhum contrato cadastrado.")
        return

    df["dt_fim"] = pd.to_datetime(df["dt_fim"])
    hoje = pd.Timestamp.today().normalize()
    df["dias_para_fim"] = (df["dt_fim"] - hoje).dt.days

    def destacar(row):
        if row["dias_para_fim"] <= 10:
            return ["background-color: #ffcccc"] * len(row)
        elif row["dias_para_fim"] <= 20:
            return ["background-color: #fff2cc"] * len(row)
        return [""] * len(row)

    df = aplicar_filtros(df)

    st.dataframe(df.style.apply(destacar, axis=1), use_container_width=True)

# ---------------- DASHBOARD ----------------
def tela_dashboard():
    st.title("📊 Dashboard")

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM contratos", conn)
    conn.close()

    df = aplicar_filtros(df)

    st.metric("Total de Contratos", len(df))
    st.metric("Valor Mensal Total", f"R$ {df['vlr_mensal_atual'].sum():,.2f}")

    col1, col2 = st.columns(2)
    col1.bar_chart(df["servico_contratado"].value_counts())
    col2.bar_chart(df["uf"].value_counts())

# ---------------- FLUXO ----------------
if st.session_state.usuario is None:
    tela_login()
else:
    menu = st.sidebar.radio(
        "📂 Menu",
        ["Cadastro", "Visualização", "Dashboard"]
    )

    if menu == "Cadastro":
        tela_cadastro()
    elif menu == "Visualização":
        tela_visualizacao()
    else:
        tela_dashboard()
