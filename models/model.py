from models.conn import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  # Campo per la password criptata

    def set_password(self, password):
        """Imposta la password criptata."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se la password è corretta."""
        return check_password_hash(self.password_hash, password)

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

    def __repr__(self):
        return f'<User {self.username}>'