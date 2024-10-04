from flask import Flask, jsonify, request, render_template
import random, json
from flask_login import LoginManager, login_required
from flask_migrate import Migrate
from models.model import db
from models.model import *
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from routes.auth import auth as bp_auth
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
load_dotenv()

app = Flask(__name__)

app.register_blueprint(bp_auth, url_prefix='/auth')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
#app.config['SECRET_KEY'] = 'dksjdlkajlkdj jfdsns'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask_hello_admin:Admin$00@localhost/flask_hello'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)

class ProtectedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))

# Creare un oggetto Admin con la tabella User come modello di dati
admin = Admin(app, name='Admin dashboard', template_mode='bootstrap4')
admin.add_view(ProtectedModelView(User, db.session))

#inizializzare 
with app.app_context():
    init_db()

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
    # category = request.args.get('category')
    
    # if category:
    #     # Se è stata specificata una categoria valida, scegli una citazione da quella categoria
    #     quotes_in_category = Quote.query.filter_by(category=category).all()
        
    #     if quotes_in_category:
    #         selected_quote = random.choice(quotes_in_category).content
    #     else:
    #         return "Categoria non trovata", 404
    # else:
    #     # Se nessuna categoria specificata, scegli una citazione da tutte le categorie
    #     all_quotes = Quote.query.all()
    #     selected_quote = random.choice(all_quotes).content
    
    # url = 'https://www.quodb.com/search/r?advance-search=false&keywords=r'
    url = "https://api.quodb.com/search/r?advance-search=false&keywords=r&titles_per_page=10&phrases_per_title=1&page=1"

    response = requests.get(url)
    if response.status_code == 200:
        films = response.json()['docs']

        film = random.choice(films)

        # soup = BeautifulSoup(html_content, 'html.parser')
        # quotes = soup.find_all('a', class_='phrase')
        return render_template('text.html', title=film['title'], phrase=film['phrase'], year=film['year'])
    else :
        "Errore"

@app.route('/addQuote')
@login_required
@user_has_role('admin')
def addQuote():
    categories = Category.query.all()
    return render_template('addText.html', categories=categories)

@app.route('/addQuote', methods=['POST'])
@login_required
@user_has_role('admin')
def addQuote_post():
    values = request.form
    text = values['text']
    category = values['category']
    author = values['author']
    category_id = Category.findIdByName(category)
    phrase = Quote(content=text, author=author, category_id=category_id)
    db.session.add(phrase)
    db.session.commit()
    flash('Quote added with success.')
    return redirect(url_for('addQuote'))

if __name__ == '__main__':
    app.run(debug=True)