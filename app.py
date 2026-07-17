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
EMAIL_REMETENTE = "natanaelcampossilva2006@gmail.com" 
SENHA_APP = "bwpagsnxwcsxhlsm"

def enviar_codigo_email(email_destino, codigo):
    try:
        msg = MIMEText(f"Olá! Seu código de verificação para o sistema Gilka Bordados é: {codigo}")
        msg['Subject'] = 'Código de Verificação - Gilka Bordados'
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = email_destino

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
os.makedirs(PASTA_DRIVE, exist_ok=True) 

ARQ_ESTOQUE = f"{PASTA_DRIVE}/estoque.csv"
ARQ_VENDAS = f"{PASTA_DRIVE}/vendas.csv"
ARQ_FINANCEIRO = f"{PASTA_DRIVE}/financeiro.csv"
ARQ_USUARIOS = f"{PASTA_DRIVE}/usuarios.csv" 

def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo).to_dict('records')
    return []

def salvar_dados(dados, arquivo):
    df = pd.DataFrame(dados)
    df.to_csv(arquivo, index=False)

# Função para evitar erros de cálculo com dados antigos que usavam "-"
def converter_valor(valor):
    try:
        return float(valor)
    except:
        return 0.0

# 2. Inicialização do Banco de Dados
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
    # ALTERAÇÃO: Definição do administrador padrão com 'admin' e '12347'
    if len(st.session_state.usuarios) == 0:
        st.session_state.usuarios.append({'email': 'admin@gilkabordados.com', 'usuario': 'admin', 'senha': '12347'})
        salvar_dados(st.session_state.usuarios, ARQ_USUARIOS)

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

        with aba_login:
            st.write("Faça login para acessar o sistema:")
            usuario = st.text_input("👤 Usuário")
            senha = st.text_input("🔑 Senha", type="password")

            # ALTERAÇÃO: Botão alterado de "Entrar no Sistema" para "Entrar"
            if st.button("Entrar", type="primary", use_container_width=True):
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

        with aba_cadastro:
            if st.session_state.etapa_cadastro == 1:
                st.write("Digite seu e-mail para receber um código de validação:")
                email_input = st.text_input("📧 Seu E-mail")
                
                if st.button("Enviar Código", type="primary", use_container_width=True):
                    if "@" in email_input and "." in email_input:
                        codigo = str(random.randint(100000, 999999))
                        st.session_state.codigo_gerado = codigo
                        st.session_state.email_temp = email_input
                        
                        sucesso_email = enviar_codigo_email(email_input, codigo)
                        
                        if sucesso_email:
                            st.success(f"Código enviado para {email_input}!")
                            st.session_state.etapa_cadastro = 2
                            st.rerun()
                        else:
                            st.warning(f"Erro ao enviar e-mail. Para testes, seu código é: {codigo}")
                            st.session_state.etapa_cadastro = 2 
                    else:
                        st.error("Por favor, digite um e-mail válido.")

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

            elif st.session_state.etapa_cadastro == 3:
                st.write("Código validado! Agora crie seu acesso:")
                novo_usuario = st.text_input("👤 Defina um Nome de Usuário")
                nova_senha = st.text_input("🔑 Defina uma Senha", type="password")
                
                if st.button("Finalizar Cadastro", type="primary", use_container_width=True):
                    if novo_usuario and nova_senha:
                        st.session_state.usuarios.append({
                            'email': st.session_state.email_temp, 
                            'usuario': novo_usuario, 
                            'senha': nova_senha
                        })
                        salvar_dados(st.session_state.usuarios, ARQ_USUARIOS)
                        st.success("✅ Cadastro concluído! Vá para a aba 'Entrar' e faça login.")
                        st.session_state.etapa_cadastro = 1 
                    else:
                        st.error("Preencha todos os campos!")

        st.markdown("""
            <div style='text-align: center; margin-top: 50px;'>
                <p style='font-family: "Courier New", Courier, monospace; font-size: 13px; color: #888888; letter-spacing: 0.5px;'>
                    Desenvolvido por <span style='font-weight: bold; color: #ff4b4b;'>N.campos soluções</span>
                </p>
            </div>
        """, unsafe_allow_html=True)

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
                    valor = col3.number_input("Valor de Venda (R$)", min_value=0.0, step=0.5, format="%.2f")
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
                    produto = col1.text_input("Nome do Material / Insumo")
                    cor = col2.text_input("Cor")

                    col3, col4, col5 = st.columns(3)
                    metragem = col3.number_input("Metragem/Qtd", min_value=0.0, step=0.1)
                    valor_material = col4.number_input("Valor de Custo Total (R$)", min_value=0.0, step=0.5, format="%.2f")
                    foto = col5.file_uploader("Foto do Material", type=["png", "jpg", "jpeg"])

                    submit_material = st.form_submit_button("Cadastrar Material", type="primary")

                    if submit_material and produto:
                        nome_foto = foto.name if foto is not None else "Sem foto"
                        st.session_state.estoque.append({
                            'Categoria': 'Material', 'Produto': produto,
                            'Tamanho': '-', 'Valor (R$)': valor_material, 'Quantidade': '-',
                            'Cor': cor, 'Metragem': metragem, 'Foto': nome_foto
                        })
                        salvar_dados(st.session_state.estoque, ARQ_ESTOQUE)
                        st.success(f"✅ Material '{produto}' salvo!")

        with aba2:
            if st.session_state.estoque:
                df_estoque = pd.DataFrame(st.session_state.estoque)
                
                st.subheader("👗 Peças Prontas Disponíveis")
                df_pecas = df_estoque[df_estoque['Categoria'] == 'Peça Pronta']
                if not df_pecas.empty:
                    st.dataframe(df_pecas, use_container_width=True)
                else:
                    st.info("Nenhuma peça pronta no estoque.")
                
                st.divider()

                st.subheader("🧵 Materiais e Insumos")
                df_materiais = df_estoque[df_estoque['Categoria'] == 'Material']
                if not df_materiais.empty:
                    st.dataframe(df_materiais, use_container_width=True)
                else:
                    st.info("Nenhum material cadastrado no estoque.")
            else:
                st.info("Seu estoque está vazio.")

    # ----------------------------------------
    # MÓDULO 2: VENDAS E PEDIDOS
    # ----------------------------------------
    elif escolha == "💰 Vendas / Pedidos":
        st.header("Gestão de Vendas e Pedidos")
        aba1, aba2 = st.tabs(["🛒 Novo Registro", "🧾 Histórico"])

        with aba1:
            tipo_registro = st.radio("O que você deseja registrar?", ["Venda de Estoque (Pronta Entrega)", "Novo Pedido (Encomenda)"], horizontal=True)
            st.divider()

            if tipo_registro == "Venda de Estoque (Pronta Entrega)":
                pecas_disponiveis = [item for item in st.session_state.estoque if item['Categoria'] == 'Peça Pronta' and str(item['Quantidade']).isdigit() and int(item['Quantidade']) > 0]
                
                if not pecas_disponiveis:
                    st.warning("⚠️ Não há peças prontas com estoque disponível no momento.")
                else:
                    with st.form("form_venda_estoque", clear_on_submit=True):
                        col_a, col_b = st.columns(2)
                        nome_cliente = col_a.text_input("Nome do Cliente")
                        data_venda = col_b.date_input("Data da Venda")
                        
                        opcoes_select = {f"{p['Produto']} (Tam: {p['Tamanho']}) - R$ {p['Valor (R$)']} | Disp: {p['Quantidade']} un": p for p in pecas_disponiveis}
                        
                        peca_selecionada = st.selectbox("Selecione a Peça do Estoque", list(opcoes_select.keys()))
                        
                        col_c, col_d = st.columns(2)
                        qtd_vendida = col_c.number_input("Quantidade a vender", min_value=1, step=1)
                        desconto = col_d.number_input("Desconto / Ajuste de valor (Opcional - R$)", min_value=0.0, step=0.5, format="%.2f")

                        submit_venda = st.form_submit_button("Concluir Venda e Baixar Estoque", type="primary")

                        if submit_venda and nome_cliente:
                            peca_ref = opcoes_select[peca_selecionada]
                            
                            if qtd_vendida > int(peca_ref['Quantidade']):
                                st.error(f"❌ Estoque insuficiente! Você tem apenas {peca_ref['Quantidade']} unidades em estoque.")
                            else:
                                valor_total = (float(peca_ref['Valor (R$)']) * qtd_vendida) - desconto
                                data_str = data_venda.strftime("%d/%m/%Y")
                                
                                for p in st.session_state.estoque:
                                    if p == peca_ref:
                                        p['Quantidade'] = int(p['Quantidade']) - qtd_vendida
                                        break
                                
                                st.session_state.vendas.append({
                                    'Tipo': 'Venda', 'Data': data_str, 'Cliente': nome_cliente,
                                    'Produto': peca_ref['Produto'], 'Qtd': qtd_vendida,
                                    'Total (R$)': valor_total, 'Entrega': 'Pronta Entrega'
                                })
                                salvar_dados(st.session_state.vendas, ARQ_VENDAS)
                                salvar_dados(st.session_state.estoque, ARQ_ESTOQUE)

                                st.session_state.financeiro.append({
                                    'Data': data_str, 'Tipo': 'Entrada',
                                    'Descrição': f"Venda Estoque: {peca_ref['Produto']} ({nome_cliente})", 'Valor (R$)': valor_total
                                })
                                salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO)

                                st.success(f"✅ Venda registrada! (R$ {valor_total:.2f}). O estoque foi atualizado automaticamente.")
                                st.rerun()

            elif tipo_registro == "Novo Pedido (Encomenda)":
                with st.form("form_pedidos", clear_on_submit=True):
                    col_a, col_b = st.columns(2)
                    nome_cliente = col_a.text_input("Nome do Cliente")
                    data_entrega = col_b.date_input("Data Limite para Entrega")

                    st.divider()
                    produto_vendido = st.text_input("Produto/Serviço Encomendado")

                    col_c, col_d = st.columns(2)
                    qtd_vendida = col_c.number_input("Quantidade", min_value=1, step=1)
                    valor_total = col_d.number_input("Valor Total Combinado (R$)", min_value=0.0, step=0.5, format="%.2f")

                    submit_pedido = st.form_submit_button("Registrar Encomenda", type="primary")

                    if submit_pedido and nome_cliente and produto_vendido:
                        data_registro = datetime.now().strftime("%d/%m/%Y")

                        st.session_state.vendas.append({
                            'Tipo': 'Pedido', 'Data': data_registro, 'Cliente': nome_cliente,
                            'Produto': produto_vendido, 'Qtd': qtd_vendida,
                            'Total (R$)': valor_total, 'Entrega': data_entrega.strftime("%d/%m/%Y")
                        })
                        salvar_dados(st.session_state.vendas, ARQ_VENDAS)

                        st.session_state.financeiro.append({
                            'Data': data_registro, 'Tipo': 'Entrada',
                            'Descrição': f"Encomenda: {produto_vendido} ({nome_cliente})", 'Valor (R$)': valor_total
                        })
                        salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO)

                        st.success(f"✅ Encomenda salva! (R$ {valor_total:.2f})")

        with aba2:
            if st.session_state.vendas:
                df_vendas = pd.DataFrame(st.session_state.vendas)
                if 'Tipo' not in df_vendas.columns:
                    df_vendas['Tipo'] = 'Pedido'

                st.subheader("🛍️ Vendas Realizadas (Pronta Entrega)")
                df_vendas_prontas = df_vendas[df_vendas['Tipo'] == 'Venda'].drop(columns=['Tipo'], errors='ignore')
                if not df_vendas_prontas.empty:
                    st.dataframe(df_vendas_prontas, use_container_width=True)
                else:
                    st.info("Nenhuma venda de pronta entrega realizada.")
                
                st.divider()

                st.subheader("📦 Pedidos e Encomendas")
                df_pedidos_encomendas = df_vendas[df_vendas['Tipo'] == 'Pedido'].drop(columns=['Tipo'], errors='ignore')
                if not df_pedidos_encomendas.empty:
                    st.dataframe(df_pedidos_encomendas, use_container_width=True)
                else:
                    st.info("Nenhum pedido ou encomenda registrado.")
            else:
                st.info("Nenhuma venda ou pedido realizado ainda.")

    # ----------------------------------------
    # MÓDULO 3: FINANCEIRO
    # ----------------------------------------
    elif escolha == "📊 Financeiro":
        st.header("Gestão Financeira e Relatórios")

        receitas = sum(converter_valor(i['Valor (R$)']) for i in st.session_state.financeiro if i['Tipo'] == 'Entrada')
        saidas = sum(converter_valor(i['Valor (R$)']) for i in st.session_state.financeiro if i['Tipo'] == 'Saída')
        custos_fixos = sum(converter_valor(i['Valor (R$)']) for i in st.session_state.financeiro if i.get('Tipo') == 'Custo Fixo')
        
        saldo_livre = receitas - saidas - custos_fixos
        valor_estoque = sum(converter_valor(i['Valor (R$)']) for i in st.session_state.estoque if i['Categoria'] == 'Material')

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Entradas (Receitas)", f"R$ {receitas:.2f}")
        col2.metric("Saídas (Variáveis/Insumos)", f"R$ {saidas:.2f}")
        col3.metric("Custos Fixos", f"R$ {custos_fixos:.2f}")
        col4.metric("Saldo Líquido", f"R$ {saldo_livre:.2f}", delta=f"R$ {saldo_livre:.2f}", delta_color="normal")
        
        st.info(f"🧵 **Capital investido em Estoque (Materiais e Insumos):** R$ {valor_estoque:.2f}")

        st.divider()
        aba1, aba2 = st.tabs(["💸 Lançar Movimentação", "📈 Extrato Completo"])

        with aba1:
            with st.form("form_financeiro", clear_on_submit=True):
                tipo_movimento = st.radio(
                    "Tipo de Movimentação:", 
                    ["Saída (Variável - ex: compra de linha, frete)", "Custo Fixo (ex: aluguel, luz, internet)", "Entrada Extra"], 
                    horizontal=True
                )
                
                desc_despesa = st.text_input("Descrição")
                valor_despesa = st.number_input("Valor (R$)", min_value=0.01, step=0.5, format="%.2f")
                submit_financeiro = st.form_submit_button("Registrar Lançamento", type="primary")

                if submit_financeiro and desc_despesa:
                    tipo_final = "Saída"
                    if "Fixo" in tipo_movimento:
                        tipo_final = "Custo Fixo"
                    elif "Entrada" in tipo_movimento:
                        tipo_final = "Entrada"

                    st.session_state.financeiro.append({
                        'Data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                        'Tipo': tipo_final, 'Descrição': desc_despesa, 'Valor (R$)': valor_despesa
                    })
                    salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO)
                    st.success(f"✅ Lançamento de '{tipo_final}' salvo com sucesso!")
                    st.rerun()

        with aba2:
            if st.session_state.financeiro:
                df_financeiro = pd.DataFrame(st.session_state.financeiro)
                
                st.subheader("Relatório Financeiro")
                filtro = st.selectbox("Filtrar por tipo:", ["Todos", "Entrada", "Saída", "Custo Fixo"])
                
                if filtro != "Todos":
                    df_exibir = df_financeiro[df_financeiro['Tipo'] == filtro]
                else:
                    df_exibir = df_financeiro
                
                if not df_exibir.empty:
                    st.dataframe(df_exibir, use_container_width=True)
                else:
                    st.info(f"Nenhum lançamento do tipo '{filtro}' encontrado.")
            else:
                st.info("Nenhuma movimentação financeira registrada.")
