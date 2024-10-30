from flask_login import UserMixin
from models.conn import db
from flask_bcrypt import Bcrypt
# from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select
from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user


bcrypt = Bcrypt()

user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  # Campo per la password criptata

    api_keys = db.relationship('ApiKey', backref='user', lazy='dynamic')

    def set_api_key(self, key_value):
        """Imposta una chiave API personalizzata."""
        new_key = ApiKey(user=self, value=key_value)
        db.session.add(new_key)
        db.session.commit()

    def get_api_keys(self):
        """Restituisce le chiavi API personalizzate dell'utente."""
        return self.api_keys


    # Relazione many-to-many tra User e Role
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        """Imposta la password criptata."""
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        """Verifica se la password è corretta."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def find_user_by_username(username):
        stmt = db.select(User).filter_by(username=username)
        user = db.session.execute(stmt).scalar_one_or_none()
        return user
    
    def update_user_email(username, new_email):
        stmt = db.select(User).filter_by(username=username)
        user = db.session.execute(stmt).scalar_one_or_none()
        if user:
            user.email = new_email
            db.session.commit()
            return f"Email aggiornata per {user.username}"
        else:
            return "Utente non trovato."
        
    def delete_user_by_username(username):
        stmt = db.select(User).filter_by(username=username)
        user = db.session.execute(stmt).scalar_one_or_none()
        if user:
            db.session.delete(user)
            db.session.commit()
            return f"Utente {username} eliminato."
        else:
            return "Utente non trovato."
        
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def __repr__(self):
        return f'<User {self.username}>'
    
class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    value = db.Column(db.String(80), unique=True, nullable=False)

def user_has_role(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Devi essere autenticato per accedere a questa pagina.")
                return redirect(url_for('login'))
            if not current_user.has_role(role_name):
                flash("Non hai il permesso per accedere a questa pagina.")
                return abort(403)  # Restituisce un errore 403 Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), unique=True)
    author = db.Column(db.String(50))
    year = db.Column(db.Date)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    def __repr__(self):
        return f'<Texts {self.content}>'
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    quotes = db.relationship('Quote', backref='category', lazy=True)

    def findIdByName(name):
        stmt = db.select(Category).filter_by(name=name)
        category = db.session.execute(stmt).scalar_one_or_none()
        return category

    def __repr__(self):
        return f'<Categories {self.name}>'