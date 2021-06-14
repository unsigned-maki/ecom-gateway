import os
import settings
import requests
import json
from flask import Flask, request, render_template, abort

app = Flask(__name__)
api_key = os.getenv("API_KEY")

BLACKLISTED_CHARACTERS = ["<", ">"]

def method_not_allowed():
    return json.dumps({"success": False, "code": 405, "message": "Method Not Allowed"})


def service_unavailable():
    return json.dumps({"success": False, "code": 503, "message": "Service Unavailable"})


def forbidden():
    return json.dumps({"success": False, "code": 403, "message": "Forbidden"})


def bad_request():
    return json.dumps({"success": False, "code": 400, "message": "Bad Request"})


def validate_product(form):
    for i in ["title", "description"]:
        for character in BLACKLISTED_CHARACTERS:
            if character in form[i]:
                return False

    if form["category"]:
        if not request.get("http://127.0.0.1:5001/category/{id_}").json()["success"]:
            return False

    for i in ["price", "stock"]:
        if form[i] < 0:
            return False

    if form["checkout"]:
        if form["checkout"] != "default" and form["checkout"] != "external":
            return False

    if form["type"]:
        if form["type"] != "physical" and form["type"] != "digital" and form["type"] != "udigital":
            return False

    return True


@app.route("/product/<id_>", methods=["GET", "PATCH", "DELETE"])
def category_handler_id(id_):
    try:
        if request.method == "GET":
            response = requests.get(f"http://127.0.0.1:5001/product/{id_}")
        elif request.method == "PATCH" or request.method == "DELETE":
            if not request.headers["API-Key"]:
                return forbidden()

            if request.headers["API-Key"] != api_key:
                return forbidden()

            if request.method == "PATCH":
                if not validate_product(request.form):
                    return bad_request()

                response = requests.patch(f"http://127.0.0.1:5001/product/{id_}")
            elif request.method == "DELETE":
                response = requests.delete(f"http://127.0.0.1:5001/product/{id_}")
        else:
            return method_not_allowed()

    except requests.exceptions.ConnectionError:
        return service_unavailable()

    if response.status_code == 200:
        return response.json()
    else:
        return service_unavailable()


@app.route("/")
def index():
    try:
        return render_template("index.html",
                               categories=requests.get(f"{settings.SERVICE_PRODUCTS}/category").json()["categories"])
    except requests.exceptions.ConnectionError:
        abort(503)


@app.route("/category/<id_>")
def category(id_):
    try:
        response = requests.get(f"{settings.SERVICE_PRODUCTS}/category/{id_}")

        if response["code"] != 200:
            abort(404)

        return render_template("index.html",
                               category=response["category"],
                               categories=requests.get(f"{settings.SERVICE_PRODUCTS}/category").json()["categories"])
    except requests.exceptions.ConnectionError:
        abort(503)


if __name__ == '__main__':
    app.run()
