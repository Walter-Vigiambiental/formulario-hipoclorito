import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from io import BytesIO
import yagmail
import os

st.set_page_config(page_title="Formulário Hipoclorito", page_icon="📦", layout="centered")
st.title("📦 Formulário de Entrega de Hipoclorito")

CSV_FILE = "entregas_hipoclorito.csv"
EMAIL_DESTINO_FIXO = "vigiambientalmochipoclorito@gmail.com"

def formatar_data(data):
    return data.strftime("%d/%m/%Y") if data else ""

def carregar_entregas():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE).to_dict(orient="records")
    return []

def salvar_entregas(entregas):
    df = pd.DataFrame(entregas)
    df.to_csv(CSV_FILE, index=False)

def gerar_pdf(entrega):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica", 12)
    c.drawString(100, 800, "📦 Registro de Entrega de Hipoclorito")
    y = 760
    for chave, valor in entrega.items():
        c.drawString(100, y, f"{chave}: {valor}")
        y -= 20
    c.save()
    buffer.seek(0)
    return buffer

def enviar_email(destinatario, pdf_buffer):
    try:
        yag = yagmail.SMTP("vigiambientalmochipoclorito@gmail.com", "SUA_SENHA_DE_APP")
        yag.send(
            to=destinatario,
            subject="📄 Registro de Entrega - Hipoclorito",
            contents="Segue em anexo o registro da entrega em PDF.",
            attachments={"registro_entrega.pdf": pdf_buffer}
        )
        yag.close()
        return True
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")
        return False

if "entregas" not in st.session_state:
    st.session_state.entregas = carregar_entregas()

localidades = [
    "Selecione uma localidade...",
    "Miralta", "Nova Esperança", "Santa Rosa", "Ermidinha",
    "Samambaia", "São Pedro da Garça", "Aparecida Mundo Novo",
    "Canto Engenho", "Santa Barbara", "Planalto Rural",
    "Ponta do Morro", "Sec. Vigilância em Saúde", "Defesa Civil"
]

with st.form("form_entrega"):
    col1, col2 = st.columns(2)
    with col1:
        quant_pactuada = st.number_input("Quant. Pactuada (Caixas)", min_value=0, step=1, format="%d")
    with col2:
        entregador = st.text_input("Entregador")

    col3, col4 = st.columns(2)
    with col3:
        localidade = st.selectbox("Localidade", localidades)
    with col4:
        data_entrega = st.date_input("Data de entrega", value=None, format="DD/MM/YYYY", key="data_entrega")

    col5, col6 = st.columns(2)
    with col5:
        quant_entregue = st.number_input("Quant. Entregue (Caixas)", min_value=0, step=1, format="%d")
    with col6:
        vencimento_a = st.date_input("Vencimento", value=None, format="DD/MM/YYYY", key="vencimento_a")

    col7, col8 = st.columns(2)
    with col7:
        saldo_remanescente = st.number_input("Saldo Remanescente (Caixas)", min_value=0, step=1, format="%d")
    with col8:
        vencimento_b = st.date_input("Vencimento", value=None, format="DD/MM/YYYY", key="vencimento_b")

    col9, col10 = st.columns(2)
    with col9:
        recebedor = st.text_input("Recebedor")
    with col10:
        observacoes = st.text_area("Observações")

    enviado = st.form_submit_button("📤 Registrar entrega")

    if enviado:
        entrega = {
            "Quant. Pactuada": int(quant_pactuada),
            "Entregador": entregador,
            "Localidade": localidade,
            "Data de entrega": formatar_data(data_entrega),
            "Quant. Entregue": int(quant_entregue),
            "Vencimento A": formatar_data(vencimento_a),
            "Saldo Remanescente": int(saldo_remanescente),
            "Vencimento B": formatar_data(vencimento_b),
            "Recebedor": recebedor,
            "Observações": observacoes,
            "Email destino": EMAIL_DESTINO_FIXO
        }

        st.session_state.entregas.append(entrega)
        salvar_entregas(st.session_state.entregas)

        pdf_buffer = gerar_pdf(entrega)
        if enviar_email(EMAIL_DESTINO_FIXO, pdf_buffer):
            st.success("✅ Entrega registrada e PDF enviado automaticamente para o e-mail do sistema!")

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
