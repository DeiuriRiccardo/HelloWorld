from flask import Flask, jsonify, request
import random, json
from flask_login import LoginManager
from flask_migrate import Migrate
from models.model import db
from models.model import *
from routes.auth import auth as bp_auth

app = Flask(__name__)

app.register_blueprint(bp_auth, url_prefix='/auth')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask_hello_admin:Admin$00@localhost/flask_hello'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)

# Funzione per caricare le citazioni da un file JSON
def load_quotes():
    with open('data.json', 'r') as f:
        return json.load(f)

quotes = load_quotes()

# flask_login user loader block
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.execute(stmt).scalar_one_or_none()    
    return user

@app.route('/testuser/')
def test():
    # Creazione di un nuovo utente con una password criptata
    user = User(username='testuser', email='test@example.com')
    user.set_password('mysecretpassword')

    # Aggiunta dell'utente al database
    db.session.add(user)
    db.session.commit()

    # Verifica della password
    if user.check_password('mysecretpassword'):
        return "Password corretta!"
    else:
        return "Password errata!"

@app.route('/createuser', methods=['POST'])
def create_user():
    values = request.json
    username = values['username'] # in caso di form possiamo usare request.form
    email = values['email']
    password = values['password']
    user = User(username=username, email=email)
    user.set_password(password)  # Imposta la password criptata
    db.session.add(user)  # equivalente a INSERT
    db.session.commit()
    return f"Utente {username} creato con successo."

@app.route('/updateuser', methods=['POST'])
def update_user():
    values = request.json
    username = values['username']
    new_email = values['email']
    User.update_user_email(username, new_email)
    return f'Utente {username} modificato con successo'

@app.route('/deleteuser', methods=['POST'])
def delete_user():
    values = request.json
    username = values['username']
    User.delete_user_by_username(username)
    return f'Utente {username} eliminato con successo'

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