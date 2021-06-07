import settings
import requests
from flask import Flask, render_template, abort

app = Flask(__name__)


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
