import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. Configuração da Página
st.set_page_config(page_title="Gilka Campos Bordados", page_icon="🪡", layout="wide")

# ----------------------------------------
# CONFIGURAÇÃO DO GOOGLE DRIVE
# ----------------------------------------
PASTA_DRIVE = "/content/drive/MyDrive/Sistema_Gilka_Bordados"
os.makedirs(PASTA_DRIVE, exist_ok=True) # Cria a pasta no Drive se não existir

ARQ_ESTOQUE = f"{PASTA_DRIVE}/estoque.csv"
ARQ_VENDAS = f"{PASTA_DRIVE}/vendas.csv"
ARQ_FINANCEIRO = f"{PASTA_DRIVE}/financeiro.csv"

# Funções para Salvar e Carregar dados do Drive
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
if 'estoque' not in st.session_state:
    st.session_state.estoque = carregar_dados(ARQ_ESTOQUE)
if 'vendas' not in st.session_state:
    st.session_state.vendas = carregar_dados(ARQ_VENDAS)
if 'financeiro' not in st.session_state:
    st.session_state.financeiro = carregar_dados(ARQ_FINANCEIRO)

# 3. Tela de Login
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🪡 Gilka Bordados</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: gray;'>Acesso Restrito</h4>", unsafe_allow_html=True)
        st.divider()

        usuario = st.text_input("👤 Usuário")
        senha = st.text_input("🔑 Senha", type="password")

        if st.button("Entrar no Sistema", type="primary", use_container_width=True):
            if usuario == "gilka" and senha == "bordados123":
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos! Tente novamente.")

# 4. Sistema Principal
else:
    st.sidebar.title("🪡 Menu Principal")
    menu = ["📦 Estoque", "💰 Vendas / Pedidos", "📊 Financeiro"]
    escolha = st.sidebar.radio("Navegue por aqui:", menu)

    st.sidebar.divider()
    st.sidebar.write("👤 Usuário logado: **Gilka**")
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
                        salvar_dados(st.session_state.estoque, ARQ_ESTOQUE) # SALVA NO DRIVE
                        st.success(f"✅ Peça '{produto}' salva no Drive!")

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
                        salvar_dados(st.session_state.estoque, ARQ_ESTOQUE) # SALVA NO DRIVE
                        st.success(f"✅ Material '{produto}' salvo no Drive!")

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
                    salvar_dados(st.session_state.vendas, ARQ_VENDAS) # SALVA NO DRIVE

                    st.session_state.financeiro.append({
                        'Data': data_venda, 'Tipo': 'Entrada',
                        'Descrição': f"Pedido: {produto_vendido} ({nome_cliente})", 'Valor (R$)': valor_total
                    })
                    salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO) # SALVA NO DRIVE

                    st.success(f"✅ Pedido salvo no Drive! (R$ {valor_total:.2f})")

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
                    salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO) # SALVA NO DRIVE
                    st.success("✅ Despesa salva no Drive com sucesso!")

        with aba2:
            if st.session_state.financeiro:
                df_financeiro = pd.DataFrame(st.session_state.financeiro)
                st.dataframe(df_financeiro, use_container_width=True)
            else:
                st.info("Nenhuma movimentação financeira.")
