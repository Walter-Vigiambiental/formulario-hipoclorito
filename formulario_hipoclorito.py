import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Formulário Hipoclorito", page_icon="📦", layout="centered")
st.title("📦 Formulário de Entrega de Hipoclorito")

# Inicializa a lista de entregas
if "entregas" not in st.session_state:
    st.session_state.entregas = []

# Lista de localidades
localidades = [
    "Selecione uma localidade...",
    "Miralta",
    "Nova Esperança",
    "Santa Rosa",
    "Ermidinha",
    "Samambaia",
    "São Pedro da Garça",
    "Aparecida Mundo Novo",
    "Canto Engenho",
    "Santa Barbara",
    "Planalto Rural",
    "Ponta do Morro",
    "Sec. Vigilância em Saúde",
    "Defesa Civil"
]

def data_foi_alterada(data_selecionada):
    return data_selecionada.date() != datetime.today().date()

# Formulário
with st.form("form_entrega"):
    col1, col2 = st.columns(2)
    with col1:
        st.caption("📅 Selecione a data no calendário:")
        data_entrega = st.date_input("Data de entrega", value=datetime.today(), format="DD/MM/YYYY")
        quant_pactuada = st.number_input("Quant. Pactuada (Caixas)", min_value=0, step=1, format="%d")
        quant_entregue = st.number_input("Quant. Entregue (Caixas)", min_value=0, step=1, format="%d")
        saldo_remanescente = st.number_input("Saldo Remanescente (Caixas)", min_value=0, step=1, format="%d")
        vencimento_entregue = st.date_input("Vencimento do produto entregue", value=datetime.today(), format="DD/MM/YYYY")
        vencimento_saldo = st.date_input("Vencimento do saldo remanescente", value=datetime.today(), format="DD/MM/YYYY")
    with col2:
        entregador = st.text_input("Entregador")
        recebedor = st.text_input("Recebedor")
        localidade = st.selectbox("Localidade", localidades)
        observacoes = st.text_area("Observações")

    enviado = st.form_submit_button("📤 Registrar entrega")
    if enviado:
        if not data_foi_alterada(data_entrega):
            st.error("⛔ Por favor, selecione a data de entrega.")
        elif not data_foi_alterada(vencimento_entregue):
            st.error("⛔ Selecione o vencimento do produto entregue.")
        elif not data_foi_alterada(vencimento_saldo):
            st.error("⛔ Selecione o vencimento do saldo remanescente.")
        elif localidade == "Selecione uma localidade...":
            st.error("⛔ Selecione uma localidade válida.")
        else:
            entrega = {
                "Data de entrega": data_entrega.strftime("%d/%m/%Y"),
                "Quant. Pactuada": int(quant_pactuada),
                "Quant. Entregue": int(quant_entregue),
                "Saldo Remanescente": int(saldo_remanescente),
                "Vencimento do produto entregue": vencimento_entregue.strftime("%d/%m/%Y"),
                "Vencimento do saldo remanescente": vencimento_saldo.strftime("%d/%m/%Y"),
                "Entregador": entregador,
                "Recebedor": recebedor,
                "Localidade": localidade,
                "Observações": observacoes
            }
            st.session_state.entregas.append(entrega)
            st.success("✅ Entrega registrada com sucesso!")

# Histórico
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
st.caption("Desenvolvido por Walter Alves usando Streamlit.")
