import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import yagmail
import os
import socket

# Configuração da página
st.set_page_config(page_title="Formulário Hipoclorito", page_icon="📦", layout="centered")
st.title("📦 Formulário de Entrega de Hipoclorito")

CSV_FILE = "entregas_hipoclorito.csv"
EMAIL_DESTINO_FIXO = "vigiambientalmochipoclorito@gmail.com"
SENHA_EXCLUSAO = "hipoclorito2025"

campos_formulario = {
    "quant_pactuada": 0,
    "entregador": "",
    "localidade": "Selecione uma localidade...",
    "data_entrega": None,
    "quant_entregue": 0,
    "vencimento_a": None,
    "saldo_remanescente": 0,
    "vencimento_b": None,
    "recebedor": "",
    "observacoes": "",
    "enviado": False
}

for campo, valor in campos_formulario.items():
    if campo not in st.session_state:
        st.session_state[campo] = valor

def tem_conexao():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def formatar_data(data):
    return data.strftime("%d/%m/%Y") if data else ""

def carregar_entregas():
    if os.path.exists(CSV_FILE):
        try:
            return pd.read_csv(CSV_FILE).to_dict(orient="records")
        except pd.errors.EmptyDataError:
            return []
    return []

def salvar_entregas(entregas):
    pd.DataFrame(entregas).to_csv(CSV_FILE, index=False)

def gerar_pdf(entrega):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica", 12)
    c.drawString(100, 800, "📦 Registro de Entrega de Hipoclorito")
    y = 760
    for chave, valor in entrega.items():
        if chave != "enviado":
            c.drawString(100, y, f"{chave}: {valor}")
            y -= 20
    c.save()
    buffer.seek(0)
    return buffer

def enviar_email(destinatario, pdf_buffer):
    try:
        yag = yagmail.SMTP("vigiambientalmochipoclorito@gmail.com", "reyzteerwjszvnsl")
        with open("registro_entrega.pdf", "wb") as f:
            f.write(pdf_buffer.read())
        yag.send(
            to=destinatario,
            subject="📄 Registro de Entrega - Hipoclorito",
            contents="Segue em anexo o registro da entrega em PDF.",
            attachments="registro_entrega.pdf"
        )
        os.remove("registro_entrega.pdf")
        yag.close()
        return True
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")
        return False

if "entregas" not in st.session_state:
    st.session_state.entregas = carregar_entregas()

# Envio automático de pendentes
if tem_conexao():
    atualizou = False
    for entrega in st.session_state.entregas:
        if not entrega.get("enviado"):
            buffer_pdf = gerar_pdf(entrega)
            enviado_ok = enviar_email(entrega["Email destino"], buffer_pdf)
            if enviado_ok:
                entrega["enviado"] = True
                atualizou = True
    if atualizou:
        salvar_entregas(st.session_state.entregas)

if st.button("➕ Inserir Novo Lançamento"):
    for campo, valor in campos_formulario.items():
        st.session_state[campo] = valor
    st.rerun()

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
        st.number_input("Quant. Pactuada (Caixas)", min_value=0, step=1, format="%d", key="quant_pactuada")
    with col2:
        st.text_input("Entregador", key="entregador")

    col3, col4 = st.columns(2)
    with col3:
        st.selectbox("Localidade", localidades, key="localidade")
    with col4:
        st.date_input("Data de entrega", format="DD/MM/YYYY", key="data_entrega")

    col5, col6 = st.columns(2)
    with col5:
        st.number_input("Quant. Entregue (Caixas)", min_value=0, step=1, format="%d", key="quant_entregue")
    with col6:
        st.date_input("Vencimento", format="DD/MM/YYYY", key="vencimento_a")

    col7, col8 = st.columns(2)
    with col7:
        st.number_input("Saldo Remanescente (Caixas)", min_value=0, step=1, format="%d", key="saldo_remanescente")
    with col8:
        st.date_input("Vencimento", format="DD/MM/YYYY", key="vencimento_b")

    st.text_input("Recebedor", key="recebedor")
    st.text_area("Observações", key="observacoes")

    enviado = st.form_submit_button("📤 Registrar entrega")

    if enviado:
        erro = False

        if not st.session_state.data_entrega:
            erro = True
            st.error("❌ O campo 'Data de entrega' é obrigatório.")

        if st.session_state.quant_entregue > 0 and not st.session_state.vencimento_a:
            erro = True
            st.error("❌ Campo 'Vencimento' é obrigatório quando houver entrega.")

        if st.session_state.saldo_remanescente > 0 and not st.session_state.vencimento_b:
            erro = True
            st.error("❌ Campo 'Vencimento' é obrigatório quando houver saldo remanescente.")

        if not erro:
            entrega = {
                "Quant. Pactuada": int(st.session_state.quant_pactuada),
                "Entregador": st.session_state.entregador,
                "Localidade": st.session_state.localidade,
                "Data de entrega": formatar_data(st.session_state.data_entrega),
                "Quant. Entregue": int(st.session_state.quant_entregue),
                "Vencimento A": formatar_data(st.session_state.vencimento_a),
                "Saldo Remanescente": int(st.session_state.saldo_remanescente),
                "Vencimento B": formatar_data(st.session_state.vencimento_b),
                "Recebedor": st.session_state.recebedor,
                "Observações": st.session_state.observacoes,
                "Email destino": EMAIL_DESTINO_FIXO,
                "enviado": False
            }
            st.session_state.entregas.append(entrega)
            salvar_entregas(st.session_state.entregas)
            st.success("✅ Entrega registrada localmente. Será enviada por e-mail quando houver internet.")
