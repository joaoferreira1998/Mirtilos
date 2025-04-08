import streamlit as st
import pandas as pd
from datetime import date
import os
import streamlit_authenticator as stauth

# --- Configuração da página ---
st.set_page_config(page_title="Entregas de Mirtilos", layout="centered")

# --- Utilizadores ---
user_credentials = {
    'usernames': {
        'joao': {
            'name': 'João Ferreira',
            'password': stauth.Hasher(['123']).generate()[0]
        },
        'ana': {
            'name': 'Ana Silva',
            'password': stauth.Hasher(['abc']).generate()[0]
        }
    }
}

# --- Autenticação ---
authenticator = stauth.Authenticate(
    user_credentials,
    'mirtilos_app', 'abcdef', cookie_expiry_days=30
)

nome, autenticado, username = authenticator.login("Login", "main")

if autenticado:
    st.success(f"Bem-vindo, {nome} 👋")

    # Ficheiro específico por utilizador
    FICHEIRO = f'dados_{username}.csv'

    def carregar_dados():
        if os.path.exists(FICHEIRO):
            return pd.read_csv(FICHEIRO)
        else:
            return pd.DataFrame(columns=["Data", "Trabalhador", "Quilos", "Preço/kg", "Total"])

    def guardar_dados(df):
        df.to_csv(FICHEIRO, index=False)

    # Título
    st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>📦 Gestão de Entregas de Mirtilos</h1>",
                unsafe_allow_html=True)

    # Formulário de entrega
    st.markdown("### ➕ Nova Entrega")
    with st.form("form_entrega"):
        col1, col2 = st.columns(2)
        with col1:
            trabalhador = st.text_input("👷 Nome do trabalhador")
            data = st.date_input("📅 Data da entrega", value=date.today())
        with col2:
            quilos = st.number_input(
                "⚖️ Quantidade (kg)", min_value=0.0, step=0.1)
            preco = st.number_input(
                "💶 Preço por kg (€)", min_value=0.0, step=0.1)
        submit = st.form_submit_button("✅ Adicionar entrega")

    # Carrega os dados
    df = carregar_dados()

    # Adiciona nova entrega
    if submit and trabalhador and quilos > 0 and preco > 0:
        total = round(quilos * preco, 2)
        nova_linha = pd.DataFrame([[str(data), trabalhador, quilos, preco, total]],
                                  columns=["Data", "Trabalhador", "Quilos", "Preço/kg", "Total"])
        df = pd.concat([df, nova_linha], ignore_index=True)
        guardar_dados(df)
        st.success(
            f"Entrega registada com sucesso: {trabalhador} - {quilos}kg - {total:.2f}€")

    st.markdown("---")

    # Corrigir tipo da coluna "Data"
    if not df.empty:
        df["Data"] = df["Data"].astype(str)

    # Mostrar dados
    st.markdown("### 📋 Registos de Entregas")
    st.dataframe(df, use_container_width=True)

    # Totais por trabalhador
    st.markdown("### 📊 Totais por Trabalhador")
    if not df.empty:
        totais = df.groupby("Trabalhador")["Total"].sum().reset_index()
        st.table(totais)

    # Download CSV
    st.download_button(
        "⬇️ Download CSV",
        df.to_csv(index=False),
        file_name=f"entregas_{username}.csv"
    )

    # Logout
    authenticator.logout("Sair", "sidebar")

else:
    st.warning("Por favor, inicie sessão.")
