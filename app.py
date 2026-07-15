import streamlit as st
import pandas as pd
from datetime import datetime
import os
import smtplib
import random
from email.mime.text import MIMEText

# 1. Configuração da Página
st.set_page_config(page_title="Gilka Campos Bordados", page_icon="🪡", layout="wide")

# ----------------------------------------
# CONFIGURAÇÃO DE E-MAIL (REMETENTE)
# ----------------------------------------
# VOCÊ PRECISA PREENCHER AQUI COM SEU E-MAIL E SENHA DE APLICATIVO DO GMAIL
EMAIL_REMETENTE = "natanaelcampossilva2006@gmail.com" 
SENHA_APP = "ezuhuoqmlbdfiqwo"

def enviar_codigo_email(email_destino, codigo):
    try:
        msg = MIMEText(f"Olá! Seu código de verificação para o sistema Gilka Bordados é: {codigo}")
        msg['Subject'] = 'Código de Verificação - Gilka Bordados'
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = email_destino

        # Conecta ao servidor do Gmail
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_REMETENTE, SENHA_APP)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False

# ----------------------------------------
# CONFIGURAÇÃO DE ARQUIVOS LOCAIS
# ----------------------------------------
PASTA_DRIVE = "dados_sistema"
os.makedirs(PASTA_DRIVE, exist_ok=True) # Cria a pasta se não existir

ARQ_ESTOQUE = f"{PASTA_DRIVE}/estoque.csv"
ARQ_VENDAS = f"{PASTA_DRIVE}/vendas.csv"
ARQ_FINANCEIRO = f"{PASTA_DRIVE}/financeiro.csv"
ARQ_USUARIOS = f"{PASTA_DRIVE}/usuarios.csv" # NOVO ARQUIVO DE USUÁRIOS

# Funções para Salvar e Carregar dados
def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo).to_dict('records')
    return []

def salvar_dados(dados, arquivo):
    df = pd.DataFrame(dados)
    df.to_csv(arquivo, index=False)

# 2. Inicialização do Banco de Dados Permanentemente
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = ""
if 'estoque' not in st.session_state:
    st.session_state.estoque = carregar_dados(ARQ_ESTOQUE)
if 'vendas' not in st.session_state:
    st.session_state.vendas = carregar_dados(ARQ_VENDAS)
if 'financeiro' not in st.session_state:
    st.session_state.financeiro = carregar_dados(ARQ_FINANCEIRO)
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = carregar_dados(ARQ_USUARIOS)
    # Se não tiver nenhum usuário, cria o usuário padrão "gilka"
    if len(st.session_state.usuarios) == 0:
        st.session_state.usuarios.append({'email': 'admin', 'usuario': 'gilka', 'senha': '123'})
        salvar_dados(st.session_state.usuarios, ARQ_USUARIOS)

# Variáveis de controle para a tela de cadastro
if 'etapa_cadastro' not in st.session_state:
    st.session_state.etapa_cadastro = 1
if 'codigo_gerado' not in st.session_state:
    st.session_state.codigo_gerado = ""
if 'email_temp' not in st.session_state:
    st.session_state.email_temp = ""

# 3. Tela de Login e Cadastro
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🪡 Gilka Bordados</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: gray;'>Acesso Restrito</h4>", unsafe_allow_html=True)
        
        aba_login, aba_cadastro = st.tabs(["🔐 Entrar", "📝 Cadastrar Novo Usuário"])

        # ABA DE LOGIN
        with aba_login:
            st.write("Faça login para acessar o sistema:")
            usuario = st.text_input("👤 Usuário")
            senha = st.text_input("🔑 Senha", type="password")

            if st.button("Entrar no Sistema", type="primary", use_container_width=True):
                login_sucesso = False
                for usr in st.session_state.usuarios:
                    if str(usr['usuario']) == usuario and str(usr['senha']) == senha:
                        login_sucesso = True
                        break
                
                if login_sucesso:
                    st.session_state.logado = True
                    st.session_state.usuario_logado = usuario
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos!")

        # ABA DE CADASTRO
        with aba_cadastro:
            # Etapa 1: Pedir E-mail e Enviar Código
            if st.session_state.etapa_cadastro == 1:
                st.write("Digite seu e-mail para receber um código de validação:")
                email_input = st.text_input("📧 Seu E-mail")
                
                if st.button("Enviar Código", use_container_width=True):
                    if "@" in email_input and "." in email_input:
                        # Gera um código de 6 dígitos
                        codigo = str(random.randint(100000, 999999))
                        st.session_state.codigo_gerado = codigo
                        st.session_state.email_temp = email_input
                        
                        # --- PARA TESTES --- 
                        # Se você não configurar o email ali em cima, o sistema falha. 
                        # Para você testar ANTES de configurar o e-mail real, eu mostro o código na tela de sucesso.
                        sucesso_email = enviar_codigo_email(email_input, codigo)
                        
                        if sucesso_email:
                            st.success(f"Código enviado para {email_input}!")
                            st.session_state.etapa_cadastro = 2
                            st.rerun()
                        else:
                            st.warning(f"Erro ao enviar e-mail. Para testes, seu código é: {codigo}")
                            # Avança mesmo dando erro apenas para você conseguir testar o sistema
                            st.session_state.etapa_cadastro = 2 
                    else:
                        st.error("Por favor, digite um e-mail válido.")

            # Etapa 2: Validar o Código
            elif st.session_state.etapa_cadastro == 2:
                st.info(f"Um código de 6 dígitos foi enviado para: {st.session_state.email_temp}")
                codigo_digitado = st.text_input("🔢 Digite o Código", max_chars=6)
                
                col_voltar, col_avancar = st.columns(2)
                if col_voltar.button("⬅️ Voltar"):
                    st.session_state.etapa_cadastro = 1
                    st.rerun()
                    
                if col_avancar.button("Validar Código", type="primary"):
                    if codigo_digitado == st.session_state.codigo_gerado:
                        st.success("Código Validado!")
                        st.session_state.etapa_cadastro = 3
                        st.rerun()
                    else:
                        st.error("❌ Código Incorreto!")

            # Etapa 3: Criar Usuário e Senha
            elif st.session_state.etapa_cadastro == 3:
                st.write("Código validado! Agora crie seu acesso:")
                novo_usuario = st.text_input("👤 Defina um Nome de Usuário")
                nova_senha = st.text_input("🔑 Defina uma Senha", type="password")
                
                if st.button("Finalizar Cadastro", type="primary", use_container_width=True):
                    if novo_usuario and nova_senha:
                        # Salva o novo usuário na lista e no arquivo
                        st.session_state.usuarios.append({
                            'email': st.session_state.email_temp, 
                            'usuario': novo_usuario, 
                            'senha': nova_senha
                        })
                        salvar_dados(st.session_state.usuarios, ARQ_USUARIOS)
                        
                        st.success("✅ Cadastro concluído! Vá para a aba 'Entrar' e faça login.")
                        st.session_state.etapa_cadastro = 1 # Reseta para o próximo que for cadastrar
                    else:
                        st.error("Preencha todos os campos!")
# ... (resto do seu código da Etapa 3) ...
                if st.button("Finalizar Cadastro", type="primary", use_container_width=True):
                    if novo_usuario and nova_senha:
                        # Salva o novo usuário na lista e no arquivo
                        st.session_state.usuarios.append({
                            'email': st.session_state.email_temp, 
                            'usuario': novo_usuario, 
                            'senha': nova_senha
                        })
                        salvar_dados(st.session_state.usuarios, ARQ_USUARIOS)
                        
                        st.success("✅ Cadastro concluído! Vá para a aba 'Entrar' e faça login.")
                        st.session_state.etapa_cadastro = 1 # Reseta para o próximo que for cadastrar
                    else:
                        st.error("Preencha todos os campos!")
        st.markdown("""
            <div style='text-align: center; margin-top: 50px;'>
                <p style='font-family: "Courier New", Courier, monospace; font-size: 13px; color: #888888; letter-spacing: 0.5px;'>
                    Desenvolvido por <span style='font-weight: bold; color: #ff4b4b;'>N.campos soluções</span>
                </p>
            </div>
        """, unsafe_allow_html=True)
        # -------------------------------------------------------------

# 4. Sistema Principal
else:
    st.sidebar.title("🪡 Menu Principal")
# 4. Sistema Principal
else:
    st.sidebar.title("🪡 Menu Principal")
    menu = ["📦 Estoque", "💰 Vendas / Pedidos", "📊 Financeiro"]
    escolha = st.sidebar.radio("Navegue por aqui:", menu)

    st.sidebar.divider()
    st.sidebar.write(f"👤 Usuário logado: **{st.session_state.usuario_logado.capitalize()}**")
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state.logado = False
        st.rerun()

    # ----------------------------------------
    # MÓDULO 1: ESTOQUE
    # ----------------------------------------
    if escolha == "📦 Estoque":
        st.header("Gestão de Estoque")
        aba1, aba2 = st.tabs(["➕ Cadastrar Item", "📋 Ver Estoque Atual"])

        with aba1:
            categoria = st.radio("Selecione o tipo de cadastro:", ["Peça Pronta", "Material"], horizontal=True)
            st.divider()

            if categoria == "Peça Pronta":
                with st.form("form_peca", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    produto = col1.text_input("Nome da Peça")
                    tamanho = col2.text_input("Tamanho (Ex: P, M, Único)")

                    col3, col4 = st.columns(2)
                    valor = col3.number_input("Valor (R$)", min_value=0.0, step=0.5, format="%.2f")
                    disponibilidade = col4.number_input("Disponibilidade (Quantidade)", min_value=0, step=1)

                    submit_peca = st.form_submit_button("Cadastrar Peça Pronta", type="primary")

                    if submit_peca and produto:
                        st.session_state.estoque.append({
                            'Categoria': 'Peça Pronta', 'Produto': produto,
                            'Tamanho': tamanho, 'Valor (R$)': valor, 'Quantidade': disponibilidade,
                            'Cor': '-', 'Metragem': '-', 'Foto': '-'
                        })
                        salvar_dados(st.session_state.estoque, ARQ_ESTOQUE)
                        st.success(f"✅ Peça '{produto}' salva!")

            elif categoria == "Material":
                with st.form("form_material", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    produto = col1.text_input("Nome do Material")
                    cor = col2.text_input("Cor")

                    col3, col4 = st.columns(2)
                    metragem = col3.number_input("Metragem (Metros)", min_value=0.0, step=0.1)
                    foto = col4.file_uploader("Foto do Material", type=["png", "jpg", "jpeg"])

                    submit_material = st.form_submit_button("Cadastrar Material", type="primary")

                    if submit_material and produto:
                        nome_foto = foto.name if foto is not None else "Sem foto"
                        st.session_state.estoque.append({
                            'Categoria': 'Material', 'Produto': produto,
                            'Tamanho': '-', 'Valor (R$)': '-', 'Quantidade': '-',
                            'Cor': cor, 'Metragem': metragem, 'Foto': nome_foto
                        })
                        salvar_dados(st.session_state.estoque, ARQ_ESTOQUE)
                        st.success(f"✅ Material '{produto}' salvo!")

        with aba2:
            st.subheader("Itens Cadastrados")
            if st.session_state.estoque:
                df_estoque = pd.DataFrame(st.session_state.estoque)
                st.dataframe(df_estoque, use_container_width=True)
            else:
                st.info("Seu estoque está vazio.")

    # ----------------------------------------
    # MÓDULO 2: VENDAS E PEDIDOS
    # ----------------------------------------
    elif escolha == "💰 Vendas / Pedidos":
        st.header("Gestão de Vendas e Pedidos")
        aba1, aba2 = st.tabs(["🛒 Registrar Novo Pedido", "🧾 Histórico"])

        with aba1:
            with st.form("form_vendas", clear_on_submit=True):
                col_a, col_b = st.columns(2)
                nome_cliente = col_a.text_input("Nome do Cliente")
                data_entrega = col_b.date_input("Data de Entrega")

                st.divider()
                produto_vendido = st.text_input("Produto/Serviço Encomendado")

                col_c, col_d = st.columns(2)
                qtd_vendida = col_c.number_input("Quantidade", min_value=1, step=1)
                valor_total = col_d.number_input("Valor Total (R$)", min_value=0.0, step=0.5, format="%.2f")

                submit_venda = st.form_submit_button("Concluir Venda/Pedido", type="primary")

                if submit_venda and nome_cliente and produto_vendido:
                    data_venda = datetime.now().strftime("%d/%m/%Y %H:%M")

                    st.session_state.vendas.append({
                        'Data': data_venda, 'Cliente': nome_cliente,
                        'Produto': produto_vendido, 'Qtd': qtd_vendida,
                        'Total (R$)': valor_total, 'Entrega': data_entrega.strftime("%d/%m/%Y")
                    })
                    salvar_dados(st.session_state.vendas, ARQ_VENDAS)

                    st.session_state.financeiro.append({
                        'Data': data_venda, 'Tipo': 'Entrada',
                        'Descrição': f"Pedido: {produto_vendido} ({nome_cliente})", 'Valor (R$)': valor_total
                    })
                    salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO)

                    st.success(f"✅ Pedido salvo! (R$ {valor_total:.2f})")

        with aba2:
            if st.session_state.vendas:
                df_vendas = pd.DataFrame(st.session_state.vendas)
                st.dataframe(df_vendas, use_container_width=True)
            else:
                st.info("Nenhuma venda ou pedido realizado ainda.")

    # ----------------------------------------
    # MÓDULO 3: FINANCEIRO
    # ----------------------------------------
    elif escolha == "📊 Financeiro":
        st.header("Gestão Financeira")

        receitas = sum(float(i['Valor (R$)']) for i in st.session_state.financeiro if i['Tipo'] == 'Entrada')
        despesas = sum(float(i['Valor (R$)']) for i in st.session_state.financeiro if i['Tipo'] == 'Saída')
        saldo = receitas - despesas

        col1, col2, col3 = st.columns(3)
        col1.metric("Entradas (Receitas)", f"R$ {receitas:.2f}")
        col2.metric("Saídas (Despesas)", f"R$ {despesas:.2f}")
        col3.metric("Saldo Atual", f"R$ {saldo:.2f}", delta=f"R$ {saldo:.2f}", delta_color="normal")

        st.divider()
        aba1, aba2 = st.tabs(["💸 Lançar Despesa", "📈 Extrato Completo"])

        with aba1:
            with st.form("form_despesas", clear_on_submit=True):
                desc_despesa = st.text_input("Descrição da Despesa")
                valor_despesa = st.number_input("Valor (R$)", min_value=0.01, step=0.5, format="%.2f")
                submit_despesa = st.form_submit_button("Registrar Despesa", type="primary")

                if submit_despesa and desc_despesa:
                    st.session_state.financeiro.append({
                        'Data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                        'Tipo': 'Saída', 'Descrição': desc_despesa, 'Valor (R$)': valor_despesa
                    })
                    salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO)
                    st.success("✅ Despesa salva com sucesso!")

        with aba2:
            if st.session_state.financeiro:
                df_financeiro = pd.DataFrame(st.session_state.financeiro)
                st.dataframe(df_financeiro, use_container_width=True)
            else:
                st.info("Nenhuma movimentação financeira.")
