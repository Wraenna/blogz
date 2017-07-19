from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from helpers import check_empty, check_length

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:almostdone@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B6978Lklkj34'

# Post model with id, title, body, and date/time published
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Setting the pub_date to None lets us make posts
    # Without entering in the date and time
    # The initializer handles it for us by autopopulating
    # The datetime with the datetime in UTC format
    def __init__(self, title, body, owner, pub_date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

    # TODO - Move validation up here

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True)
    password = db.Column(db.String(32))
    user_posts = db.relationship('Post', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    # TODO - Can I put validation here?


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/logout")
def logout():
    del session['username']
    del session['id']
    return redirect("/blog")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    # If the user tries to sign up,
    if request.method == 'POST':
        # Pull in the variables from the form
        username = request.form['username']
        password = request.form['password']
        verifypw = request.form['verifypw']
        # Query the database for the user
        existing_user = User.query.filter_by(username=username).first()
        errors_on_page = False

        # If the username field is empty, flash the error
        # Move some of this up to the model
        if username == "" or password == "" or verifypw == "":
            flash("One or more fields is invalid.", "error")
            errors_on_page = True
            # If the username isn't 3-20 characters, flash the error
        if check_length(username):
            flash("Your username should be between 3 and 20 characters.", "error")
            errors_on_page = True
        # If the password isn't 3-20 characters, flash the error
        if check_length(password):
            flash("Your password should be between 3 and 20 characters.", "error")
            errors_on_page = True
        # If the password and verifypw don't match, flash the error
        if password != verifypw:
            flash("Your passwords don't match.", "error")
            errors_on_page = True
        #If the user already exists, flash the error.
        if existing_user:
            flash("You already exist! Please log in.", "error")
            errors_on_page = True

        if errors_on_page == True:
            return render_template("/signup.html", title="Sign Up", username=username)

        # If the user doesn't exist already and their
        # passwords match, instantiate the user as new_user,
        # stage it, and commit it to the database.
        # Make a new session using their username
        # and redirect them to "/newpost"
        if not existing_user and password == verifypw:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            session['id'] = new_user.id
            return redirect("/newpost")

    return render_template("/signup.html", title="Sign Up")


@app.route("/login", methods=['POST', 'GET'])
def login():
    # If the user submits a POST, i.e. tries to log in
    if request.method == 'POST':
        # Request the data from the form fields
        username = request.form['username']
        password = request.form['password']
        # Go try to find the user in the database
        user = User.query.filter_by(username=username).first()
        # If the username exists in the database and the password matches,
        # Make a new session using their username, flash the logged in,
        # and then redirect them to "/newpost"
        if user and user.password == password:
            session['username'] = username
            session['id'] = user.id
            flash("Logged in")
            return redirect('/newpost')

        elif user == None:
            flash("You don't exist or you may have mistyped your username.")

        elif user.password != password:
            flash("Your passwords don't match!")

        return render_template('login.html', title="Log In", username=username)

    return render_template('login.html', title="Log In")

@app.route("/", methods=['POST', 'GET'])
def index():
    # Query for all the users
    users = User.query.all()
    # Render the template to display all the users
    return render_template("index.html", title="Current users", users=users)


# Main route. This route renders the blog with all the entries.
@app.route("/blog", methods=['POST', 'GET'])
def blog():
    # First check to see if there are any query parameters
    blog_post_id = request.args.get('id')

    user_id = request.args.get('user')

    # If it finds the id query parameter, it renders only the post that matches the id
    if blog_post_id:
        # Pull in only the posts that match the blog_post_id
        # Which should be one since primary keys are unique
        posts = Post.query.filter_by(id=blog_post_id).all()
        # Render the template with the title as the post title
        return render_template("blog.html", title=posts[0].title, posts=posts)
    # If it finds the user query parameter, it renders only posts from that author
    if user_id:
        # Pull in only posts made by the user matching the user id
        posts = Post.query.filter_by(owner_id=user_id).order_by(Post.pub_date.desc()).all()
        # Render the template with the list of posts to iterate over
        if len(posts) == 0:
            return render_template("singleUser.html", title="No Posts Yet", posts=posts)
        else:
            return render_template("singleUser.html", title="{}'s Posts".format(posts[0].owner.username), posts=posts)

    # Query for all the posts.
    # Order them by pub_date in descending order (newest to oldest)
    posts = Post.query.order_by(Post.pub_date.desc()).all()

    # Render the template
    return render_template("blog.html", title="All Blog Posts", posts=posts)

# Newpost route. This route allows you to add a new post.
@app.route("/newpost", methods=['POST', 'GET'])
def new_post():
    post_owner = User.query.filter_by(username=session['username']).first()
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
        new_post = Post(post_title, post_body, post_owner)
        db.session.add(new_post)
        db.session.commit()

        # Redirect user to their new post
        return redirect("/blog?id=" + str(new_post.id))

    # If navigating to the page from a link, load the newpost template
    return render_template("newpost.html", title="New Post")

# Run the app
if __name__ == '__main__':
    app.run()
