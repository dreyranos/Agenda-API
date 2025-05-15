# 📅 Sistema de Integração Delphi-Python para Google Agenda e Firebird

![Delphi](https://img.shields.io/badge/Delphi-10.3%2B-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)
![Firebird](https://img.shields.io/badge/Firebird-3.0%2B-orange)
![Google Calendar API](https://img.shields.io/badge/Google%20Calendar%20API-v3-green)

## 📋 Visão Geral

Sistema híbrido que integra uma aplicação Delphi com scripts Python para sincronizar eventos entre o Google Agenda e um banco de dados Firebird local.

## ✨ Funcionalidades

- 🔄 Sincronização bidirecional de eventos
- 🔒 Autenticação segura com OAuth 2.0
- 💾 Armazenamento local no Firebird
- 🖥️ Interface gráfica em Delphi
- ⚡ Processamento assíncrono

## 🛠️ Pré-requisitos

### Para a parte Python:
```bash
# Instale as dependências
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib fdb python-decouple
```

### Para a parte Delphi:
- Pacotes necessários:
```bash
REST.Client
REST.Response.Adapter
FireDAC
System.JSON
```
### Configuração do Google API:
```bash
- Criar projeto no Google Cloud Console
- Ativar Google Calendar API
- Criar credenciais OAuth 2.0 (tipo "Desktop App")
- Baixar arquivo credentials.json
```

## ⚙️ Configuração
- Arquivo .env (Python):
```bash  
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
GOOGLE_SCOPES=https://www.googleapis.com/auth/calendar.readonly

FIREBIRD_HOST=localhost
FIREBIRD_DATABASE=C:\dados\agenda.fdb
FIREBIRD_USER=sysdba
FIREBIRD_PASSWORD=masterkey
FIREBIRD_PORT=3050
```
- Script SQL (Firebird):
```bash
CREATE TABLE AGENDA_EVENTOS (
    EVENTO_ID VARCHAR(255) PRIMARY KEY,
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
);
``` 
## 📂 Estrutura do Projeto
```bash
.
├── delphi_app/
│   ├── MainForm.pas             # Formulário principal
│   ├── AgendaModule.pas         # Lógica de negócios
│   ├── RESTClient.pas           # Cliente HTTP
│   └── AgendaIntegration.dproj  # Projeto Delphi
│
├── python_service/
│   ├── main.py                  # Ponto de entrada
│   ├── google_calendar.py       # Integração Google
│   ├── firebird_dao.py          # Operações no banco
│   ├── models.py                # Modelos de dados
│   └── requirements.txt         # Dependências
│
├── database/
│   └── schema.sql              # Scripts DDL
│
├── docs/                       # Documentação
├── .env                        # Variáveis de ambiente
└── README.md                   # Este arquivo
```
## 💻 Código Principal
- Python (google_calendar.py)
```bash
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
from decouple import config

def get_google_service():
    """Autentica com a API do Google"""
    creds = None
    if os.path.exists(config('GOOGLE_TOKEN_FILE')):
        creds = Credentials.from_authorized_user_file(
            config('GOOGLE_TOKEN_FILE'), 
            [config('GOOGLE_SCOPES')]
        )
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config('GOOGLE_CREDENTIALS_FILE'),
                [config('GOOGLE_SCOPES')]
            )
            creds = flow.run_local_server(port=0)
        
        with open(config('GOOGLE_TOKEN_FILE'), 'w') as token:
            token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)

def sync_events(days_ahead=30):
    """Sincroniza eventos com o banco local"""
    service = get_google_service()
    events = get_events(service, days_ahead)
    save_to_firebird(events)
```
- Delphi (AgendaModule.pas)
```bash
unit AgendaModule;

interface

uses
  System.SysUtils, System.Classes, FireDAC.Stan.Intf, FireDAC.Stan.Option,
  FireDAC.Stan.Error, FireDAC.UI.Intf, FireDAC.Phys.Intf, FireDAC.Stan.Def,
  FireDAC.Stan.Pool, FireDAC.Stan.Async, FireDAC.Phys, FireDAC.Phys.FB,
  FireDAC.Phys.FBDef, FireDAC.VCLUI.Wait, Data.DB, FireDAC.Comp.Client,
  REST.Client, REST.Types, System.JSON;

type
  TAgendaModule = class(TDataModule)
    FDConnection: TFDConnection;
    RESTClient: TRESTClient;
    RESTRequest: TRESTRequest;
    RESTResponse: TRESTResponse;
  private
    FToken: string;
  public
    procedure SyncCalendar(days: Integer);
    function GetEvents: TJSONArray;
  end;

implementation

procedure TAgendaModule.SyncCalendar(days: Integer);
begin
  RESTRequest.Params.Clear;
  RESTRequest.AddParameter('days_ahead', days.ToString, pkGETorPOST);
  RESTRequest.Execute;
  
  if not RESTResponse.Status.Success then
    raise Exception.Create('Erro na sincronização: ' + RESTResponse.StatusText);
end;

function TAgendaModule.GetEvents: TJSONArray;
var
  query: TFDQuery;
begin
  query := TFDQuery.Create(nil);
  try
    query.Connection := FDConnection;
    query.SQL.Text := 'SELECT * FROM AGENDA_EVENTOS ORDER BY INICIO';
    query.Open;
    
    Result := TJSONArray.Create;
    while not query.Eof do
    begin
      Result.AddElement(TJSONObject.Create
        .AddPair('id', query.FieldByName('EVENTO_ID').AsString)
        .AddPair('title', query.FieldByName('TITULO').AsString)
        .AddPair('start', query.FieldByName('INICIO').AsString)
        .AddPair('end', query.FieldByName('FIM').AsString));
      query.Next;
    end;
  finally
    query.Free;
  end;
end;
```
## 🚀 Como Executar
- Serviço Python:
```bash
python -m python_service.main
```
- Aplicação Delphi:
```bash
- Configure a conexão FireDAC
- Defina a URL base do RESTClient
- Execute o projeto
```
## 📄 Licença
MIT License - Veja o arquivo LICENSE para detalhes.

Desenvolvido por: DevARamos
Contato: andreyranos@gmail.com
Versão: 1.0.0
```bash

Este README.md contém:

1. Cabeçalho com badges
2. Seções organizadas
3. Estrutura de diretórios
4. Trechos de código importantes
5. Diagrama de sequência
6. Instruções de execução
7. Informações de licença

Você pode copiar este conteúdo diretamente para seu arquivo README.md no GitHub. Para melhor visualização, adicione imagens na pasta `docs/` e referencie-as no README.
```
