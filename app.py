from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "LTIPsecretkey"

# --- Configuração do banco SQLite ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ltip.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Configuração de upload ---
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

# --- Modelo de Equipamento ---
class Equipamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipamento = db.Column(db.String(100), nullable=False)
    funcionalidade = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    quantidade = db.Column(db.Integer, default=1)
    tombo = db.Column(db.String(50))
    imagem = db.Column(db.String(100))

    def __repr__(self):
        return f'<Equipamento {self.equipamento}>'

# --- Função para validar upload ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- ROTAS ---

# Página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Inventário
@app.route('/inventario')
def inventario():
    equipamentos = Equipamento.query.all()
    return render_template('inventario.html', equipamentos=equipamentos)

# Cadastrar equipamento
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        eq = request.form['equipamento']
        func = request.form['funcionalidade']
        marca = request.form['marca']
        modelo = request.form['modelo']
        quantidade = request.form['quantidade']
        tombo = request.form['tombo']

        # Upload de imagem
        file = request.files['imagem']
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        novo_eq = Equipamento(
            equipamento=eq,
            funcionalidade=func,
            marca=marca,
            modelo=modelo,
            quantidade=int(quantidade),
            tombo=tombo,
            imagem=filename
        )
        db.session.add(novo_eq)
        db.session.commit()
        flash("Equipamento cadastrado com sucesso!")
        return redirect(url_for('inventario'))

    return render_template('cadastrar.html')

# Gerenciamento de máquinas (página em branco para você adicionar depois)
@app.route('/gerenciar')
def gerenciar():
    return render_template('gerenciar.html')

# Relatórios (página em branco para você adicionar depois)
@app.route('/relatorios')
def relatorios():
    return render_template('relatorios.html')

# Status do servidor
@app.route('/status')
def status():
    return "LTIP Laboratory - Deploy funcionando! Render OK ✅"

# --- Executar ---
if __name__ == '__main__':
    db.create_all()  # cria o banco se não existir
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
