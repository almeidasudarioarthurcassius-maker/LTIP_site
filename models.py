from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()

def init_db_and_create_default_users(app):
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado com sucesso.")

def register_routes(app):
    @app.route("/")
    def index():
        return "<h1>LTIP Laboratory - Deploy funcionando!</h1><p>Render OK ✅</p>"
