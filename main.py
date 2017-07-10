from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:getitdone@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):
    # TODO - write user class

class Post(db.Model):
    # TODO - write post class

# TODO - add the following routes:
# "/" for the index - would be good to make a register or login page of it
# "/blog" which displays all the blog posts
# "/newpost" which allows the user to add a new posts

# TODO - add the following templates:
# "register.html" to register
# "login.html" to login
# "blog.html" after logged in to display all posts
# "newpost.html" to add a new post
