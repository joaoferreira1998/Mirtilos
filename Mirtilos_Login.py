import streamlit as st
import pandas as pd
from datetime import date
import os
import streamlit_authenticator as stauth  # type: ignore

# --- Autenticação ---
# Hashear palavras-passe
hashed_passwords = stauth.Hasher(['123', 'abc']).generate()

# Definições dos utilizadores
usernames = {
    'joao': {'name': 'João Ferreira', 'password': hashed_passwords()[0]},
    'ana': {'name': 'Ana Silva', 'password': hashed_passwords()[1]}
}

# Configuração do autenticador
authenticator = stauth.Authenticate(
    usernames,
    'auth_cookie', 'some_random_key', 30
)

# Login
nome, autenticado, username = authenticator.login("Login", "main")

if autenticado:
    st.success(f"Bem-vindo, {nome}!")

    # --- Nome do ficheiro por utilizador ---
    FICHEIRO = f'dados_{username}.csv'

    # --- Funções ---
    def carregar_dados():
        if os.path.exists(FICHEIRO):
            return pd.read_csv(FICHEIRO)
        else:
            return pd.DataFrame(columns=["Data", "Trabalhador", "Quilos", "Preço/kg", "Total"])

    def guardar_dados(df):
        df.to_csv(FICHEIRO, index=False)

    # --- Interface da app ---
    st.title("Gestão de Entregas de Mirtilos")

    st.subheader("Inserir nova entrega")
    with st.form("form_entrega"):
        trabalhador = st.text_input("Nome do trabalhador")
        data = st.date_input("Data da entrega", value=date.today())
        quilos = st.number_input("Quantidade (kg)", min_value=0.0, step=0.1)
        preco = st.number_input("Preço por kg (€)", min_value=0.0, step=0.1)
        submit = st.form_submit_button("Adicionar entrega")

    # Carregar dados
    df = carregar_dados()

    # Se submetido, adicionar nova linha
    if submit and trabalhador and quilos > 0 and preco > 0:
        total = round(quilos * preco, 2)
        nova_linha = pd.DataFrame([[data, trabalhador, quilos, preco, total]],
                                  columns=["Data", "Trabalhador", "Quilos", "Preço/kg", "Total"])
        df = pd.concat([df, nova_linha], ignore_index=True)
        guardar_dados(df)
        st.success(
            f"Entrega registada: {trabalhador} - {quilos}kg - {total:.2f}€")

    # Mostrar dados
    st.subheader("Registos de Entregas")
    st.dataframe(df)

    # Totais por trabalhador
    st.subheader("Totais por Trabalhador")
    if not df.empty:
        totais = df.groupby("Trabalhador")["Total"].sum().reset_index()
        st.table(totais)

    # Exportar
    st.download_button("Download CSV", df.to_csv(
        index=False), file_name=f"entregas_{username}.csv")

    # Logout
    authenticator.logout("Sair", "sidebar")

else:
    st.warning("Por favor, inicie sessão.")
