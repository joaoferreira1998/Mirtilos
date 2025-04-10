import streamlit as st
import pandas as pd
import hashlib
from datetime import date
import os

st.set_page_config(page_title="Gestão de Entregas", layout="centered")

# Diretórios e ficheiros
UTILIZADORES_FILE = "utilizadores.csv"

# Criação de ficheiro de utilizadores se não existir
if not os.path.exists(UTILIZADORES_FILE):
    pd.DataFrame(columns=["username", "nome", "password"]).to_csv(UTILIZADORES_FILE, index=False)


# Funções de autenticação
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def validar_login(username, password):
    utilizadores = pd.read_csv(UTILIZADORES_FILE)
    utilizador = utilizadores[utilizadores["username"] == username]
    if not utilizador.empty:
        return hash_password(password) == utilizador.iloc[0]["password"]
    return False


def registar_utilizador(nome, username, password):
    utilizadores = pd.read_csv(UTILIZADORES_FILE)
    if username in utilizadores["username"].values:
        return False
    novo_utilizador = pd.DataFrame([[username, nome, hash_password(password)]],
                                   columns=["username", "nome", "password"])
    utilizadores = pd.concat([utilizadores, novo_utilizador], ignore_index=True)
    utilizadores.to_csv(UTILIZADORES_FILE, index=False)
    return True


# Interface de Login e Registo
menu = st.sidebar.selectbox("Acesso", ["Login", "Registar"])

if menu == "Registar":
    st.sidebar.markdown("### Criar conta")
    nome_reg = st.sidebar.text_input("Nome completo")
    user_reg = st.sidebar.text_input("Nome de utilizador")
    pass_reg = st.sidebar.text_input("Palavra-passe", type="password")
    if st.sidebar.button("Criar conta"):
        if nome_reg and user_reg and pass_reg:
            if registar_utilizador(nome_reg, user_reg, pass_reg):
                st.sidebar.success("Conta criada com sucesso! Faça login.")
            else:
                st.sidebar.error("Nome de utilizador já existe.")
        else:
            st.sidebar.warning("Preencha todos os campos.")

# LOGIN
login_sucesso = False
username = None

if menu == "Login":
    st.sidebar.markdown("### Login")
    username = st.sidebar.text_input("Utilizador")
    password = st.sidebar.text_input("Palavra-passe", type="password")
    if st.sidebar.button("Entrar"):
        if validar_login(username, password):
            st.session_state["login"] = True
            st.session_state["user"] = username
            st.success(f"Bem-vindo {username}!")
            login_sucesso = True
        else:
            st.error("Credenciais inválidas!")

if st.session_state.get("login") or login_sucesso:
    username = st.session_state["user"]
    FICHEIRO = f"dados_{username}.csv"

    def carregar_dados():
        if os.path.exists(FICHEIRO):
            return pd.read_csv(FICHEIRO)
        else:
            return pd.DataFrame(columns=["Data", "Trabalhador", "Quilos", "Preço/kg", "Total"])

    def guardar_dados(df):
        df.to_csv(FICHEIRO, index=False)

    st.markdown(f"<h1 style='text-align: center; color: #4B8BBE;'>📦 Entregas de Mirtilos</h1>", unsafe_allow_html=True)

    st.markdown("### ➕ Nova Entrega")
    with st.form("form_entrega"):
        col1, col2 = st.columns(2)
        with col1:
            trabalhador = st.text_input("👷 Nome do trabalhador")
            data = st.date_input("📅 Data da entrega", value=date.today())
        with col2:
            quilos = st.number_input("⚖️ Quantidade (kg)", min_value=0.0, step=0.1)
            preco = st.number_input("💶 Preço por kg (€)", min_value=0.0, step=0.1)
        submit = st.form_submit_button("✅ Adicionar entrega")

    df = carregar_dados()

    if submit and trabalhador and quilos > 0 and preco > 0:
        total = round(quilos * preco, 2)
        nova_linha = pd.DataFrame([[data, trabalhador, round(quilos, 2), round(preco, 2), total]],
                                  columns=["Data", "Trabalhador", "Quilos", "Preço/kg", "Total"])
        df = pd.concat([df, nova_linha], ignore_index=True)
        guardar_dados(df)
        st.success(f"Entrega registada: {trabalhador} - {quilos}kg - {total:.2f}€")

    # Arredondar colunas
    df["Quilos"] = df["Quilos"].round(2)
    df["Preço/kg"] = df["Preço/kg"].round(2)
    df["Total"] = df["Total"].round(2)

    st.markdown("---")
    st.markdown("### 📋 Registos de Entregas")
    st.dataframe(df, use_container_width=True)

    st.markdown("### 📊 Totais por Trabalhador")
    if not df.empty:
        resumo = df.groupby("Trabalhador")[["Quilos", "Total"]].sum().reset_index()
        resumo["Quilos"] = resumo["Quilos"].round(2)
        resumo["Total"] = resumo["Total"].round(2)
        st.dataframe(resumo)

    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button(
            "⬇️ Download CSV",
            df.to_csv(index=False, sep=';', encoding="utf-8-sig"),
            file_name=f"entregas_{username}.csv"
        )

    with col_b:
        if st.button("🗑️ Limpar Todos os Dados"):
            if st.confirm("Tem a certeza que quer eliminar todos os dados? Esta ação é irreversível."):
                os.remove(FICHEIRO)
                st.success("Dados eliminados com sucesso.")
                st.experimental_rerun()
else:
    st.info("Faça login para aceder à aplicação.")


