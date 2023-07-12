from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import openai
import re

app = Flask(__name__)
app.secret_key = '5p2L=H4jmy76Cg95Q35+'
openai.api_key = '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'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://phpmyadmin:eminem92AA!!@localhost/superAntena'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.String(1000), nullable=False)
    chatbot_response = db.Column(db.String(5000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('conversations', lazy=True))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return render_template('index.html')


@app.route('/chat', methods=['GET'])
@login_required
def chat():
    conversations = Conversation.query.filter_by(user_id=current_user.id).all()
    return render_template('chat.html', conversations=conversations)


@app.route('/chat', methods=['POST'])
def chat_post():
    data = request.get_json()
    user_input = data['message']
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un experto en programación reconocido y tutor de codificación en python y javascript. Estás ayudando a un profesional con un problema de codificación."},
            {"role": "user", "content": user_input}
        ]
    )
    response = response.choices[0].message['content']
    response = format_response(response)

    convo = Conversation(user_input=user_input, chatbot_response=response, user_id=current_user.id)
    db.session.add(convo)
    db.session.commit()

    return jsonify(response=response)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Has iniciado sesión correctamente', 'success')
            return redirect(url_for('chat'))
        else:
            flash('Error en el inicio de sesión. Por favor, inténtalo de nuevo.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        flash('Te has registrado con éxito. Por favor, inicia sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


def format_response(response):
    response = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', response, flags=re.DOTALL)
    paragraphs = response.split('\n\n')
    formatted_response = '<p>'.join(paragraphs)

    return formatted_response


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
