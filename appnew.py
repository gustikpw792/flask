from flask import Flask
from v1.routes import bp_v1
from v2.routes import bp_v2

def create_app():
    app = Flask(__name__)
    
    # Daftarkan blueprint untuk kedua versi
    app.register_blueprint(bp_v1)
    app.register_blueprint(bp_v2)
    
    @app.route('/')
    def home():
        return {
            'message': 'API Server',
            'versions': ['v1', 'v2'],
            'endpoints': {
                'v1': '/v1/users',
                'v2': '/api/v2/users'
            }
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)