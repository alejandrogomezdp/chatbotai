from flask import Flask, request, render_template, jsonify
import openai
import re
import json

app = Flask(__name__)

openai.api_key = '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'

# Cargar base de datos JSON
def load_db():
    with open('database.json', 'r') as file:
        db = json.load(file)
    return db

# Guardar base de datos JSON
def save_db(db):
    with open('database.json', 'w') as file:
        json.dump(db, file, indent=4)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/chat', methods=['GET'])
def chat():
    db = load_db()
    return render_template('chat.html', conversations=db["conversations"])

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
    response = format_response(response)  # Formatea la respuesta

    # Inserta la conversación en la base de datos
    db = load_db()
    db["conversations"].append({"user_input": user_input, "chatbot_response": response})
    save_db(db)

    return jsonify(response=response)

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
        db = load_db()
        db["users"].append({"username": username, "password": password})
        save_db(db)

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

if __name__ == '__main__':
    app.run(debug=True)
