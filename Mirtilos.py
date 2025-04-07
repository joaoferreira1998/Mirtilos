import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Entregas de Mirtilos", layout="centered")

FICHEIRO = 'dados_entregas.csv'


def carregar_dados():
    if os.path.exists(FICHEIRO):
        return pd.read_csv(FICHEIRO)
    else:
        return pd.DataFrame(columns=["Data", "Trabalhador", "Quilos", "Preço/kg", "Total"])


def guardar_dados(df):
    df.to_csv(FICHEIRO, index=False)


# Cabeçalho
st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>📦 Gestão de Entregas de Mirtilos</h1>",
            unsafe_allow_html=True)

# Formulário
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
    nova_linha = pd.DataFrame([[data, trabalhador, quilos, preco, total]],
                              columns=["Data", "Trabalhador", "Quilos", "Preço/kg", "Total"])
    df = pd.concat([df, nova_linha], ignore_index=True)
    guardar_dados(df)
    st.success(
        f"Entrega registada com sucesso: {trabalhador} - {quilos}kg - {total:.2f}€")

# Separador visual
st.markdown("---")

# Mostrar os dados
st.markdown("### 📋 Registos de Entregas")
st.dataframe(df, use_container_width=True)

# Totais
st.markdown("### 📊 Totais por Trabalhador")
if not df.empty:
    totais = df.groupby("Trabalhador")["Total"].sum().reset_index()
    st.table(totais)

# Exportação
st.download_button("⬇️ Download CSV", df.to_csv(
    index=False), file_name="entregas_mirtilos.csv")
