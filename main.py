from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

# Post model with id, title, and body
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date


# Index route redirects to /blog
@app.route("/")
def index():
    return redirect("/blog")

# Main route. This route renders the blog with all the entries.
@app.route("/blog", methods=['POST', 'GET'])
def blog():
    # First check to see if there are any query parameters
    blog_post_id = request.args.get('id')

    # If it finds a query parameter, it renders only the post that matches the id
    if blog_post_id:
        # Pull in only the posts that match the blog_post_id
        # Which should be one since primary keys are unique
        posts = Post.query.filter_by(id=blog_post_id).all()
        # Render the template with the title as the post title
        return render_template("blog.html", title=posts[0].title, posts=posts)

    # Query for all the posts.
    posts = Post.query.order_by(Post.pub_date.desc()).all()

    # Render the template
    return render_template("blog.html", title="My Blog", posts=posts)

# Newpost route. This route allows you to add a new post.
@app.route("/newpost", methods=['POST', 'GET'])
def new_post():
    # If making a new post on this page:
    if request.method == 'POST':
        # Get your title and body
        post_title = request.form['post_title']
        post_body = request.form['post_body']
        # If either title or body is blank, flash the appropriate message(s)
        if post_title == "" or post_body == "":
            if post_title == "":
                flash("Please enter a title.", "error")

            if post_body == "":
                flash("Please enter a body.", "error")

            return render_template("newpost.html", title="New Post", post_title=post_title, post_body=post_body)
        # If there are no errors, go ahead and make the post
        new_post = Post(post_title, post_body)
        db.session.add(new_post)
        db.session.commit()

        # Redirect user to their new post
        return redirect("/blog?id=" + str(new_post.id))

    # If navigating to the page from a link, load the newpost template
    return render_template("newpost.html", title="New Post")

# Run the app
if __name__ == '__main__':
    app.run()
