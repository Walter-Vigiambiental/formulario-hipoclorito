import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Formulário Hipoclorito", page_icon="📦", layout="centered")
st.title("📦 Formulário de Entrega de Hipoclorito")

# Inicializa a lista de entregas
if "entregas" not in st.session_state:
    st.session_state.entregas = []

# Formulário
with st.form("form_entrega"):
    col1, col2 = st.columns(2)
    with col1:
        data_entrega = st.date_input("Data de entrega", value=datetime.today())
        quant_pactuada = st.number_input("Quant. Pactuada (Caixas)", min_value=0.0, step=0.1)
        quant_entregue = st.number_input("Quant. Entregue (Caixas)", min_value=0.0, step=0.1)
        saldo_remanescente = st.number_input("Saldo Remanescente (Caixas)", min_value=0.0, step=0.1)
        vencimento = st.date_input("Vencimento", value=datetime.today())
    with col2:
        entregador = st.text_input("Entregador")
        recebedor = st.text_input("Recebedor")
        localidade = st.text_input("Localidade")
        observacoes = st.text_area("Observações")

    enviado = st.form_submit_button("📤 Registrar entrega")
    if enviado:
        entrega = {
            "Data de entrega": data_entrega.strftime("%d/%m/%Y"),
            "Quant. Pactuada": quant_pactuada,
            "Quant. Entregue": quant_entregue,
            "Saldo Remanescente": saldo_remanescente,
            "Vencimento": vencimento.strftime("%d/%m/%Y"),
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
st.caption("Desenvolvido com ❤️ usando Streamlit.")
