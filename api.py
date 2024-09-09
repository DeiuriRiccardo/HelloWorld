from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import random
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/db_name'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Funzione per caricare le citazioni da un file JSON
def load_quotes():
    with open('data.json', 'r') as f:
        return json.load(f)

quotes = load_quotes()

# Endpoint per ottenere una citazione casuale
@app.route('/random-text', methods=['GET'])
def get_random_quote():
    category = request.args.get('category')
    
    if category and category in quotes:
        # Se è stata specificata una categoria valida, scegli una citazione da quella categoria
        selected_quote = random.choice(quotes[category])
    else:
        # Se nessuna categoria specificata, scegli una citazione da tutte le categorie
        all_quotes = [quote for category_quotes in quotes.values() for quote in category_quotes]
        selected_quote = random.choice(all_quotes)
    
    return jsonify({"quote": selected_quote})

if __name__ == '__main__':
    app.run(debug=True)