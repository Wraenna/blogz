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
        posts = Post.query.filter_by(id=blog_post_id).all()
        return render_template("blog.html", title="My Blog", posts=posts)
    # Query for all the posts.
    posts = Post.query.all()
    # Render the template
    return render_template("blog.html", title="My Blog", posts=posts)

# Newpost route. This route allows you to add a new post.
@app.route("/newpost", methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':
        post_title = request.form['post_title']
        post_body = request.form['post_body']
        # TODO - Add error messages if title or body is blank
        # Have these flash as appropriate
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

        # TODO - Once the commit is done, query the new post
        # Maybe do this by the post title? Or post body?
        # The odds of it being duplicate are low

        return redirect("/blog?id=" + str(new_post.id))

    return render_template("newpost.html", title="New Post")

if __name__ == '__main__':
    app.run()
