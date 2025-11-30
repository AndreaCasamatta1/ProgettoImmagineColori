import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from PIL import Image
from models.connection import db
from models.model import ImageFile, ColorStat
from routes.color_tools import analyze_image_colors

app = Blueprint("default", __name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/")
@login_required
def home():
    images = (
        ImageFile.query
        .filter_by(user_id=current_user.id)
        .order_by(ImageFile.created_at.desc())
        .all()
    )
    return render_template("home.html", images=images)

@app.route("/upload")
@login_required
def upload_page():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
@login_required
def upload_post():
    if "image" not in request.files:
        flash("Nessun file selezionato")
        return redirect(url_for("default.upload_page"))

    f = request.files["image"]
    if f.filename == "":
        flash("Nome file non valido")
        return redirect(url_for("default.upload_page"))

    save_path = os.path.join(UPLOAD_DIR, f.filename)
    f.save(save_path)

    img = Image.open(save_path).convert("RGB")
    w, h = img.size

    image_row = ImageFile(
        user_id=current_user.id,
        filename=f.filename,
        path=save_path,
        width=w,
        height=h
    )
    db.session.add(image_row)
    db.session.commit()

    palette = analyze_image_colors(save_path, n_colors=15)

    for p in palette:
        r, g, b = p["rgb"]
        cs = ColorStat(
            image_id=image_row.id,
            r=r, g=g, b=b,
            hex=p["hex"],
            percent=p["percent"],
            name=p["name"]
        )
        db.session.add(cs)

    db.session.commit()

    flash("Immagine caricata e analizzata correttamente")
    return redirect(url_for("default.home"))
