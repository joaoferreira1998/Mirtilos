import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Entregas de Mirtilos", layout="centered")

# --- Funções ---
def get_user_file(username):
    return f"entregas_{username}.csv"


def carregar_dados(username):
    file = get_user_file(username)
    if os.path.exists(file):
        return pd.read_csv(file)
    else:
        return pd.DataFrame(columns=["Data", "Trabalhador", "Quilos", "Preço/kg", "Total"])


def guardar_dados(df, username):
    # Arredondar para 2 casas decimais
    df["Quilos"] = df["Quilos"].round(2)
    df["Preço/kg"] = df["Preço/kg"].round(2)
    df["Total"] = df["Total"].round(2)
    # Guardar com encoding para Excel
    df.to_csv(get_user_file(username), index=False, encoding='utf-8-sig')


# --- Login Simples (pode ser melhorado depois) ---
st.markdown("<h1 style='text-align: center;'>🔐 Login do Gestor</h1>", unsafe_allow_html=True)
username = st.text_input("👤 Nome de utilizador", key="login_user")

if username:
    st.success(f"Bem-vindo, {username}!")

    # --- Cabeçalho ---
    st.markdown("<h2 style='text-align: center; color: #4B8BBE;'>📦 Gestão de Entregas de Mirtilos</h2>",
                unsafe_allow_html=True)

    df = carregar_dados(username)

    # --- Formulário de Nova Entrega ---
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

    if submit and trabalhador and quilos > 0 and preco > 0:
        total = round(quilos * preco, 2)
        nova_linha = pd.DataFrame([[data, trabalhador, quilos, preco, total]],
                                  columns=["Data", "Trabalhador", "Quilos", "Preço/kg", "Total"])
        df = pd.concat([df, nova_linha], ignore_index=True)
        guardar_dados(df, username)
        st.success(f"Entrega registada com sucesso: {trabalhador} - {quilos}kg - {total:.2f}€")

    st.markdown("---")

    # --- Mostrar Dados ---
    st.markdown("### 📋 Registos de Entregas")
    st.dataframe(df, use_container_width=True)

    # --- Resumo por Trabalhador ---
    st.markdown("### 📊 Totais por Trabalhador")
    if not df.empty:
        resumo = df.groupby("Trabalhador")[["Quilos", "Total"]].sum().reset_index()
        resumo["Quilos"] = resumo["Quilos"].round(2)
        resumo["Total"] = resumo["Total"].round(2)
        st.dataframe(resumo, use_container_width=True)

    # --- Botão de Exportação ---
    st.download_button("⬇️ Download CSV", df.to_csv(index=False, encoding='utf-8-sig'),
                       file_name=f"entregas_{username}.csv")

    # --- Opção de Limpar os Dados ---
    st.markdown("### ⚠️ Limpar Dados")
    if st.button("🗑️ Eliminar todos os dados deste gestor"):
        if st.checkbox("❗ Confirmo que quero apagar todos os dados"):
            os.remove(get_user_file(username))
            st.success("✅ Dados eliminados com sucesso. Recarregue a página.")
            st.stop()

else:
    st.warning("Por favor, introduza o seu nome de utilizador para começar.")

