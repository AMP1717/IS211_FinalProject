from flask import Flask, render_template, request, redirect, url_for, session
import urllib
import json
import database

app = Flask(__name__)
app.secret_key = "my_super_secret_key"

logins = {
    "user" : "password"
}

db = database.Database()

books = [{"author": "author", "title": "Title"}, {"author": "second"}]

def add_message(name, msg):
    if "messages" not in session:
        session["messages"] = {}
    session["messages"][name] = msg
    session.modified = True
    print(session["messages"])

def parse_messages():
    if "messages" not in session:
        session["messages"] = {}
    
    messages = session["messages"]
    session["messages"] = {}
    return messages

@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html",
    books=db.get_books(),
    logged_in = session.get("logged_in"),
    **parse_messages()
    )

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        if username not in logins:
            session["logged_in"] = False
            return render_template("login.html", error=f"Username '{username}' is invalid.")
        
        if password != logins[username]:
            session["logged_in"] = False
            return render_template("login.html", error=f"Invalid password.")
        
        session["logged_in"] = True
        add_message("msg_success", "You were successfully logged in.")
        return redirect(url_for("index"))

    elif session.get("logged_in"):
        add_message("already_logged_in", "You are already logged in.")
        return render_template("login.html", **parse_messages()) 
    
    return render_template("login.html", **parse_messages()) 

@app.route("/add", methods=["POST"])
def add_book():
    if not session.get("logged_in"):
        add_message("error", "You must be logged in to add book.")
        return redirect(url_for("login"))
    
    isbn = request.form["isbn"]
    isbn_parsed = ""
    for char in isbn:
        if char in "0123456789":
            isbn_parsed += char

    isbn = isbn_parsed
    if not isbn_parsed:
        add_message("msg_error", f"Invalid ISBN.")
        return redirect(url_for("index"))

    data = urllib.request.urlopen(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}").read()

    try:
        data = json.loads(data)
    except:
        add_message("msg_error", f"Error parsing JSON file.")
        return redirect(url_for("index"))

    if data.get("totalItems") == 0:
        add_message("msg_error", f"No book found with this ISBN.")
        return redirect(url_for("index"))

    info = data.get("items")[0].get("volumeInfo")
    selected_info = {
        "title": info.get("title"),
        "author": info.get("authors"),
        "pages": info.get("pageCount"),
        "rating": info.get("averageRating")
    }

    if not selected_info.get("author"):
        selected_info["author"] = "No author found."
    else:
        selected_info["author"] = ",".join(selected_info["author"])

    if not selected_info.get("rating"):
        selected_info["rating"] = "No ratings."
    else:
        selected_info["rating"] = str(selected_info["rating"])

    if not selected_info.get("pages"):
        selected_info["pages"] = "Not found."


    db.add_book(selected_info)

    add_message("msg_success", f"'{selected_info['title']}' added to your catalogue.")
    return redirect(url_for("index"))

@app.route('/delete/<id>')
def delete(id):
    if not session.get("logged_in"):
        add_message("error", "You must be logged in to delete book.")
        return redirect(url_for("login"))

    db.delete_book(id)
    add_message("msg_success", f"Book deleted from catalogue.")
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True)