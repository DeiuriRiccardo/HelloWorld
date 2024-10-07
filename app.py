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
    # url = 'https://www.quodb.com/search/r?advance-search=false&keywords=r'
    url = "https://api.quodb.com/search/example?advance-search=false&keywords=example&titles_per_page=50&phrases_per_title=1&page=1"
    response = requests.get(url)
    if response.status_code == 200:
        films = response.json()['docs']

        film = random.choice(films)
        categories = db.session.execute(db.select(Category)).scalars()
        return render_template('text.html', title=film['title'], phrase=film['phrase'], year=film['year'], categories=categories)
    else :
        flash("There was an error, try to verify research parameters and reload.")
        return redirect(url_for('get_random_quote'))

@app.route('/random-text', methods=['POST'])
def get_random_quote_post():
    category = request.form.get('category')
    year = str(request.form.get('year'))
    search_text = request.form.get('search')
    seeAll = request.form.getlist('cb')
    if(search_text == '') :
        flash("you must enter a search text")
        return redirect(url_for('get_random_quote'))
    if not db.session.execute(db.select(Category).filter_by(name=category)).scalars().first() and "CATEGORY" != category:
        flash("you must enter a valid category")
        return redirect(url_for('get_random_quote'))
    url = f"https://api.quodb.com/search/{search_text}?advance-search=true&keywords={search_text}&titles_per_page=50&phrases_per_title=1&page=1{'&genres=' + category if category != 'CATEGORY' else ''}{'&year=' + year if year != '' else ''}"
    response = requests.get(url)
    if response.status_code == 200:
        films = response.json()['docs']
        if len(films) == 0 :
            flash("There aren't film.")
            return redirect(url_for('get_random_quote'))
        categories = db.session.execute(db.select(Category)).scalars()
        if(not(seeAll)):
            film = random.choice(films)
            return render_template('text.html', title=film['title'], phrase=film['phrase'], year=film['year'], categories=categories)
        else:
            return render_template('text.html', films=films, seeAll=seeAll, categories=categories)
    else :
        flash("There was an error, try to verify research parameters and reload.")
        return redirect(url_for('get_random_quote'))

def init_db():  #nuovo stile
    # Verifica se i ruoli esistono già
    if not db.session.execute(db.select(Role).filter_by(name='admin')).scalars().first():
        admin_role = Role(name='admin')
        db.session.add(admin_role)
        db.session.commit()

    if not db.session.execute(db.select(Role).filter_by(name='user')).scalars().first():
        user_role = Role(name='user')
        db.session.add(user_role)
        db.session.commit()

    # Verifica se l'utente admin esiste già
    if not db.session.execute(db.select(User).filter_by(username='admin')).scalars().first():
        admin_user = User(username="admin", email="admin@example.com")
        admin_user.set_password("adminpassword")
        
        # Aggiunge il ruolo 'admin' all'utente
        admin_role = db.session.execute(db.select(Role).filter_by(name='admin')).scalars().first()
        admin_user.roles.append(admin_role)

        db.session.add(admin_user)
        db.session.commit()

    categories=["Action",
        "Sci-Fi",
        "Thriller",
        "Mystery",
        "Adventure",
        "Animation",
        "Drama",
        "Crime",
        "Fantasy",
        "Comedy",
        "Family",
        "Romance",
        "Horror",
        "Biography",
        "Music",
        "Sport",
        "Documentary",
        "War",
        "History",
        "Musical",
        "Short",
        "Western",
        "Film-Noir",
        "Reality-TV",
        "Adult",
        "Game-Show",
        "News",
        "Talk-Show"]

    for category in categories :
        # Verifica se la categoria esiste esiste già
        if not db.session.execute(db.select(Category).filter_by(name=category)).scalars().first():
            new_category = Category(name=category)

            db.session.add(new_category)
            db.session.commit()

if __name__ == '__main__':
    #inizializzare 
    with app.app_context():
        init_db()
    app.run(debug=True)