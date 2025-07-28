import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import yagmail
import os

st.set_page_config(page_title="Formulário Hipoclorito", page_icon="📦", layout="centered")
st.title("📦 Formulário de Entrega de Hipoclorito")

CSV_FILE = "entregas_hipoclorito.csv"
EMAIL_DESTINO_FIXO = "vigiambientalmochipoclorito@gmail.com"
SENHA_EXCLUSAO = "hipoclorito2025"

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
    df = pd.DataFrame(entregas)
    df.to_csv(CSV_FILE, index=False)

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

        pares_de_campos = [
            ("Quant. Pactuada", "Entregador"),
            ("Localidade", "Data de entrega"),
            ("Quant. Entregue", "Vencimento A"),
            ("Saldo Remanescente", "Vencimento B"),
            ("Recebedor", "Observações"),
        ]

        for campo1, campo2 in pares_de_campos:
            valor1 = "" if pd.isna(entrega.get(campo1)) else str(entrega.get(campo1))
            valor2 = "" if pd.isna(entrega.get(campo2)) else str(entrega.get(campo2))
            c.drawString(80, y, f"{campo1}: {valor1}")
            c.drawString(300, y, f"{campo2}: {valor2}")
            y -= 15

        email_destino = "" if pd.isna(entrega.get("Email destino")) else str(entrega.get("Email destino"))
        c.drawString(80, y, f"Email destino: {email_destino}")
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

# ➕ Botão para limpar o formulário
if st.button("➕ Inserir Novo Lançamento"):
    campos_formulario = [
        "quant_pactuada", "entregador", "localidade", "data_entrega",
        "quant_entregue", "vencimento_a", "saldo_remanescente", "vencimento_b",
        "recebedor", "observacoes"
    ]
    for campo in campos_formulario:
        st.session_state[campo] = None if "data" in campo or "vencimento" in campo else ""
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
        quant_pactuada = st.number_input("Quant. Pactuada (Caixas)", min_value=0, step=1, format="%d", key="quant_pactuada")
    with col2:
        entregador = st.text_input("Entregador", key="entregador")
    col3, col4 = st.columns(2)
    with col3:
        localidade = st.selectbox("Localidade", localidades, key="localidade")
    with col4:
        data_entrega = st.date_input("Data de entrega", value=None, format="DD/MM/YYYY", key="data_entrega")
    col5, col6 = st.columns(2)
    with col5:
        quant_entregue = st.number_input("Quant. Entregue (Caixas)", min_value=0, step=1, format="%d", key="quant_entregue")
    with col6:
        vencimento_a = st.date_input("Vencimento", value=None, format="DD/MM/YYYY", key="vencimento_a")
    col7, col8 = st.columns(2)
    with col7:
        saldo_remanescente = st.number_input("Saldo Remanescente (Caixas)", min_value=0, step=1, format="%d", key="saldo_remanescente")
    with col8:
        vencimento_b = st.date_input("Vencimento", value=None, format="DD/MM/YYYY", key="vencimento_b")
    col9, col10 = st.columns(2)
    with col9:
        recebedor = st.text_input("Recebedor", key="recebedor")
    with col10:
        observacoes = st.text_area("Observações", key="observacoes")
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

    pdf_historico = gerar_pdf_historico(st.session_state.entregas)
    st.download_button(
        label="📥 Exportar Histórico em PDF",
        data=pdf_historico,
        file_name="historico_entregas_hipoclorito.pdf",
        mime="application/pdf"
    )

    st.subheader("🗑️ Gerenciar Lançamentos")

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

st.markdown("---")
st.caption("Desenvolvido por Walter Alves usando Streamlit.")


