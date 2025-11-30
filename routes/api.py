import os
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.connection import db
from models.model import ImageFile, ColorStat
from PIL import Image
from routes.color_tools import analyze_image_colors


api = Blueprint("api", __name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@api.route("/palette", methods=["POST"])
@login_required
def palette_from_upload():
    if "image" not in request.files:
        return jsonify({"error": "file image mancante"}), 400

    f = request.files["image"]
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

    return jsonify({
        "image_id": image_row.id,
        "user_id": current_user.id,
        "colors": palette
    })
