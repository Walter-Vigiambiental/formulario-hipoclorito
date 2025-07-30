import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import yagmail
import os

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
    "observacoes": ""
}

for campo, valor in campos_formulario.items():
    if campo not in st.session_state:
        st.session_state[campo] = valor

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
        c.drawString(100, y, f"{chave}: {valor}")
        y -= 20
    c.save()
    buffer.seek(0)
    return buffer

def gerar_pdf_historico(entregas):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(80, altura - 50, "📋 Histórico de Entregas de Hipoclorito")
    y = altura - 80
    for i, entrega in enumerate(entregas, start=1):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(80, y, f"Entrega {i}")
        y -= 15
        c.setFont("Helvetica", 11)
        for campo1, campo2 in [
            ("Quant. Pactuada", "Entregador"),
            ("Localidade", "Data de entrega"),
            ("Quant. Entregue", "Vencimento A"),
            ("Saldo Remanescente", "Vencimento B"),
            ("Recebedor", "Observações"),
        ]:
            valor1 = entrega.get(campo1, "")
            valor2 = entrega.get(campo2, "")
            c.drawString(80, y, f"{campo1}: {valor1}")
            c.drawString(300, y, f"{campo2}: {valor2}")
            y -= 15
        c.drawString(80, y, f"Email destino: {entrega.get('Email destino', '')}")
        y -= 25
        if y < 100:
            c.showPage()
            c.setFont("Helvetica-Bold", 14)
            c.drawString(80, altura - 50, "📋 Histórico de Entregas de Hipoclorito (continuação)")
            y = altura - 80
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
        st.date_input("Vencimento A", format="DD/MM/YYYY", key="vencimento_a")

    col7, col8 = st.columns(2)
    with col7:
        st.number_input("Saldo Remanescente (Caixas)", min_value=0, step=1, format="%d", key="saldo_remanescente")
    with col8:
        st.date_input("Vencimento B", format="DD/MM/YYYY", key="vencimento_b")

    col9, col10 = st.columns(2)
    with col9:
    st.text_input("Recebedor", key="recebedor")

    st.text_area("Observações", key="observacoes")

    with col10:
        st.text_area("Observações", key="observacoes")

    enviado = st.form_submit_button("📤 Registrar entrega")

    if enviado:
        erro = False

if not st.session_state.data_entrega:
    erro = True
    st.error("❌ O campo 'Data de entrega' é obrigatório.")

# Vencimento A obrigatório se houver entrega
if st.session_state.quant_entregue > 0 and not st.session_state.vencimento_a:
    erro = True
    st.error("❌ Campo 'Vencimento A' é obrigatório quando houver entrega.")

# Vencimento B obrigatório se houver saldo remanescente
if st.session_state.saldo_remanescente > 0 and not st.session_state.vencimento_b:
    erro = True
    st.error("❌ Campo 'Vencimento B' é obrigatório quando houver saldo remanescente.")

if not erro:
    # prossegue com o registro

        if not erro_vencimento:
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
                "Email destino": EMAIL_DESTINO_FIXO
            }
            st.session_state.entregas.append(entrega)
            salvar_entregas(st.session_state.entregas)
            buffer_pdf = gerar_pdf(entrega)
            enviado_ok = enviar_email(EMAIL_DESTINO_FIXO, buffer_pdf)
            if enviado_ok:
                st.success("✅ Entrega registrada e e-mail enviado com sucesso!")
            else:
                st.warning("⚠️ Entrega registrada, mas falha ao enviar o e-mail.")

st.subheader("🗑️ Gerenciar Lançamentos")
if st.session_state.entregas:
    for i, entrega in enumerate(st.session_state.entregas):
        with st.expander(f"Entrega {i + 1} - {entrega.get('Localidade', 'Sem local')}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                for chave, valor in entrega.items():
                    valor_formatado = "" if pd.isna(valor) else str(valor)
                    st.markdown(f"**{chave}:** {valor_formatado}")
            with col2:
                if st.button(f"🗑️ Excluir", key=f"del_{i}"):
                    senha = st.text_input("Digite a senha", type="password", key=f"senha_{i}")
                    if senha:
                        if senha == SENHA_EXCLUSAO:
                            st.session_state.entregas.pop(i)
                            salvar_entregas(st.session_state.entregas)
                            st.success("✅ Lançamento excluído com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Senha incorreta.")
else:
    st.info("Nenhuma entrega registrada ainda.")

st.subheader("📤 Exportar Histórico de Entregas")
pdf_historico = gerar_pdf_historico(st.session_state.entregas)
st.download_button(
    label="📥 Exportar Histórico em PDF",
    data=pdf_historico,
    file_name="historico_entregas_hipoclorito.pdf",
    mime="application/pdf"
)

st.markdown("---")
st.caption("Desenvolvido por Walter Alves usando Streamlit.")
