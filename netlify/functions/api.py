import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'backend', 'src'))

from main import app

def handler(event, context):
    """
    Função handler para Netlify Functions
    """
    try:
        # Importar o app Flask
        from main import app
        
        # Configurar para produção
        app.config['ENV'] = 'production'
        app.config['DEBUG'] = False
        
        # Processar a requisição
        with app.test_request_context(
            path=event.get('path', '/'),
            method=event.get('httpMethod', 'GET'),
            headers=event.get('headers', {}),
            data=event.get('body', '')
        ):
            response = app.full_dispatch_request()
            
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }

