from flask import Flask, request, render_template, make_response
import sqlite3

app = Flask(__name__)


@app.route('/', methods=['GET'])
def survey():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
