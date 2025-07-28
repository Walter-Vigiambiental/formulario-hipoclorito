import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Inicializa os dados se não existirem
if "entregas" not in st.session_state:
    st.session_state.entregas = []

st.title("📦 Registro de Entregas de Hipoclorito")

# Formulário para nova entrega
with st.form("form_entrega"):
    data = st.date_input("Data da Entrega")
    quantidade = st.text_input("Quantidade Entregue")
    responsavel = st.text_input("Responsável pela Entrega")
    enviado_por = st.text_input("Enviado por")
    recebido_por = st.text_input("Recebido por")
    observacao = st.text_area("Observações", "")
    enviar = st.form_submit_button("Registrar Entrega")

    if enviar:
        nova_entrega = {
            "Data": data.strftime("%d/%m/%Y"),
            "Quantidade": quantidade,
            "Responsável": responsavel,
            "Enviado por": enviado_por,
            "Recebido por": recebido_por,
            "Observações": observacao
        }
        st.session_state.entregas.append(nova_entrega)
        st.success("Entrega registrada com sucesso!")

# Exibe tabela das entregas
if st.session_state.entregas:
    st.subheader("📋 Entregas Registradas")
    st.table(st.session_state.entregas)

    # Função para gerar o PDF
    def gerar_pdf(entregas):
        c = canvas.Canvas("registros_entregas.pdf", pagesize=A4)
        largura, altura = A4
        y = altura - 40

        for i, entrega in enumerate(entregas, 1):
            c.drawString(40, y, f"Entrega {i}:")
            y -= 20
            for campo, valor in entrega.items():
                c.drawString(60, y, f"{campo}: {valor}")
                y -= 15
            y -= 10
            if y < 50:
                c.showPage()
                y = altura - 40
        c.save()

    if st.button("📄 Exportar registros em PDF"):
        gerar_pdf(st.session_state.entregas)
        st.success("PDF gerado com sucesso! Verifique o arquivo 'registros_entregas.pdf' na pasta do app.")
else:
    st.info("Nenhuma entrega registrada ainda.")
