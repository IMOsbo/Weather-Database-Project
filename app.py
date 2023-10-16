from flask import Flask, request, render_template
import mysql.connector

app = Flask(__name__)

conn = mysql.connector.connect(user='root', database='weather', password="1234")

# Code heavily inspired by this:
#     https://manojahi.medium.com/flask-html-template-with-mysql-2f3b9405d0e2
# Thank you!!
@app.route("/")
def home():
    return render_template("query.html")

@app.route("/query_elevation", methods=["POST"])
def showElevation():
    cursor = conn.cursor()
    elevation = request.form["elevation"]
    cursor.execute(f"select id, `Elevation [m]` from coopmetadata where `Elevation [m]` > {elevation} order by `Elevation [m]`")
    return render_template("queryResult.html", results = cursor)

if __name__ == "__main__":
    app.run(debug=True)

