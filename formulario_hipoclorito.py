import streamlit as st
import pandas as pd
from datetime import date

# Dicionário de tradução de meses
meses_pt = {
    "January": "janeiro", "February": "fevereiro", "March": "março",
    "April": "abril", "May": "maio", "June": "junho",
    "July": "julho", "August": "agosto", "September": "setembro",
    "October": "outubro", "November": "novembro", "December": "dezembro"
}

st.set_page_config(page_title="Formulário Hipoclorito", page_icon="📦", layout="centered")
st.title("📦 Formulário de Entrega de Hipoclorito")

if "entregas" not in st.session_state:
    st.session_state.entregas = []

localidades = [
    "Selecione uma localidade...",
    "Miralta", "Nova Esperança", "Santa Rosa", "Ermidinha", "Samambaia",
    "São Pedro da Garça", "Aparecida Mundo Novo", "Canto Engenho",
    "Santa Barbara", "Planalto Rural", "Ponta do Morro",
    "Sec. Vigilância em Saúde", "Defesa Civil"
]

# Função para formatar data com mês em português
def formatar_data(data):
    mes_en = data.strftime("%B")
    mes_pt = meses_pt.get(mes_en, mes_en)
    return f"{data.day} de {mes_pt} de {data.year}"

with st.form("form_entrega"):
    col1, col2 = st.columns(2)
    with col1:
        data_entrega = st.date_input("Data de entrega")
        quant_pactuada = st.number_input("Quant. Pactuada (Caixas)", min_value=0, step=1, format="%d")
        quant_entregue = st.number_input("Quant. Entregue (Caixas)", min_value=0, step=1, format="%d")
        saldo_remanescente = st.number_input("Saldo Remanescente (Caixas)", min_value=0, step=1, format="%d")
        vencimento_entregue = st.date_input("Vencimento do produto entregue")
        vencimento_saldo = st.date_input("Vencimento do saldo remanescente")
    with col2:
        entregador = st.text_input("Entregador")
        recebedor = st.text_input("Recebedor")
        localidade = st.selectbox("Localidade", localidades)
        observacoes = st.text_area("Observações")

    enviado = st.form_submit_button("📤 Registrar entrega")
    if enviado:
        if localidade == "Selecione uma localidade...":
            st.error("⛔ Escolha uma localidade válida.")
        else:
            entrega = {
                "Data de entrega": formatar_data(data_entrega),
                "Quant. Pactuada": int(quant_pactuada),
                "Quant. Entregue": int(quant_entregue),
                "Saldo Remanescente": int(saldo_remanescente),
                "Vencimento do produto entregue": formatar_data(vencimento_entregue),
                "Vencimento do saldo remanescente": formatar_data(vencimento_saldo),
                "Entregador": entregador,
                "Recebedor": recebedor,
                "Localidade": localidade,
                "Observações": observacoes
            }
            st.session_state.entregas.append(entrega)
            st.success("✅ Entrega registrada com sucesso!")

if st.session_state.entregas:
    st.subheader("📄 Histórico de Entregas")
    df = pd.DataFrame(st.session_state.entregas)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Exportar para CSV",
        data=csv,
        file_name="entregas_hipoclorito.csv",
        mime="text/csv"
    )
else:
    st.info("Nenhuma entrega registrada ainda.")

st.markdown("---")
st.caption("Desenvolvido por Walter Alves com ❤️ usando Streamlit.")
