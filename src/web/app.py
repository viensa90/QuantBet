from flask import Flask, render_template
from src.web.api import api_bp
from src.storage.database import Database

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    return app

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)