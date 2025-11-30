import os
from flask import Flask, send_from_directory
from flask_login import LoginManager
from flask_migrate import Migrate
from models.connection import db
from models.model import User, init_db
from routes.views import views
from routes.api import api
from routes.auth import auth

app = Flask(__name__)
app.config["SECRET_KEY"] = "dsbgfdbdvial"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/uploads/<path:filename>")
def uploaded_files(filename):
    return send_from_directory(UPLOAD_DIR, filename)

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(views)
app.register_blueprint(api, url_prefix="/api")

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
