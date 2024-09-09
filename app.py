from flask import Flask
from flask import render_template
from flask import request, jsonify
from flask import Blueprint, Flask
import random

app = Flask(__name__)

@app.route('/')
def default():
    return "Ciao, questa è la root"

@app.route('/hello/<name>')
def hello(name):
    return render_template('hello.html', name=name)

@app.route('/power/<int:value>')
def power(value):
    return f'Power: {value*value}'

@app.route('/sum/', methods=["POST"])
def sum():
    values = request.json
    v1 = values['v1']
    v2 = values['v2']
    return f'{v1 + v2}'


randomtext = Blueprint('random-text', __name__)

@randomtext.route('/')
def home():
    return render_template('hello.html', name='')

# @randomtext.route('/submit/', methods=['GET'])
# def submit_data():
#     form_data = request.form.get('data')

#     url = "https://www.frasicelebri.it/ricerca-frasi/?q=citazioni"

#     response = requests.get(url)

#     if response.status_code == 200:
#         citazioni = response.json()
#         # Estrai le informazioni principali
#         citazioni_info = {
#             'citazione': citazioni.get('name')
#         }
#         return jsonify(citazioni_info), 201
#     else:
#         # Se la richiesta non è andata a buon fine, restituisci un errore
#         return jsonify({'errore': 'Impossibile ottenere i dati'}), 500

@randomtext.route('/submit/<string:frase>', methods=['GET'])
def submit_data(frase):
    return frase

# Frasi di esempio
frasi = {
    "motivazionale": [
        "Non smettere mai di sognare.",
        "Il successo è la somma di piccoli sforzi."
    ],
    "citazioni": [
        "La vita è quello che succede mentre sei impegnato a fare altri piani.",
        "Il tempo è denaro."
    ],
    "canzoni": [
        "Let it be, let it be.",
        "We don't need no education."
    ]
}

@randomtext.route('/sub', methods=['GET'])
def random_text():
    category = request.args.get('category')
    
    if category and category in frasi:
        return jsonify({"text": random.choice(frasi[category])})
    else:
        all_frasi = sum(frasi.values(), [])
        return jsonify({"text": random.choice(all_frasi)})

app.register_blueprint(randomtext, url_prefix='/random-text')

if __name__ == '__main__':
    app.run(debug=True)