import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from google_agenda_to_firebird import (
    get_all_items, 
    save_items_to_firebird, 
    create_firebird_connection,
    get_google_service,
    get_items_from_firebird,
    setup_database
)

app = Flask(__name__)
CORS(app)  # Permite requisições do React Native

@app.route('/api/items', methods=['GET'])
def get_calendar_items():
    try:
        # Parâmetros de filtro
        exclude_titles = request.args.get('exclude_titles', 'Aniversário,Parabéns').split(',')
        item_type = request.args.get('type')  # 'event', 'task' ou None para ambos
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        con = create_firebird_connection()
        if not con:
            return jsonify({"success": False, "error": "Erro na conexão com o banco"}), 500

        # Busca itens do banco com filtros
        items = get_items_from_firebird(
            con, 
            exclude_titles=exclude_titles,
            item_type=item_type,
            start_date=datetime.datetime.fromisoformat(start_date) if start_date else None,
            end_date=datetime.datetime.fromisoformat(end_date) if end_date else None
        )

        if not items:
            calendar_service, tasks_service = get_google_service()
            if not calendar_service and not tasks_service:
                return jsonify({"success": False, "error": "Erro ao autenticar com os serviços do Google"}), 500

            # Busca todos os itens do Google
            items = get_all_items(calendar_service, tasks_service, exclude_titles)
            
            # Filtra por tipo se especificado
            if item_type:
                items = [item for item in items if item['tipo'] == item_type.upper()]
            
            # Salva no banco
            save_items_to_firebird(items, con)
            
            # Busca novamente para garantir formato consistente
            items = get_items_from_firebird(
                con, 
                exclude_titles=exclude_titles,
                item_type=item_type,
                start_date=datetime.datetime.fromisoformat(start_date) if start_date else None,
                end_date=datetime.datetime.fromisoformat(end_date) if end_date else None
            )

        con.close()
        
        # Converte datetime para string ISO
        for item in items:
            for field in ['inicio', 'fim', 'data_criacao', 'data_atualizacao']:
                if item.get(field) and isinstance(item[field], datetime.datetime):
                    item[field] = item[field].isoformat()
        
        return jsonify({
            "success": True, 
            "items": items,
            "counts": {
                "total": len(items),
                "events": sum(1 for i in items if i['tipo'] == 'EVENTO'),
                "tasks": sum(1 for i in items if i['tipo'] == 'TAREFA')
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='10.0.0.240', port=5555, debug=True)