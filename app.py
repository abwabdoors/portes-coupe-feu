from flask import Flask, render_template, request, redirect, session
import os
import cloudinary
import cloudinary.uploader
from supabase import create_client

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "CHANGE_THIS_SECRET")

ADMIN_CODE = "aZ@z_rI\-/ab#JT31781"

# Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cloudinary
cloudinary.config(secure=True)


@app.route("/")
def accueil():
    print("SUPABASE TEST")
    result = supabase.table("doors").select("*").order("id").execute()

    doors = result.data

    return render_template("index.html", doors=doors)


@app.route("/admin", methods=["GET", "POST"])
def admin():

    result = supabase.table("doors").select("*").order("id").execute()

    doors = result.data

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

        supabase.table("doors").insert(door).execute()

        return redirect("/admin")

    return render_template("admin.html", doors=doors)


@app.route("/delete/<code>", methods=["POST"])
def delete_door(code):

    result = (
        supabase
        .table("doors")
        .select("*")
        .eq("code", code)
        .execute()
    )

    if result.data:

        door = result.data[0]

        # حذف الصورة من Cloudinary
        public_id = door.get("public_id")

        if public_id:
            cloudinary.uploader.destroy(public_id)

        # حذف الباب من Supabase
        supabase.table("doors").delete().eq("code", code).execute()

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
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
