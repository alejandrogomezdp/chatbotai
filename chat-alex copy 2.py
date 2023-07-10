from flask import Flask, request, render_template, jsonify
import openai
import re
import mysql.connector
import json

app = Flask(__name__)

openai.api_key = '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'

# Conexión a la base de datos MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
)
cursor = db.cursor()

# Crea la base de datos si no existe
cursor.execute("CREATE DATABASE IF NOT EXISTS CONVERSACIONESYUSUARIOS")
db.database = "CONVERSACIONESYUSUARIOS"

# Crea las tablas si no existen
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))")
cursor.execute("CREATE TABLE IF NOT EXISTS conversations (id INT AUTO_INCREMENT PRIMARY KEY, user_input TEXT, chatbot_response TEXT)")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/chat', methods=['GET'])
def chat():
    # Obtiene todas las conversaciones guardadas
    cursor.execute("SELECT * FROM conversations")
    conversations = cursor.fetchall()
    return render_template('chat.html', conversations=conversations)

@app.route('/chat', methods=['POST'])
def chat_post():
    user_input = request.form['message']
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un experto en programación reconocido y tutor de codificación. Estás ayudando a un profesional con un problema de codificación."},
            {"role": "user", "content": user_input}
        ]
    )
    response = response.choices[0].message['content']
    response = format_response(response)  # Formatea la respuesta

    # Inserta la conversación en la base de datos
    insert_conversation(user_input, response)

    # Obtiene todas las conversaciones guardadas
    cursor.execute("SELECT * FROM conversations")
    conversations = cursor.fetchall()

    return render_template('chat.html', conversations=conversations, response=response)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Aquí va tu código para el inicio de sesión
        pass
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Inserta el nuevo usuario en la base de datos
        insert_user(username, password)

        # Redirige al inicio de sesión después del registro
        return render_template('login.html')

    return render_template('register.html')

def format_response(response):
    # Detecta y formatea bloques de código
    response = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', response, flags=re.DOTALL)

    # Divide el texto en párrafos
    paragraphs = response.split('\n\n')

    # Combina los párrafos formateados en una sola cadena
    formatted_response = '<p>'.join(paragraphs)

    return formatted_response

def insert_user(username, password):
    # Inserta el nuevo usuario en la base de datos
    sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
    val = (username, password)
    cursor.execute(sql, val)
    db.commit()

def insert_conversation(user_input, response):
    # Inserta la conversación en la base de datos
    sql = "INSERT INTO conversations (user_input, chatbot_response) VALUES (%s, %s)"
    val = (user_input, response)
    cursor.execute(sql, val)
    db.commit()

if __name__ == '__main__':
    app.run(debug=True)
