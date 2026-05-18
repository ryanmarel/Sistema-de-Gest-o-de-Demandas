import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime, date

# 1. CONEXÃO E CONFIGURAÇÃO DO BANCO DE DADOS
conn = sqlite3.connect('relatorios_telecom.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS atividades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_inicio TEXT,
        data_fim TEXT,
        categoria TEXT,
        status TEXT,
        titulo TEXT,
        descricao TEXT,
        executantes TEXT,
        tipo TEXT,
        urgencia TEXT,
        anexo TEXT,
        equipe TEXT
    )
''')

# TABELA PARA LOGS DE AUDITORIA
cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs_atividades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        atividade_id INTEGER,
        usuario TEXT,
        acao TEXT,
        data_hora TEXT
    )
''')

# TABELA PARA GERENCIAMENTO DE USUÁRIOS E PERMISSÕES
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        nome TEXT PRIMARY KEY,
        senha TEXT,
        permissao TEXT,
        equipe TEXT
    )
''')

# TABELA PARA ARMAZENAMENTO DINÂMICO DE EQUIPES
cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipes (
        nome TEXT PRIMARY KEY
    )
''')

# FORÇAR ATUALIZAÇÃO E MIGRAÇÃO ESTRUTURAL DE COLUNAS
os.makedirs(atividades_anexos, exist_ok=True)
try
    cursor.execute(ALTER TABLE atividades ADD COLUMN anexo TEXT)
    conn.commit()
except sqlite3.OperationalError
    pass  

try
    cursor.execute(ALTER TABLE atividades ADD COLUMN equipe TEXT)
    conn.commit()
except sqlite3.OperationalError
    pass  

try
    cursor.execute(ALTER TABLE usuarios ADD COLUMN equipe TEXT)
    conn.commit()
except sqlite3.OperationalError
    pass  

# Inicializa as equipes padrão no banco de dados se estiver vazio
cursor.execute(SELECT COUNT() FROM equipes)
if cursor.fetchone()[0] == 0
    cursor.execute(INSERT INTO equipes VALUES ('Telecomunicações'))
    cursor.execute(INSERT INTO equipes VALUES ('Automação'))
    cursor.execute(INSERT INTO equipes VALUES ('Gestor'))
    conn.commit()

# Inicializa os usuários padrão distribuídos por equipes caso a tabela esteja vazia
cursor.execute(SELECT COUNT() FROM usuarios)
if cursor.fetchone()[0] == 0
    cursor.execute(INSERT INTO usuarios VALUES ('Arthur', 'telecom123', 'admin', 'Telecomunicações'))
    cursor.execute(INSERT INTO usuarios VALUES ('Eduardo', 'telecom123', 'admin', 'Telecomunicações'))
    cursor.execute(INSERT INTO usuarios VALUES ('Ryan', 'telecom123', 'admin', 'Telecomunicações'))
    cursor.execute(INSERT INTO usuarios VALUES ('Consulta', 'telecom123', 'leitura', 'Telecomunicações'))
    cursor.execute(INSERT INTO usuarios VALUES ('Administrador', 'admin123', 'admin', 'Telecomunicações'))
    cursor.execute(INSERT INTO usuarios VALUES ('Tecnico_Teste', 'telecom123', 'tecnico', 'Telecomunicações'))
    cursor.execute(INSERT INTO usuarios VALUES ('Lucas_Automacao', 'telecom123', 'tecnico', 'Automação'))
    cursor.execute(INSERT INTO usuarios VALUES ('Gestor_Teste', 'telecom123', 'gestor', 'Gestor'))
    conn.commit()

# Puxa a lista dinâmica de equipes cadastradas no banco de dados
cursor.execute(SELECT nome FROM equipes ORDER BY nome ASC)
LISTA_EQUIPES_DINAMICA = [row[0] for row in cursor.fetchall()]
if not LISTA_EQUIPES_DINAMICA
    LISTA_EQUIPES_DINAMICA = [Telecomunicações, Automação, Gestor]

# Opções fixas do sistema
LISTA_TECNICOS = [Arthur, Eduardo, Ryan]
LISTA_TIPOS = [Rede NT, Rede DB, Melhoria, ProcessoDocumentação]
LISTA_URGENCIA = [Alta, Média, Normal]
LISTA_STATUS = [Aberto, Em Andamento, Concluído]

# --- CONTROLE DE ESTADO DO FORMULÁRIO (Previne perda de dados) ---
if form_version not in st.session_state
    st.session_state.form_version = 0
if sucesso_cadastro not in st.session_state
    st.session_state.sucesso_cadastro = False
if id_edit not in st.session_state
    st.session_state.id_edit = None

# --- ESTADOS PARA AUTENTICAÇÃO, SENHA E EQUIPE ---
if autenticado not in st.session_state
    st.session_state.autenticado = False
if usuario_logado not in st.session_state
    st.session_state.usuario_logado = None
if permissao not in st.session_state
    st.session_state.permissao = None
if equipe not in st.session_state
    st.session_state.equipe = None
if mostrar_alterar_senha not in st.session_state
    st.session_state.mostrar_alterar_senha = False
if imagens_relatorio not in st.session_state
    st.session_state.imagens_relatorio = []

# 2. CONFIGURAÇÃO DA INTERFACE WEB
st.set_page_config(page_title=Dashboard Telecom, page_icon=📡, layout=wide)

# -------------------------------------------------------------------------
# 🎨 CUSTOMIZAÇÃO VISUAL IDENTIDADE DE CORES (Azul Predominante e Branco)
# -------------------------------------------------------------------------
st.markdown(
    style
         1. Fundo Geral do Sistema - Dark Focado 
        .stApp {
            background-color #11151c !important;
            color #ffffff !important;
        }

         2. Elementos de Destaque da Marca (Azul Barbosa Melo #004A93) nos Botões 
        .stButtonbutton, .stForm_submit_button button {
            background-color #004A93 !important;
            color #ffffff !important;
            border-radius 5px;
            border none;
            font-weight bold;
        }
        .stButtonbuttonhover {
            background-color #00356B !important;
        }
        
         Contornos dos campos de seleção e inputs 
        .stSelectbox div[data-baseweb=select] div, .stMultiSelect div[data-baseweb=select] div, .stDateInput input {
            border-color #004A93 !important;
        }
        
         Títulos de Seções e Cabeçalhos em Azul da Marca 
        h1, h2, h3, h4, h5, h6 {
            color #004A93 !important;
        }
        
         Customização dos Cards de Atividades (Expanders) 
        .stExpander {
            border 1px solid #3d3d3d;
            border-radius 5px;
            margin-bottom 10px;
            background-color rgba(255, 255, 255, 0.02) !important;
        }
        .stExpanderhover {
            border-color #004A93 !important;
        }
        
         Definições de contraste para textos e rótulos em Branco 
        .stMarkdown p, .stMarkdown label, .stMarkdown li, .stCheckbox span {
            color #ffffff !important;
        }
        .stTextInput input, .stTextArea textarea, .stDateInput input {
            color #ffffff !important;
            background-color rgba(255, 255, 255, 0.05) !important;
            border-color rgba(255, 255, 255, 0.2) !important;
        }
        
         Menus drop-down suspensos 
        div[data-baseweb=select] ul {
            background-color #1c1c1c !important;
            color #ffffff !important;
        }
    style
, unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 🔑 VERIFICAÇÃO ATIVA DO RECURSO SALVAR LOGIN (AUTO-LOGIN)
# -------------------------------------------------------------------------
if not st.session_state.autenticado and token in st.query_params
    token_usuario = st.query_params[token]
    cursor.execute(SELECT senha, permissao, equipe FROM usuarios WHERE nome = , (token_usuario,))
    dados_token = cursor.fetchone()
    if dados_token
        st.session_state.autenticado = True
        st.session_state.usuario_logado = token_usuario
        st.session_state.permissao = dados_token[1]
        st.session_state.equipe = dados_token[2] if dados_token[2] else Telecomunicações

# -------------------------------------------------------------------------
# INTERFACE DE LOGIN
# -------------------------------------------------------------------------
if not st.session_state.autenticado
    st.title(🔒 Sistema de Gestão de Demandas - Telecom)
    st.subheader(Autenticação de Acesso)
    
    user_login = st.text_input(Digite seu usuário, key=login_user_input).strip()
    pass_login = st.text_input(Digite sua senha, type=password, key=login_pass_input)
    salvar_login = st.checkbox(Salvar Login (Auto-login neste navegador), key=login_save_checkbox)
    botao_login = st.button(Entrar, key=login_submit_btn)
    
    if botao_login
        if not user_login
            st.error(❌ Por favor, informe o seu usuário para prosseguir.)
        else
            cursor.execute(SELECT senha, permissao, equipe FROM usuarios WHERE nome = , (user_login,))
            dados_usuario = cursor.fetchone()
            
            if dados_usuario and pass_login == dados_usuario[0]
                st.session_state.autenticado = True
                st.session_state.usuario_logado = user_login
                st.session_state.permissao = dados_usuario[1]
                st.session_state.equipe = dados_usuario[2] if dados_usuario[2] else Telecomunicações
                
                if salvar_login
                    st.query_params[token] = user_login
                st.rerun()
            else
                st.error(❌ Usuário ou senha incorretos! Tente novamente.)
    st.stop()

# CORDÃO DE TOPO
col_tit, col_user = st.columns([2.8, 1.2])
with col_tit
    st.title(📋 Sistema de Gestão de Demandas - Telecom)
with col_user
    st.markdown(f👤 Operador {st.session_state.usuario_logado} ({st.session_state.permissao.upper()})  🏢 Escopo {st.session_state.equipe})
    c1, c2 = st.columns(2)
    with c1
        if st.button( 🚪 Sair, key=btn_logout)
            st.session_state.autenticado = False
            st.session_state.usuario_logado = None
            st.session_state.permissao = None
            st.session_state.equipe = None
            st.session_state.mostrar_alterar_senha = False
            st.session_state.id_edit = None
            if token in st.query_params
                del st.query_params[token]
            st.rerun()
    with c2
        if st.button(🔑 Senha, key=btn_toggle_senha)
            st.session_state.mostrar_alterar_senha = not st.session_state.mostrar_alterar_senha
            st.rerun()

# Painel expansível para alteração de senha individual
if st.session_state.mostrar_alterar_senha
    st.write(---)
    with st.form(form_alterar_senha)
        st.subheader(🔑 Alterar Senha de Acesso)
        nova_senha = st.text_input(Digite a Nova Senha, type=password)
        confirma_senha = st.text_input(Confirme a Nova Senha, type=password)
        btn_gravar_senha = st.form_submit_button(Gravar Nova Senha)
        
        if btn_gravar_senha
            if not nova_senha
                st.error(❌ A senha não pode ficar em branco!)
            elif nova_senha != confirma_senha
                st.error(❌ As senhas digitadas não coincidem!)
            else
                cursor.execute(UPDATE usuarios SET senha =  WHERE nome = , (nova_senha, st.session_state.usuario_logado))
                conn.commit()
                st.success(🎯 Senha atualizada com sucesso!)
                st.session_state.mostrar_alterar_senha = False
                st.rerun()

# --- REGRA DE ACESSO GLOBAL PARA EQUIPE GESTOR E PERFIS ADMINGESTOR ---
tem_acesso_global = (st.session_state.permissao in [admin, gestor] or st.session_state.equipe == Gestor)

# --- CONFIGURAÇÃO DE ABAS DINÂMICAS ---
lista_abas_operacionais = [
    📝 Registrar Atividade, 
    ⚙️ Gestão Atividades, 
    📊 Gerar Relatório,
    📈 Painel de SLA & Métricas
]

es_administrador = (st.session_state.permissao == admin)
if es_administrador
    lista_abas_operacionais.append(👥 Gestão Usuários)

abas_sistema = st.tabs(lista_abas_operacionais)

if es_administrador
    aba_inserir, aba_gerenciar, aba_relatorio, aba_sla, aba_usuarios = abas_sistema
else
    aba_inserir, aba_gerenciar, aba_relatorio, aba_sla = abas_sistema

usuario_leitura = (st.session_state.permissao == leitura)

# -------------------------------------------------------------------------
# ABA 1 REGISTRAR ATIVIDADE
# -------------------------------------------------------------------------
with aba_inserir
    st.subheader(Cadastrar Nova Demanda)
    
    if usuario_leitura
        st.warning(🔒 Seu usuário possui permissão apenas de LEITURA. O cadastro de novas demandas está bloqueado.)
    
    with st.form(key=fform_atividade_v_{st.session_state.form_version}, clear_on_submit=False)
        col1, col2 = st.columns(2)
        
        with col1
            categoria = st.selectbox(Categoria, [Atividade do Turno, Segurança, 5S], disabled=usuario_leitura)
            status = st.selectbox(Status Inicial, LISTA_STATUS, disabled=usuario_leitura)
            urgencia = st.selectbox(Nível de Urgência, LISTA_URGENCIA, index=2, disabled=usuario_leitura)
            titulo = st.text_input(Título da Atividade, placeholder=Ex Teste de Bancada Sw EH-115, disabled=usuario_leitura)
            
            if tem_acesso_global
                equipe_registro = st.selectbox(Equipe Destino da Atividade, LISTA_EQUIPES_DINAMICA)
            else
                equipe_registro = st.session_state.equipe
        
        with col2
            executantes_sel = st.multiselect(Executantes Responsáveis, options=LISTA_TECNICOS, disabled=usuario_leitura)
            tipos_sel = st.multiselect(Tipo de Infraestrutura  Atividade, options=LISTA_TIPOS, disabled=usuario_leitura)
            
            data_ini = st.date_input(Data de Início, datetime.now(), format=DDMMYYYY, disabled=usuario_leitura)
            
            tem_data_fim = st.checkbox(Definir Data de Finalização agora, disabled=usuario_leitura)
            data_final = st.date_input(Data de Finalização, datetime.now(), format=DDMMYYYY) if tem_data_fim else None
            
        descricao = st.text_area(Descrição Detalhada, placeholder=Descreva o escopo ou diagnóstico da atividade..., disabled=usuario_leitura)
        arquivo_anexo = st.file_uploader(Anexar Evidências Técnicas (Imagens, PDFs, Configs, etc.), disabled=usuario_leitura, key=ffile_reg_{st.session_state.form_version}, accept_multiple_files=True)
        
        botao_salvar = st.form_submit_button(Salvar Registro, disabled=usuario_leitura)
        
        if botao_salvar and not usuario_leitura
            if categoria == 5S and not titulo and not descricao
                titulo = Sala em conformidade, Organização contínua.
            
            if not titulo and categoria != 5S
                st.error(❌ O campo 'Título' é obrigatório!)
            elif not executantes_sel
                st.error(❌ Selecione pelo menos um Executante!)
            elif not tipos_sel and categoria == Atividade do Turno
                st.error(❌ Selecione pelo menos um Tipo para atividades de turno!)
            else
                executantes_str = , .join(executantes_sel)
                tipos_str = , .join(tipos_sel)
                dt_inicio_str = data_ini.strftime(%Y-%m-%d)
                dt_fim_str = data_final.strftime(%Y-%m-%d) if data_final else 
                
                # MODIFICADO AQUI Se marcou para definir data de finalização, o status vira Concluído automaticamente
                if tem_data_fim
                    status = Concluído
                
                anexos_nomes = []
                if arquivo_anexo
                    for arq in arquivo_anexo
                        nome_gerado = f{datetime.now().strftime('%Y%m%d%H%M%S')}_{arq.name}
                        with open(os.path.join(atividades_anexos, nome_gerado), wb) as f
                            f.write(arq.getbuffer())
                        anexos_nomes.append(nome_gerado)
                anexo_str = , .join(anexos_nomes) if anexos_nomes else 
                
                cursor.execute('''
                    INSERT INTO atividades (data_inicio, data_fim, categoria, status, titulo, descricao, executantes, tipo, urgencia, anexo, equipe)
                    VALUES (, , , , , , , , , , )
                ''', (dt_inicio_str, dt_fim_str, categoria, status, titulo, descricao, executantes_str, tipos_str, urgencia, anexo_str, equipe_registro))
                
                id_nova_atv = cursor.lastrowid
                dt_log = datetime.now().strftime(%d%m%Y %H%M%S)
                cursor.execute(INSERT INTO logs_atividades (atividade_id, usuario, acao, data_hora) VALUES (, , , ),
                               (id_nova_atv, st.session_state.usuario_logado, fCriou a atividade inicial no setor {equipe_registro}., dt_log))
                conn.commit()
                
                st.session_state.form_version += 1
                st.session_state.sucesso_cadastro = True
                st.rerun()

# -------------------------------------------------------------------------
# ABA 2 PAINEL DE CONTROLE E EDIÇÃO
# -------------------------------------------------------------------------
with aba_gerenciar
    st.subheader(Filtros de Busca)
    
    if tem_acesso_global
        f_col1, f_col2, f_col3, f_col4, f_col5, f_col6 = st.columns(6)
        with f_col6
            filtro_equipe = st.selectbox(Filtrar por Equipe, [Todas] + LISTA_EQUIPES_DINAMICA, key=filter_equipe_selectbox)
    else
        f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
        
    with f_col1
        filtro_status = st.multiselect(Filtrar por Status, LISTA_STATUS, default=LISTA_STATUS, key=filter_status_multiselect)
    with f_col2
        filtro_exec = st.selectbox(Filtrar por Executante, [Todos] + LISTA_TECNICOS, key=filter_exec_selectbox)
    with f_col3
        filtro_data_tipo = st.selectbox(Filtrar por Data, [Não Filtrar, Data de Início, Data de Finalização], key=filter_datetype_selectbox)
    with f_col4
        filtro_data_val = st.date_input(Escolha a Data, datetime.now(), format=DDMMYYYY, key=filter_dateval_input)
    with f_col5
        opcao_ordenar = st.selectbox(Ordenar por, [Mais Recentes, Mais Antigos, Urgência, Status], key=filter_order_selectbox)
        
    query = SELECT id, data_inicio, data_fim, status, titulo, descricao, executantes, tipo, urgencia, categoria, anexo, equipe FROM atividades WHERE 1=1
    params = []
    
    if not tem_acesso_global
        query +=  AND equipe = 
        params.append(st.session_state.equipe)
    elif filtro_equipe != Todas
        query +=  AND equipe = 
        params.append(filtro_equipe)
        
    if filtro_status
        query += f AND status IN ({','.join(['']len(filtro_status))})
        params.extend(filtro_status)
        
    if filtro_exec != Todos
        query +=  AND executantes LIKE 
        params.append(f%{filtro_exec}%)
        
    if filtro_data_tipo == Data de Início
        query +=  AND data_inicio = 
        params.append(f%{filtro_data_val.strftime('%Y-%m-%d')}%)
    elif filtro_data_tipo == Data de Finalização
        query +=  AND data_fim = 
        params.append(f%{filtro_data_val.strftime('%Y-%m-%d')}%)
        
    if opcao_ordenar == Mais Recentes
        query +=  ORDER BY id DESC
    elif opcao_ordenar == Mais Antigos
        query +=  ORDER BY id ASC
    elif opcao_ordenar == Urgência
        query +=  ORDER BY CASE urgencia WHEN 'Alta' THEN 1 WHEN 'Média' THEN 2 WHEN 'Normal' THEN 3 END ASC, id DESC
    elif opcao_ordenar == Status
        query +=  ORDER BY CASE status WHEN 'Aberto' THEN 1 WHEN 'Em Andamento' THEN 2 WHEN 'Concluído' THEN 3 END ASC, id DESC
        
    cursor.execute(query, params)
    atividades_filtradas = cursor.fetchall()
    
    if st.session_state.id_edit and not usuario_leitura
        st.write(---)
        st.subheader(f🛠️ Editando Atividade #{st.session_state.id_edit})
        
        cursor.execute(SELECT data_inicio, data_fim, status, executantes, tipo, urgencia, titulo, descricao, anexo, equipe FROM atividades WHERE id = , (st.session_state.id_edit,))
        dados_edicao = cursor.fetchone()
        
        with st.form(form_alteracao)
            novo_titulo = st.text_input(Alterar Título, value=dados_edicao[6])
            ed_c1, ed_c2 = st.columns(2)
            
            with ed_c1
                novo_st = st.selectbox(Alterar Status, LISTA_STATUS, index=LISTA_STATUS.index(dados_edicao[2]))
                novo_urg = st.selectbox(Alterar Urgência, LISTA_URGENCIA, index=LISTA_URGENCIA.index(dados_edicao[5]))
                exec_list = [e.strip() for e in dados_edicao[3].split(,)] if dados_edicao[3] else []
                novos_execs = st.multiselect(Alterar Executantes, LISTA_TECNICOS, default=exec_list)
                
                if tem_acesso_global
                    idx_eq_edit = LISTA_EQUIPES_DINAMICA.index(dados_edicao[9]) if dados_edicao[9] in LISTA_EQUIPES_DINAMICA else 0
                    novo_equipe_atv = st.selectbox(Alterar Setor Responsável, LISTA_EQUIPES_DINAMICA, index=idx_eq_edit)
                else
                    novo_equipe_atv = dados_edicao[9]
                
            with ed_c2
                tipo_list = [t.strip() for t in dados_edicao[4].split(,)] if dados_edicao[4] else []
                novos_tipos = st.multiselect(Alterar Tipos, LISTA_TIPOS, default=tipo_list)
                
                dt_i_atual = datetime.strptime(dados_edicao[0], %Y-%m-%d)
                nova_dt_i = st.date_input(Nova Data de Início, dt_i_atual, format=DDMMYYYY)
                
                dt_f_atual = datetime.strptime(dados_edicao[1], %Y-%m-%d) if dados_edicao[1] else datetime.now()
                tem_dt_f_ed = st.checkbox(Informar Data de Finalização, value=bool(dados_edicao[1]))
                nova_dt_f = st.date_input(Nova Data de Finalização, dt_f_atual, format=DDMMYYYY) if tem_dt_f_ed else None
                
            nova_descricao = st.text_area(Alterar Descrição, value=dados_edicao[7])
            
            if dados_edicao[8]
                st.markdown(📎 Evidências técnicas já cadastradas)
                anexos_atuais_lista = [a.strip() for a in dados_edicao[8].split(,) if a.strip()]
                for a_atual in anexos_atuais_lista
                    st.markdown(f- `{a_atual.split('_', 1)[-1]}`)
                    
            novo_arquivo_anexo = st.file_uploader(Adicionar Novas Evidências Técnicas, key=ffile_edit_{st.session_state.id_edit}, accept_multiple_files=True)
            
            btn_gravar = st.form_submit_button(Gravar Alterações)
            
            if btn_gravar
                if not novo_titulo
                    st.error(❌ O campo Título não pode ficar completamente vazio!)
                else
                    dt_f_str = nova_dt_f.strftime(%Y-%m-%d) if nova_dt_f else 
                    
                    # MODIFICADO AQUI Se informou data de finalização, altera o status para concluído automaticamente
                    if tem_dt_f_ed
                        novo_st = Concluído
                    elif novo_st == Concluído and not dt_f_str
                        dt_f_str = datetime.now().strftime(%Y-%m-%d)
                        
                    novos_anexos_nomes = []
                    if novo_arquivo_anexo
                        for arq in novo_arquivo_anexo
                            nome_gerado = f{datetime.now().strftime('%Y%m%d%H%M%S')}_{arq.name}
                            with open(os.path.join(atividades_anexos, nome_gerado), wb) as f
                                f.write(arq.getbuffer())
                            novos_anexos_nomes.append(nome_gerado)
                            
                    anexos_base = [a.strip() for a in dados_edicao[8].split(,) if a.strip()] if dados_edicao[8] else []
                    anexos_totais_lista = anexos_base + novos_anexos_nomes
                    anexo_final_str = , .join(anexos_totais_lista) if anexos_totais_lista else 
                        
                    cursor.execute('''
                        UPDATE atividades 
                        SET status = , urgencia = , executantes = , tipo = , data_inicio = , data_fim = , titulo = , descricao = , anexo = , equipe = 
                        WHERE id = 
                    ''', (novo_st, novo_urg, , .join(novos_execs), , .join(novos_tipos), nova_dt_i.strftime(%Y-%m-%d), dt_f_str, novo_titulo, nova_descricao, anexo_final_str, novo_equipe_atv, st.session_state.id_edit))
                    
                    dt_log = datetime.now().strftime(%d%m%Y %H%M%S)
                    txt_acao = fModificou Título={novo_titulo}  Status={novo_st}  Setor={novo_equipe_atv}
                    cursor.execute(INSERT INTO logs_atividades (atividade_id, usuario, acao, data_hora) VALUES (, , , ),
                                   (st.session_state.id_edit, st.session_state.usuario_logado, txt_acao, dt_log))
                    conn.commit()
                    
                    st.success(Dados updated com sucesso!)
                    st.session_state.id_edit = None
                    st.rerun()

    st.write(---)
    st.subheader(fLista de Atividades - Contexto {filtro_equipe if tem_acesso_global else st.session_state.equipe})
    
    if not atividades_filtradas
        st.info(Nenhuma atividade encontrada com os filtros aplicados.)
    else
        for atv in atividades_filtradas
            id_a, dt_ini, dt_fim, st_a, tit, desc, execs, tp, urg, cat, anx, eq_atv = atv
            
            dt_ini_br = datetime.strptime(dt_ini, %Y-%m-%d).strftime(%d%m%Y) if dt_ini else -
            dt_fim_br = datetime.strptime(dt_fim, %Y-%m-%d).strftime(%d%m%Y) if dt_fim else Em aberto
            
            if st_a == Aberto
                status_colorido = red[ABERTO]
            elif st_a == Em Andamento
                status_colorido = yellow[EM ANDAMENTO]
            else
                status_colorido = green[CONCLUÍDO]
            
            label_card = f[{status_colorido}] {tit}  Urgência {urg}  Tipo {tp}
            with st.expander(label_card)
                st.markdown(f📝 Descrição {desc})
                st.markdown(f👥 Executantes {execs}  📂 Categoria {cat}  🏢 Equipe Proprietária {eq_atv})
                st.markdown(f📅 Período Início em {dt_ini_br}  Finalização {dt_fim_br})
                
                if anx
                    lista_anexos_split = [a.strip() for a in anx.split(,) if a.strip()]
                    for sub_idx, sub_anx in enumerate(lista_anexos_split)
                        if os.path.exists(os.path.join(atividades_anexos, sub_anx))
                            with open(os.path.join(atividades_anexos, sub_anx), rb) as file_bytes
                                st.download_button(
                                    label=f📥 Baixar Evidência ({sub_anx.split('_', 1)[-1]}),
                                    data=file_bytes,
                                    file_name=sub_anx.split('_', 1)[-1],
                                    key=fdl_{id_a}_{sub_idx}
                                )
                
                cursor.execute(SELECT usuario, acao, data_hora FROM logs_atividades WHERE atividade_id =  ORDER BY id DESC, (id_a,))
                logs_atv = cursor.fetchall()
                if logs_atv
                    st.markdown(---)
                    st.markdown(📜 Histórico de Alterações (Auditoria))
                    for log in logs_atv
                        st.markdown(f⏱️ {log[2]} - {log[0]} {log[1]})
                
                st.markdown(---)
                # MODIFICADO AQUI Colunas para acomodar botões de Alteração e o novo botão global de Exclusão reativa
                col_b1, col_b2 = st.columns(2)
                with col_b1
                    if st_a == Concluído
                        st.warning(🔒 Atividade Concluída. Alterações bloqueadas para este registro.)
                    else
                        if st.button(f✏️ Alterar Atividade #{id_a}, key=fbtn_edit_{id_a}, disabled=usuario_leitura)
                            st.session_state.id_edit = id_a
                            st.rerun()
                with col_b2
                    # ADICIONADO AQUI Botão de exclusão independente disponível em qualquer status técnico
                    if st.button(f🗑️ Excluir Atividade #{id_a}, key=fbtn_del_{id_a}, disabled=usuario_leitura)
                        cursor.execute(DELETE FROM atividades WHERE id = , (id_a,))
                        cursor.execute(DELETE FROM logs_atividades WHERE atividade_id = , (id_a,))
                        conn.commit()
                        st.success(f🗑️ Atividade #{id_a} excluída com sucesso!)
                        st.rerun()

# -------------------------------------------------------------------------
# ABA 3 GERAR RELATÓRIO DIÁRIO & GERAL
# -------------------------------------------------------------------------
with aba_relatorio
    st.subheader(Configurações do Relatório de Turno)
    
    r_c1, r_c2, r_c3, r_c4 = st.columns(4)
    with r_c1
        r_data = st.date_input(Data de Referência, datetime.now(), format=DDMMYYYY, key=rep_date_input)
        r_exec = st.selectbox(Filtrar por Técnico, [Todos] + LISTA_TECNICOS, key=rep_exec)
        
        if tem_acesso_global
            r_equipe = st.selectbox(Equipe do Relatório, [Todas] + LISTA_EQUIPES_DINAMICA, key=rep_equipe_selectbox)
        else
            r_equipe = st.session_state.equipe
            
    with r_c2
        r_tipo = st.selectbox(Filtrar por Tipo, [Todos] + LISTA_TIPOS, key=rep_type_selectbox)
        r_urgencia = st.selectbox(Filtrar por Urgência, [Todos] + LISTA_URGENCIA, key=rep_urg_selectbox)
    with r_c3
        r_status = st.selectbox(Status no Relatório, [Apenas Concluídas, Todos os Status, Aberto, Em Andamento, Concluído], key=rep_status_selectbox)
    with r_c4
        tipo_relatorio = st.radio(Tipo de Relatório, [Relatório de Turno (Padrão), Relatório Geral], key=rep_mode_radio)

    if ultimo_relatorio not in st.session_state
        st.session_state.ultimo_relatorio = 

    if st.button(Compilar e Formatar Relatório, key=rep_compile_btn)
        st.session_state.imagens_relatorio = [] 
        r_data_str = r_data.strftime(%Y-%m-%d)
        r_data_br = r_data.strftime(%d%m%y)
        
        if tem_acesso_global and r_equipe == Todas
            cursor.execute(SELECT categoria, status, titulo, descricao, data_fim, data_inicio, executantes, tipo, urgencia, anexo, equipe FROM atividades)
        else
            target_eq = r_equipe if tem_acesso_global else st.session_state.equipe
            cursor.execute(SELECT categoria, status, titulo, descricao, data_fim, data_inicio, executantes, tipo, urgencia, anexo, equipe FROM atividades WHERE equipe = , (target_eq,))
            
        todos_r = cursor.fetchall()
        
        equipe_nome_uppercase = r_equipe.upper() if tem_acesso_global else st.session_state.equipe.upper()
        
        if tipo_relatorio == Relatório Geral
            atividades_filtradas_rel = []
            for r in todos_r
                if r[5] != r_data_str 
                    continue
                if r_exec != Todos and r_exec not in r[6]
                    continue
                if r_tipo != Todos and r_tipo not in r[7]
                    continue
                if r_urgencia != Todos and r_urgencia != r[8]
                    continue
                if r_status == Apenas Concluídas and r[1] != Concluído
                    continue
                elif r_status != Todos os Status and r_status != Apenas Concluídas and r[1] != r_status
                    continue
                    
                atividades_filtradas_rel.append(r)
                
            texto_relatorio = f📋 RELATÓRIO DE TURNO {equipe_nome_uppercase}nn📅 DATA DE REFERÊNCIA {r_data_br}nn
            mapeamento_emojis = {Concluído ✅, Em Andamento ⏳, Aberto 📌}
            
            if atividades_filtradas_rel
                for a in atividades_filtradas_rel
                    emoji = mapeamento_emojis.get(a[1], ▪️)
                    dt_ini_br = datetime.strptime(a[5], %Y-%m-%d).strftime(%d%m%Y) if a[5] else -
                    dt_fim_br = datetime.strptime(a[4], %Y-%m-%d).strftime(%d%m%Y) if a[4] else Em aberto
                    
                    texto_relatorio += f{emoji} {a[2]}n
                    texto_relatorio += f▪️ Categoria {a[0]}n
                    texto_relatorio += f▪️ Status {a[1]}n
                    texto_relatorio += f▪️ Urgência {a[8]}n
                    texto_relatorio += f▪️ Tipo {a[7] if a[7] else 'NA'}n
                    texto_relatorio += f▪️ Executante(s) {a[6]}n
                    texto_relatorio += f▪️ Data de Abertura {dt_ini_br}n
                    texto_relatorio += f▪️ Data de Finalização {dt_fim_br}n
                    if a[3]
                        texto_relatorio += f▪️ Descrição {a[3]}n
                        
                    if a[9]
                        lista_anx_rel = [img_r.strip() for img_r in a[9].split(,) if img_r.strip()]
                        nomes_limpos_rel = [img_r.split('_', 1)[-1] for img_r in lista_anx_rel]
                        texto_relatorio += f▪️ Imagens  Evidências {', '.join(nomes_limpos_rel)}n
                        
                    texto_relatorio += f▪️ Equipe Responsável {a[10]}n
                    texto_relatorio += n
            else
                texto_relatorio += ▪️ Nenhuma atividade encontrada nos parâmetros selecionados.n
                
            imagens_lote_acumuladas = []
            for row in atividades_filtradas_rel
                if row[9]
                    sub_split = [img_s.strip() for img_s in row[9].split(,) if img_s.strip()]
                    imagens_lote_acumuladas.extend(sub_split)
            st.session_state.imagens_relatorio = imagens_lote_acumuladas
                
        else
            seguranca = [r for r in todos_r if r[0] == Segurança and r[5] == r_data_str]
            cinco_s = [r for r in todos_r if r[0] == 5S and r[5] == r_data_str]
            
            atividades_turno = []
            for r in todos_r
                if r[0] != Atividade do Turno
                    continue
                if r_status == Apenas Concluídas and r[1] != Concluído
                    continue
                elif r_status != Todos os Status and r_status != Apenas Concluídas and r[1] != r_status
                    continue
                if r[1] == Concluído and r[4] != r_data_str
                    continue
                elif r[1] != Concluído and r[5] != r_data_str
                    continue
                if r_exec != Todos and r_exec not in r[6]
                    continue
                if r_tipo != Todos and r_tipo not in r[7]
                    continue
                if r_urgencia != Todos and r_urgencia != r[8]
                    continue
                    
                atividades_turno.append(r)
                
            texto_relatorio = f📋 RELATÓRIO DE TURNO {equipe_nome_uppercase}nn📅 DATA {r_data_br}nn
            
            texto_relatorio += 🛡️ SEGURANÇAn
            if seguranca
                for s in seguranca texto_relatorio += f▪️ {s[2]} {f'- {s[3]}' if s[3] else ''}n
            else
                texto_relatorio += ▪️ Sem intercorrências.n
                
            texto_relatorio += n🧹 5Sn
            if cinco_s
                for c in cinco_s texto_relatorio += f▪️ {c[2]} {f'- {c[3]}' if c[3] else ''}n
            else
                texto_relatorio += ▪️ Sala em conformidade, Organização contínua.n
                
            texto_relatorio += n🛠️ Atividades do turnonn
            
            if atividades_turno
                mapeamento_emojis_turno = {Concluído 🟢, Em Andamento 🟡, Aberto 🔴}
                for a in atividades_turno
                    emoji = mapeamento_emojis_turno.get(a[1], ▪️)
                    desc = f - {a[3]} if a[3] else 
                    texto_relatorio += f{emoji} {a[2]}{desc}nn
            else
                texto_relatorio += ▪️ Nenhuma atividade registradafinalizada nos parâmetros selecionados.n
                
            st.session_state.imagens_relatorio = []
                
        st.session_state.ultimo_relatorio = texto_relatorio

    if st.session_state.ultimo_relatorio
        st.write(---)
        st.subheader(📋 Relatório Compilado)
        st.write(Utilize o botão de cópia rápida localizado no canto superior direito do bloco abaixo)
        st.code(st.session_state.ultimo_relatorio, language=markdown)
        
        if tipo_relatorio == Relatório Geral and st.session_state.imagens_relatorio
            st.write(---)
            st.subheader(🖼️ Galeria de Imagens  Evidências do Relatório)
            for img in st.session_state.imagens_relatorio
                caminho_img = os.path.join(atividades_anexos, img)
                if os.path.exists(caminho_img)
                    nome_limpo = img.split('_', 1)[-1]
                    st.image(caminho_img, caption=fEvidência Técnica {nome_limpo}, width=450)

# -------------------------------------------------------------------------
# ABA 4 PAINEL DE SLA & MÉTRICAS
# -------------------------------------------------------------------------
with aba_sla
    st.subheader(Indicadores de Produtividade e Volumetria de Chamados)
    
    if tem_acesso_global
        sla_c1, sla_c2, sla_c3 = st.columns(3)
    else
        sla_c1, sla_c2 = st.columns(2)
        
    with sla_c1
        dt_inicio_sla = st.date_input(Data Inicial do Período, date(datetime.now().year, datetime.now().month, 1), format=DDMMYYYY, key=sla_start_input)
    with sla_c2
        dt_fim_sla = st.date_input(Data Final do Período, datetime.now(), format=DDMMYYYY, key=sla_end_input)
        
    if tem_acesso_global
        with sla_c3
            sla_equipe = st.selectbox(Equipe das Métricas, [Todas] + LISTA_EQUIPES_DINAMICA, key=sla_team_selectbox)
    else
        sla_equipe = st.session_state.equipe
        
    if tem_acesso_global and sla_equipe == Todas
        cursor.execute(
            SELECT categoria, status, tipo, executantes, urgencia, data_inicio 
            FROM atividades 
            WHERE data_inicio BETWEEN  AND 
        , (dt_inicio_sla.strftime(%Y-%m-%d), dt_fim_sla.strftime(%Y-%m-%d)))
    else
        target_eq = sla_equipe if tem_acesso_global else st.session_state.equipe
        cursor.execute(
            SELECT categoria, status, tipo, executantes, urgencia, data_inicio 
            FROM atividades 
            WHERE data_inicio BETWEEN  AND  AND equipe = 
        , (dt_inicio_sla.strftime(%Y-%m-%d), dt_fim_sla.strftime(%Y-%m-%d), target_eq))
        
    dados_sla = cursor.fetchall()
    
    if not dados_sla
        st.info(Sem dados operacionais para o período selecionado.)
    else
        df = pd.DataFrame(dados_sla, columns=[Categoria, Status, Tipo, Executantes, Urgência, Data])
        df_atividades = df[df[Categoria] == Atividade do Turno]
        
        if df_atividades.empty
            st.info(Nenhuma 'Atividade do Turno' cadastrada neste período para gerar gráficos.)
        else
            g_col1, g_col2 = st.columns(2)
            
            with g_col1
                st.markdown(📊 Volumetria por Tipo de Infraestrutura)
                df_tipos = df_atividades[Tipo].str.split(, ).explode()
                st.bar_chart(df_tipos.value_counts(), color=#1f77b4)
                
                st.markdown(⚖️ Demandas por Nível de Criticidade (Urgência))
                st.bar_chart(df_atividades[Urgência].value_counts(), color=#d62728)
                
            with g_col2
                st.markdown(👥 Distribuição de Carga de Trabalho por Executante)
                df_execs = df_atividades[Executantes].str.split(, ).explode()
                st.bar_chart(df_execs.value_counts(), color=#2ca02c)
                
                st.markdown(🔄 Status Atual do Backlog no Período)
                st.bar_chart(df_atividades[Status].value_counts(), color=#ff7f0e)

# -------------------------------------------------------------------------
# GESTÃO DE CONTAS & EQUIPES (Exclusiva para Perfil Admin - Chaves Travadas)
# -------------------------------------------------------------------------
if es_administrador
    with aba_usuarios
        st.subheader(👥 Painel Avançado de Governança)
        
        with st.form(form_novo_usuario)
            st.markdown(Adicionar Novo Usuário)
            u_c1, u_c2, u_c3, u_c4 = st.columns(4)
            with u_c1
                novo_nome = st.text_input(Nome do Usuário, placeholder=Ex Lucas, key=user_create_name)
            with u_c2
                nova_senha_user = st.text_input(Senha de Acesso, type=password, key=user_create_pass)
            with u_c3
                nova_perm = st.selectbox(Perfil de Acesso, [admin, tecnico, leitura, gestor], key=user_create_perm)
            with u_c4
                nova_equipe_user = st.selectbox(Equipe do Usuário, LISTA_EQUIPES_DINAMICA, key=user_create_team)
                
            btn_add_user = st.form_submit_button(➕ Cadastrar Usuário)
            
            if btn_add_user
                if not novo_nome or not nova_senha_user
                    st.error(❌ Preencha o nome e a senha do novo usuário!)
                else
                    try
                        cursor.execute(INSERT INTO usuarios VALUES (, , , ), (novo_nome, nova_senha_user, nova_perm, nova_equipe_user))
                        conn.commit()
                        st.success(f🎯 Usuário '{novo_nome}' cadastrado com sucesso para a equipe {nova_equipe_user}!)
                        st.rerun()
                    except sqlite3.IntegrityError
                        st.error(❌ Erro Já existe uma conta cadastrada com este nome.)
                        
        st.write(---)
        
        # Bloco Intermediário Edição de Contas Existentes com Chave Dedicada
        st.markdown(Editar ou Remover Contas Existentes)
        cursor.execute(SELECT nome FROM usuarios)
        lista_completa_users = [row[0] for row in cursor.fetchall()]
        
        if not lista_completa_users
            st.info(Nenhum usuário localizado no banco de dados.)
        else
            user_selecionado_gestao = st.selectbox(Selecione o usuário que deseja modificar, lista_completa_users, key=user_manage_select)
            
            cursor.execute(SELECT senha, permissao, equipe FROM usuarios WHERE nome = , (user_selecionado_gestao,))
            dados_user_gestao = cursor.fetchone()
            
            if dados_user_gestao
                with st.form(form_modificar_remover_usuario)
                    st.markdown(fAlterando credenciais de {user_selecionado_gestao})
                    
                    m_c1, m_c2, m_c3 = st.columns(3)
                    with m_c1
                        alt_senha = st.text_input(Alterar Senha de Acesso, value=dados_user_gestao[0], type=password, key=user_edit_pass)
                    with m_c2
                        lista_permissoes = [admin, tecnico, leitura, gestor]
                        idx_perm = lista_permissoes.index(dados_user_gestao[1]) if dados_user_gestao[1] in lista_permissoes else 1
                        alt_perm = st.selectbox(Alterar Perfil de Permissão, lista_permissoes, index=idx_perm, key=user_edit_perm)
                    with m_c3
                        idx_eq = LISTA_EQUIPES_DINAMICA.index(dados_user_gestao[2]) if dados_user_gestao[2] in LISTA_EQUIPES_DINAMICA else 0
                        alt_equipe = st.selectbox(Alterar Equipe Alocada, LISTA_EQUIPES_DINAMICA, index=idx_eq, key=user_edit_team)
                        
                    b_c1, b_c2 = st.columns(2)
                    with b_c1
                        btn_salvar_user = st.form_submit_button(💾 Gravar Alterações de Conta)
                    with b_c2
                        btn_deletar_user = st.form_submit_button(❌ Excluir Usuário do Sistema)
                        
                    if btn_salvar_user
                        cursor.execute(UPDATE usuarios SET senha = , permissao = , equipe =  WHERE nome = , (alt_senha, alt_perm, alt_equipe, user_selecionado_gestao))
                        conn.commit()
                        st.success(f🎯 Credenciais do usuário '{user_selecionado_gestao}' updated!)
                        st.rerun()
                        
                    if btn_deletar_user
                        if user_selecionado_gestao == st.session_state.usuario_logado
                            st.error(❌ Violação de Segurança Você não pode deletar a sua própria conta enquanto estiver logado nela!)
                        else
                            cursor.execute(DELETE FROM usuarios WHERE nome = , (user_selecionado_gestao,))
                            conn.commit()
                            st.success(f🗑️ O usuário '{user_selecionado_gestao}' foi removido do banco de dados.)
                            st.rerun()

        st.write(---)
        
        # Bloco Inferior Gerenciamento Dinâmico de Novas Equipes
        st.markdown(📁 Gerenciamento de Equipes Personalizadas)
        eq_c1, eq_c2 = st.columns(2)
        with eq_c1
            with st.form(form_nova_equipe)
                st.markdown(Criar Nova Equipe)
                nova_eq_nome = st.text_input(Nome da Nova Equipe, placeholder=Ex Infraestrutura, Redes, Suporte, key=team_create_name)
                btn_add_eq = st.form_submit_button(➕ Cadastrar Equipe)
                if btn_add_eq
                    if not nova_eq_nome
                        st.error(❌ O nome da equipe não pode ficar em branco!)
                    else
                        try
                            cursor.execute(INSERT INTO equipes VALUES (), (nova_eq_nome,))
                            conn.commit()
                            st.success(f🎯 Equipe '{nova_eq_nome}' criada com sucesso!)
                            st.rerun()
                        except sqlite3.IntegrityError
                            st.error(❌ Erro Essa equipe já está cadastrada no sistema.)
        with eq_c2
            with st.form(form_remover_equipe)
                st.markdown(Remover Equipe Existente)
                equipes_para_exclusao = [e for e in LISTA_EQUIPES_DINAMICA if e not in [Telecomunicações, Automação, Gestor]]
                eq_remover = st.selectbox(Selecione a equipe personalizada para excluir, equipes_para_exclusao, key=team_delete_select)
                btn_rem_eq = st.form_submit_button(🗑️ Remover Equipe)
                if btn_rem_eq
                    if eq_remover
                        cursor.execute(DELETE FROM equipes WHERE nome = , (eq_remover,))
                        conn.commit()
                        st.success(f🗑️ Equipe '{eq_remover}' removida com sucesso do sistema!)
                        st.rerun()
                    else
                        st.info(Nenhuma equipe personalizada disponível para exclusão no momento.)