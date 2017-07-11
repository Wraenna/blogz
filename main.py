from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

# TODO - add the following routes:
# "/newpost" which allows the user to add a new posts - should redirect to "/"

@app.route("/blog", methods=['POST', 'GET'])
def index():

    posts = Post.query.all()

    return render_template("blog.html", title="My Blog", posts=posts)

@app.route("/newpost", methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':
        post_title = request.form['title']
        post_body = request.form['body']
        new_post = Post(post_title, post_body)
        db.session.add(new_post)
        db.session.commit()
        return redirect("/blog")

    return render_template("newpost.html", title="New Post")

if __name__ == '__main__':
    app.run()
