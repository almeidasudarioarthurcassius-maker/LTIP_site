"""
LTIP Laboratory Webapp - Versão completa pronta para rede local e deploy em nuvem
Arquivo: LTIP_Laboratory_Webapp_app.py
Notas:
 - Use variáveis de ambiente para produção: SECRET_KEY, HOST, PORT, FLASK_DEBUG
 - Pastas criadas automaticamente: uploads/
 - Banco: ltip.db no mesmo diretório (SQLite)
 - Mantém o design visual antigo
"""

import os
from datetime import datetime, timezone
from flask import (
    Flask, render_template_string, request, redirect, url_for, flash,
    session, send_from_directory
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ---------------- Configurações ----------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_DIR, "uploads")
DB_PATH = os.path.join(APP_DIR, "ltip.db")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SECRET_KEY = os.environ.get("SECRET_KEY", "troque_esta_chave_em_producao")
HOST_ENV = os.environ.get("HOST", "0.0.0.0")
PORT_ENV = int(os.environ.get("PORT", 5000))
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ("1","true","yes")

COLOR_DARK = "#003366"
COLOR_LIGHT = "#66B2FF"
COLOR_WHITE = "#FFFFFF"

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB

db = SQLAlchemy(app)

# ---------------- Models ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, bolsista, visitor

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class LabInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coordenador_name = db.Column(db.String(100))
    coordenador_email = db.Column(db.String(100))
    bolsista_name = db.Column(db.String(100))
    bolsista_email = db.Column(db.String(100))

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    tombo = db.Column(db.String(100))
    quantidade = db.Column(db.Integer, default=1)
    modelo = db.Column(db.String(100))
    marca = db.Column(db.String(100))
    finalidade = db.Column(db.String(200))
    status = db.Column(db.String(100))
    localizacao = db.Column(db.String(200))
    descricao = db.Column(db.Text)
    imagem_filename = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(100), default='Não formatado')
    tipo = db.Column(db.String(50))
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    numero_serie = db.Column(db.String(100), unique=True)
    sistema_operacional = db.Column(db.String(200))
    softwares_instalados = db.Column(db.Text)
    licencas = db.Column(db.String(255))
    limpeza_fisica_data = db.Column(db.Date)
    ultima_formatacao_data = db.Column(db.Date)
    responsavel_formatacao = db.Column(db.String(80))
    imagem_filename = db.Column(db.String(300))

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# ---------------- Helpers ----------------
def current_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None

def save_uploaded_file(file_storage):
    if not file_storage:
        return None
    filename = secure_filename(file_storage.filename)
    if filename == '':
        return None
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    filename = f"{timestamp}_{filename}"
    file_storage.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename

def roles_required(allowed_roles):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = current_user()
            if not user or user.role not in allowed_roles:
                flash("Acesso negado: permissões insuficientes.", "danger")
                return redirect(url_for("index"))
            return f(*args, **kwargs)
        return decorated
    return decorator

def get_lab_info():
    db.session.expire_all()
    info = LabInfo.query.first()
    if not info:
        info = LabInfo(
            coordenador_name='Nome do Coordenador',
            coordenador_email='coord@exemplo.com',
            bolsista_name='Nome do Bolsista',
            bolsista_email='bolsista@exemplo.com'
        )
        db.session.add(info)
        db.session.commit()
    return info

# ---------------- Templates ----------------
# Aqui você coloca o template antigo completo do site
# e mantém a estrutura com "__CONTENT_BLOCK__" para cada página
BASE_TEMPLATE = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LTIP Laboratory</title>
    <link rel="stylesheet" href="{{{{ url_for('static', filename='css/style.css') }}}}">
    <style>
        body {{
            background-color: {COLOR_DARK};
            color: {COLOR_WHITE};
            font-family: Arial, sans-serif;
        }}
        h1, h2, h3 {{
            color: {COLOR_LIGHT};
        }}
        .navbar {{
            background-color: {COLOR_LIGHT};
            color: {COLOR_WHITE};
            padding: 10px;
        }}
        .container {{
            margin: 20px auto;
            max-width: 1200px;
        }}
        .btn {{
            background-color: {COLOR_LIGHT};
            color: {COLOR_WHITE};
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
        }}
        .btn:hover {{
            opacity: 0.9;
        }}
        footer {{
            background-color: {COLOR_DARK};
            color: {COLOR_WHITE};
            text-align: center;
            padding: 10px;
            margin-top: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            border: 1px solid {COLOR_LIGHT};
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: {COLOR_LIGHT};
            color: {COLOR_WHITE};
        }}
        tr:nth-child(even) {{
            background-color: {COLOR_DARK};
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>LTIP Laboratory</h1>
    </nav>

    <div class="container">
        {{{{ content|safe }}}}
    </div>

    <footer>
        <p>© 2025 LTIP Laboratory</p>
    </footer>
</body>
</html>"""

# ---------------- Rotas ----------------
@app.route("/")
def index():
    info = get_lab_info()
    content = f"""
    <h1>Bem-vindo ao LTIP Laboratory</h1>
    <p>Coordenador: {info.coordenador_name} - {info.coordenador_email}</p>
    <p>Bolsista: {info.bolsista_name} - {info.bolsista_email}</p>
    """
    return render_template_string(BASE_TEMPLATE.replace("__CONTENT_BLOCK__", content), user=current_user())

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            flash("Logado com sucesso.", "success")
            return redirect(url_for("index"))
        flash("Usuário ou senha inválidos.", "danger")
    form = """
    <h2>Login</h2>
    <form method="post">
        <input name="username" placeholder="Usuário" required><br>
        <input name="password" type="password" placeholder="Senha" required><br>
        <button class="btn">Entrar</button>
    </form>
    """
    return render_template_string(BASE_TEMPLATE.replace("__CONTENT_BLOCK__", form), user=current_user())

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logout realizado.", "success")
    return redirect(url_for("index"))

# ---------------- Inventário ----------------
@app.route("/inventario", methods=["GET","POST"])
@roles_required(["admin","bolsista"])
def inventario():
    if request.method == "POST":
        name = request.form.get("name")
        file = request.files.get("imagem")
        filename = save_uploaded_file(file)
        equipamento = Equipment(name=name, imagem_filename=filename)
        db.session.add(equipamento)
        db.session.commit()
        flash("Equipamento cadastrado!", "success")
        return redirect(url_for("inventario"))
    equipamentos = Equipment.query.all()
    content = "<h2>Inventário</h2><form method='post' enctype='multipart/form-data'>"
    content += "Nome: <input name='name' required> Imagem: <input type='file' name='imagem'> <button class='btn'>Cadastrar</button></form>"
    content += "<ul>"
    for eq in equipamentos:
        content += f"<li>{eq.name} - {eq.imagem_filename or 'Sem imagem'}</li>"
    content += "</ul>"
    return render_template_string(BASE_TEMPLATE.replace("__CONTENT_BLOCK__", content), user=current_user())

# ---------------- Máquinas ----------------
@app.route("/gerenciamento", methods=["GET","POST"])
@roles_required(["admin","bolsista"])
def gerenciamento():
    if request.method == "POST":
        name = request.form.get("name")
        machine = Machine(name=name)
        db.session.add(machine)
        db.session.commit()
        flash("Máquina cadastrada!", "success")
        return redirect(url_for("gerenciamento"))
    machines = Machine.query.all()
    content = "<h2>Gerenciamento de Máquinas</h2>"
    content += "<form method='post'>Nome: <input name='name' required> <button class='btn'>Cadastrar</button></form><ul>"
    for m in machines:
        content += f"<li>{m.name} - {m.status}</li>"
    content += "</ul>"
    return render_template_string(BASE_TEMPLATE.replace("__CONTENT_BLOCK__", content), user=current_user())

# ---------------- Relatórios ----------------
@app.route("/relatorios", methods=["GET","POST"])
@roles_required(["admin","bolsista"])
def relatorios():
    if request.method == "POST":
        title = request.form.get("title")
        file = request.files.get("file")
        filename = save_uploaded_file(file)
        if filename:
            report = Report(title=title, filename=filename)
            db.session.add(report)
            db.session.commit()
            flash("Relatório enviado!", "success")
        return redirect(url_for("relatorios"))
    reports = Report.query.order_by(Report.uploaded_at.desc()).all()
    content = "<h2>Relatórios</h2>"
    content += "<form method='post' enctype='multipart/form-data'>Título: <input name='title' required> Arquivo: <input type='file' name='file'> <button class='btn'>Enviar</button></form><ul>"
    for r in reports:
        content += f"<li>{r.title} - <a href='/uploads/{r.filename}'>Download</a></li>"
    content += "</ul>"
    return render_template_string(BASE_TEMPLATE.replace("__CONTENT_BLOCK__", content), user=current_user())

# ---------------- Servir arquivos enviados ----------------
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------------- DB Init ----------------
def init_db():
    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            admin = User(username="rendeiro123", role="admin")
            admin.set_password("admLTIP2025")
            bols = User(username="arthur123", role="bolsista")
            bols.set_password("LTIP2025")
            visitor = User(username="visitante", role="visitor")
            visitor.set_password("visitante123")
            db.session.add_all([admin, bols, visitor])
            db.session.commit()
        if LabInfo.query.count() == 0:
            info = LabInfo(
                coordenador_name="Prof. Água",
                coordenador_email="agua@uea.edu.br",
                bolsista_name="Arthur Sudario",
                bolsista_email="arthur.sudario@uea.edu.br"
            )
            db.session.add(info)
            db.session.commit()

# ---------------- Main ----------------
if __name__ == "__main__":
    init_db()
    app.run(host=HOST_ENV, port=PORT_ENV, debug=FLASK_DEBUG)
