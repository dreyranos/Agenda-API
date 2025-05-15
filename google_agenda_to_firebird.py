import os
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import fdb 
import pandas as pd
from typing import List, Dict

# Configurações
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/tasks.readonly',
    'https://www.googleapis.com/auth/tasks' 
]
FIREBIRD_CONFIG = {
    'host': 'localhost',
    'database': 'C:\AgendaBot\database\database.fdb',
    'user': 'sysdba',
    'password': 'masterkey',
    'port': 3050,
    'charset': 'WIN1252'
}
def get_google_service():
    """Autentica e retorna serviços do Google Calendar e Tasks"""
    creds = None
    try:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(
                    port=0,
                    authorization_prompt_message='Por favor, autorize o acesso ao seu Google Agenda e Tarefas',
                    success_message='Autenticação concluída! Você pode fechar esta janela.',
                    open_browser=True
                )
            
            # Salva as credenciais com os novos escopos
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        # Retorna ambos os serviços
        calendar_service = build('calendar', 'v3', credentials=creds)
        tasks_service = build('tasks', 'v1', credentials=creds)
        return calendar_service, tasks_service
    
    except Exception as e:
        print(f"Erro de autenticação: {e}")
        return None, None
def get_items_from_firebird(
    con, 
    exclude_titles=None, 
    item_type=None, 
    start_date=None, 
    end_date=None
) -> List[Dict]:
    """Busca itens no Firebird com vários filtros"""
    if exclude_titles is None:
        exclude_titles = ["Aniversário", "Parabéns"]
    
    cursor = con.cursor()

    # Construção dinâmica da cláusula WHERE
    conditions = []
    
    # Filtro por tipo
    if item_type:
        conditions.append(f"TIPO = '{item_type.upper()}'")
    
    # Filtro por título
    if exclude_titles:
        conditions.extend(
            f"LOWER(TITULO) NOT LIKE LOWER('%{title}%')" 
            for title in exclude_titles
        )
    
    # Filtro por data
    if start_date and end_date:
        conditions.append("INICIO BETWEEN ? AND ?")
    elif start_date:
        conditions.append("INICIO >= ?")
    elif end_date:
        conditions.append("INICIO <= ?")
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT 
            EVENTO_ID, TIPO, TITULO, DESCRICAO, INICIO, FIM, 
            LOCALIZACAO, STATUS, DATA_CRIACAO, DATA_ATUALIZACAO, 
            CRIADOR, ORGANIZADOR
        FROM AGENDA_EVENTOS
        {where_clause}
        ORDER BY INICIO
    """

    # Parâmetros para a query
    params = []
    if start_date and end_date:
        params.extend([start_date, end_date])
    elif start_date:
        params.append(start_date)
    elif end_date:
        params.append(end_date)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    if not rows:
        return []

    columns = [desc[0].strip().lower() for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]
def get_google_service():
    """Autentica e retorna serviços do Google Calendar e Tasks"""
    creds = None
    try:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(
                    port=0,
                    authorization_prompt_message='Por favor, autorize o acesso ao seu Google Agenda e Tarefas',
                    success_message='Autenticação concluída! Você pode fechar esta janela.',
                    open_browser=True
                )
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        # Retorna ambos os serviços
        calendar_service = build('calendar', 'v3', credentials=creds)
        tasks_service = build('tasks', 'v1', credentials=creds)
        return calendar_service, tasks_service
    
    except Exception as e:
        print(f"Erro de autenticação: {e}")
        return None, None

def get_all_items(calendar_service, tasks_service, exclude_titles=None):
    """Busca tanto eventos quanto tarefas do Google com tratamento de erros"""
    if exclude_titles is None:
        exclude_titles = ["Aniversário", "Parabéns"]
    
    all_items = []
    
    # 1. Busca eventos do Google Calendar
    if calendar_service:
        try:
            print("Buscando eventos do Google Calendar...")
            events_result = calendar_service.events().list(
                calendarId='primary',
                singleEvents=True,
                orderBy='startTime',
                maxResults=2500
            ).execute()
            
            items = events_result.get('items', [])
            print(f"Encontrados {len(items)} eventos")
            
            for event in items:
                try:
                    title = event.get('summary', '')
                    if any(exclude_title.lower() in title.lower() for exclude_title in exclude_titles):
                        continue
                        
                    all_items.append({
                        'tipo': 'EVENTO',
                        'id': event['id'],
                        'titulo': title,
                        'descricao': event.get('description', ''),
                        'inicio': event['start'].get('dateTime', event['start'].get('date')),
                        'fim': event['end'].get('dateTime', event['end'].get('date')),
                        'localizacao': event.get('location', ''),
                        'status': event.get('status', ''),
                        'data_criacao': event.get('created', ''),
                        'data_atualizacao': event.get('updated', ''),
                        'criador': event.get('creator', {}).get('email', ''),
                        'organizador': event.get('organizer', {}).get('email', '')
                    })
                except Exception as event_error:
                    print(f"Erro ao processar evento {event.get('id', 'sem-ID')}: {str(event_error)}")
                    
        except Exception as calendar_error:
            print(f"Erro grave ao acessar Google Calendar: {str(calendar_error)}")
            print("Verifique se:")
            print("- A API Google Calendar está habilitada")
            print("- O token de acesso é válido")
            print("- Os escopos estão corretos")
    
    # 2. Busca tarefas do Google Tasks
    if tasks_service:
        try:
            print("Buscando tarefas do Google Tasks...")
            tasks_result = tasks_service.tasks().list(
                tasklist='@default',
                showCompleted=False,
                maxResults=100
            ).execute()
            
            items = tasks_result.get('items', [])
            print(f"Encontradas {len(items)} tarefas")
            
            for task in items:
                try:
                    all_items.append({
                        'tipo': 'TAREFA',
                        'id': task['id'],
                        'titulo': task.get('title', 'Tarefa sem título'),
                        'descricao': task.get('notes', ''),
                        'inicio': task.get('due'),  # Data de vencimento
                        'fim': task.get('due'),     # Tarefas geralmente só tem uma data
                        'status': 'completed' if task.get('status') == 'completed' else 'needsAction',
                        'data_criacao': task.get('updated'),  # Tasks API não fornece created
                        'data_atualizacao': task.get('updated'),
                        'criador': 'Tarefa',  # Tarefas não tem criador específico
                        'organizador': 'Tarefa'
                    })
                except Exception as task_error:
                    print(f"Erro ao processar tarefa {task.get('id', 'sem-ID')}: {str(task_error)}")
                    
        except Exception as tasks_error:
            print(f"Erro grave ao acessar Google Tasks: {str(tasks_error)}")
            print("Verifique se:")
            print("- A API Google Tasks está habilitada")
            print("- O token tem os escopos necessários")
            print("- O arquivo token.json foi gerado com as permissões corretas")
            print("Dica: Delete o token.json e execute novamente para reautenticar")
    
    # 3. Log final
    event_count = sum(1 for item in all_items if item['tipo'] == 'EVENTO')
    task_count = sum(1 for item in all_items if item['tipo'] == 'TAREFA')
    print(f"Total de itens processados: {len(all_items)} ({event_count} eventos e {task_count} tarefas)")
    
    return all_items

def setup_database(con):
    """Cria ou atualiza a tabela com ID auto-incremento como chave primária"""
    cursor = con.cursor()
    
    # Verifica se a tabela existe
    cursor.execute("""
    SELECT RDB$RELATION_NAME 
    FROM RDB$RELATIONS 
    WHERE RDB$RELATION_NAME = 'AGENDA_EVENTOS'
    """)
    
    if not cursor.fetchone():
        # Cria a tabela com ID auto-incremento
        cursor.execute("""
        CREATE TABLE AGENDA_EVENTOS (
            ID INTEGER NOT NULL PRIMARY KEY,
            EVENTO_ID VARCHAR(255),
            TIPO VARCHAR(10),  -- 'EVENTO' ou 'TAREFA'
            TITULO VARCHAR(255),
            DESCRICAO BLOB SUB_TYPE TEXT,
            INICIO TIMESTAMP,
            FIM TIMESTAMP,
            LOCALIZACAO VARCHAR(255),
            STATUS VARCHAR(50),
            DATA_CRIACAO TIMESTAMP,
            DATA_ATUALIZACAO TIMESTAMP,
            CRIADOR VARCHAR(255),
            ORGANIZADOR VARCHAR(255),
            DATA_IMPORTACAO TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Cria a sequência para auto-incremento
        cursor.execute("CREATE SEQUENCE GEN_AGENDA_EVENTOS_ID")
        
        # Cria o trigger para auto-incremento
        cursor.execute("""
        CREATE TRIGGER AGENDA_EVENTOS_BI FOR AGENDA_EVENTOS
        ACTIVE BEFORE INSERT POSITION 0
        AS
        BEGIN
            IF (NEW.ID IS NULL) THEN
                NEW.ID = GEN_ID(GEN_AGENDA_EVENTOS_ID, 1);
        END
        """)
        
        con.commit()
        print("Tabela AGENDA_EVENTOS criada com sucesso com ID auto-incremento.")
    else:
        # Verifica se a coluna ID já existe
        cursor.execute("""
        SELECT RDB$FIELD_NAME 
        FROM RDB$RELATION_FIELDS 
        WHERE RDB$RELATION_NAME = 'AGENDA_EVENTOS' AND RDB$FIELD_NAME = 'ID'
        """)
        
        if not cursor.fetchone():
            # Adiciona a coluna ID e configura auto-incremento
            cursor.execute("ALTER TABLE AGENDA_EVENTOS ADD ID INTEGER")
            
            # Cria a sequência se não existir
            cursor.execute("""
            SELECT RDB$GENERATOR_NAME 
            FROM RDB$GENERATORS 
            WHERE RDB$GENERATOR_NAME = 'GEN_AGENDA_EVENTOS_ID'
            """)
            if not cursor.fetchone():
                cursor.execute("CREATE SEQUENCE GEN_AGENDA_EVENTOS_ID")
            
            # Configura os valores iniciais
            cursor.execute("""
            UPDATE AGENDA_EVENTOS SET ID = GEN_ID(GEN_AGENDA_EVENTOS_ID, 1)
            WHERE ID IS NULL
            """)
            
            # Define como NOT NULL e PRIMARY KEY
            cursor.execute("ALTER TABLE AGENDA_EVENTOS ALTER COLUMN ID SET NOT NULL")
            cursor.execute("ALTER TABLE AGENDA_EVENTOS ADD PRIMARY KEY (ID)")
            
            # Cria o trigger para auto-incremento
            cursor.execute("""
            CREATE TRIGGER AGENDA_EVENTOS_BI FOR AGENDA_EVENTOS
            ACTIVE BEFORE INSERT POSITION 0
            AS
            BEGIN
                IF (NEW.ID IS NULL) THEN
                    NEW.ID = GEN_ID(GEN_AGENDA_EVENTOS_ID, 1);
            END
            """)
            
            con.commit()
            print("Coluna ID auto-incremento adicionada à tabela AGENDA_EVENTOS.")
        
        # Verifica e adiciona a coluna TIPO se necessário
        cursor.execute("""
        SELECT RDB$FIELD_NAME 
        FROM RDB$RELATION_FIELDS 
        WHERE RDB$RELATION_NAME = 'AGENDA_EVENTOS' AND RDB$FIELD_NAME = 'TIPO'
        """)
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE AGENDA_EVENTOS ADD TIPO VARCHAR(10)")
            con.commit()
            print("Coluna TIPO adicionada à tabela AGENDA_EVENTOS.")

def save_items_to_firebird(items: List[Dict], con):
    """Salva tanto eventos quanto tarefas no Firebird"""
    if not items:
        print("Nenhum item para salvar")
        return
    
    cursor = con.cursor()
    saved_count = {'EVENTO': 0, 'TAREFA': 0}
    
    for item in items:
        try:
            # Converte datas (tratamento especial para tarefas que podem não ter datas)
            inicio = pd.to_datetime(item['inicio']).to_pydatetime() if item['inicio'] else None
            fim = pd.to_datetime(item['fim']).to_pydatetime() if item['fim'] else None
            criacao = pd.to_datetime(item['data_criacao']).to_pydatetime() if item['data_criacao'] else None
            atualizacao = pd.to_datetime(item['data_atualizacao']).to_pydatetime() if item['data_atualizacao'] else None
            
            # Verifica se o item já existe
            cursor.execute("SELECT 1 FROM AGENDA_EVENTOS WHERE EVENTO_ID = ?", (item['id'],))
            exists = cursor.fetchone()
            
            if exists:
                # Atualiza o item existente
                cursor.execute("""
                UPDATE AGENDA_EVENTOS SET
                    TIPO = ?,
                    TITULO = ?,
                    DESCRICAO = ?,
                    INICIO = ?,
                    FIM = ?,
                    LOCALIZACAO = ?,
                    STATUS = ?,
                    DATA_ATUALIZACAO = ?,
                    ORGANIZADOR = ?
                WHERE EVENTO_ID = ?
                """, (
                    item['id'],
                    item['tipo'],
                    item['titulo'],
                    item['descricao'],
                    inicio,
                    fim,
                    item.get('localizacao', ''),
                    item['status'],
                    atualizacao,
                    item['organizador'],
                    item['id']
                ))
            else:
                # Insere novo item
                cursor.execute("""
                INSERT INTO AGENDA_EVENTOS (
                    EVENTO_ID, TIPO, TITULO, DESCRICAO, INICIO, FIM, 
                    LOCALIZACAO, STATUS, DATA_CRIACAO, DATA_ATUALIZACAO, 
                    CRIADOR, ORGANIZADOR
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item['id'],
                    item['tipo'],
                    item['titulo'],
                    item['descricao'],
                    inicio,
                    fim,
                    item.get('localizacao', ''),
                    item['status'],
                    criacao,
                    atualizacao,
                    item['criador'],
                    item['organizador']
                ))
            
            con.commit()
            saved_count[item['tipo']] += 1
            
        except Exception as e:
            print(f"Erro ao processar {item['tipo']} {item['id']}: {e}")
            con.rollback()
    
    print(f"Items salvos com sucesso: {saved_count['EVENTO']} eventos e {saved_count['TAREFA']} tarefas")
    
def create_firebird_connection():
    """Cria conexão com o banco Firebird"""
    try:
        con = fdb.connect(
            host=FIREBIRD_CONFIG['host'],
            database=FIREBIRD_CONFIG['database'],
            user=FIREBIRD_CONFIG['user'],
            password=FIREBIRD_CONFIG['password'],
            port=FIREBIRD_CONFIG['port'],
            charset=FIREBIRD_CONFIG['charset']
        )
        return con
    except Exception as e:
        print(f"Erro ao conectar ao Firebird: {e}")
        print("Verifique:")
        print(f"- Se o arquivo do banco existe: {FIREBIRD_CONFIG['database']}")
        print(f"- Usuário/senha: {FIREBIRD_CONFIG['user']}/{FIREBIRD_CONFIG['password']}")
        print(f"- Servidor/porta: {FIREBIRD_CONFIG['host']}:{FIREBIRD_CONFIG['port']}")
        return None
def main():
    # Autentica nos serviços do Google
    calendar_service, tasks_service = get_google_service()
    
    if not calendar_service and not tasks_service:
        print("Falha na autenticação com os serviços do Google")
        return
    
    # Busca todos os itens (eventos e tarefas)
    items = get_all_items(calendar_service, tasks_service)
    
    if not items:
        print("Nenhum item encontrado.")
        return
    
    # Conecta ao Firebird
    con = create_firebird_connection()
    if not con:
        return
    
    try:
        # Configura/atualiza o banco de dados
        setup_database(con)
        
        # Salva os itens
        save_items_to_firebird(items, con)
        print(f"{len(items)} itens processados com sucesso ({sum(1 for i in items if i['tipo'] == 'EVENTO')} eventos e {sum(1 for i in items if i['tipo'] == 'TAREFA')} tarefas).")
    finally:
        con.close()

if __name__ == '__main__':
    main()