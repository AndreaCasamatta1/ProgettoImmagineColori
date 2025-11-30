from datetime import datetime
from flask_login import UserMixin
from models.connection import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    images = db.relationship(
        "ImageFile",
        backref="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ImageFile(db.Model):
    __tablename__ = "image_files"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    filename = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(500), nullable=False)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    colors = db.relationship(
        "ColorStat",
        backref="image",
        cascade="all, delete-orphan"
    )


class ColorStat(db.Model):
    __tablename__ = "color_stats"
    id = db.Column(db.Integer, primary_key=True)

    image_id = db.Column(db.Integer, db.ForeignKey("image_files.id"), nullable=False)

    r = db.Column(db.Integer, nullable=False)
    g = db.Column(db.Integer, nullable=False)
    b = db.Column(db.Integer, nullable=False)
    hex = db.Column(db.String(7), nullable=False)

    percent = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(80), nullable=True)

    def to_dict(self):
        return {
            "rgb": (self.r, self.g, self.b),
            "hex": self.hex,
            "percent": self.percent,
            "name": self.name,
            "rgb_name": f"RGB({self.r}, {self.g}, {self.b})"
        }


def init_db():
    db.create_all()

    if not db.session.execute(db.select(User).filter_by(username="admin")).scalars().first():
        admin_user = User(username="admin", email="admin@example.com")
        admin_user.set_password("adminpassword")
        db.session.add(admin_user)
        db.session.commit()
