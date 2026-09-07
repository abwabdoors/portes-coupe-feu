from flask import Flask, render_template, request, redirect, session
import json
import os
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

app.secret_key = "CHANGE_THIS_TO_A_RANDOM_SECRET"

ADMIN_CODE = "aZ@z_rI\-/ab#JT31781"

IMAGE_FOLDER = "static/images"

cloudinary.config(secure=True)


@app.route("/")
def accueil():
    with open("data.json", "r", encoding="utf-8") as file:
        doors = json.load(file)

    return render_template("index.html", doors=doors)


@app.route("/admin", methods=["GET", "POST"])
def admin():

    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as file:
            doors = json.load(file)
    else:
        doors = []

    if request.method == "POST":

        code = request.form["code"]
        price = request.form["price"]
        door_type = request.form["type"]
        features = request.form["features"]

        image_file = request.files["image"]

        # رفع الصورة إلى Cloudinary
        upload_result = cloudinary.uploader.upload(image_file)

        image_url = upload_result["secure_url"]
        image_public_id = upload_result["public_id"]

        door = {
            "code": code,
            "price": price,
            "type": door_type,
            "features": features,
            "image": image_url,
            "public_id": image_public_id
        }

        doors.append(door)

        with open("data.json", "w", encoding="utf-8") as file:
            json.dump(
                doors,
                file,
                ensure_ascii=False,
                indent=4
            )

        return redirect("/admin")

    return render_template("admin.html", doors=doors)


@app.route("/delete/<code>", methods=["POST"])
def delete_door(code):

    with open("data.json", "r", encoding="utf-8") as file:
        doors = json.load(file)

    door_to_delete = None

    for door in doors:
        if door["code"] == code:
            door_to_delete = door
            break

    if door_to_delete:

        doors.remove(door_to_delete)

        # حذف الصورة من Cloudinary
        public_id = door_to_delete.get("public_id")

        if public_id:
            cloudinary.uploader.destroy(public_id)

        with open("data.json", "w", encoding="utf-8") as file:
            json.dump(
                doors,
                file,
                ensure_ascii=False,
                indent=4
            )

    return redirect("/admin")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        code = request.form["code"]

        if code == ADMIN_CODE:
            session["admin_logged_in"] = True
            return redirect("/admin")

        else:
            return render_template(
                "login.html",
                error="❌ الرقم السري غير صحيح"
            )

    return render_template("login.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
