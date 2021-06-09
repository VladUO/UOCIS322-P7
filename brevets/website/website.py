import flask
from flask import Flask, request, render_template, redirect, url_for, flash, abort
from passlib.apps import custom_app_context as pwd_context
from urllib.parse import urlparse, urljoin
import requests
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user, UserMixin,
                         confirm_login, fresh_login_required)
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, validators
from passlib.hash import sha256_crypt as pwd_context

SECRET_KEY = 'SuperSecretSquirrel'
secretSalt = 'SomeSalt'

app = Flask(__name__)
app.secret_key = "SuperSecretKey"

app.config.from_object(__name__)

login_manager = LoginManager()

login_manager.session_protection = "strong"

login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."

login_manager.refresh_view = "login"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"


@login_manager.user_loader
def load_user(id):
    return User(id, flask.session.get("name"), flask.session.get("token"))


login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, id, name, token):
        self.id = id
        self.name = name
        self.token = token

class LoginForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
        message=u"A little too short or long for a username."),
        validators.InputRequired(u"Input is required.")])
    password = StringField('Password', [
        validators.Length(min=2, max=25,
        message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])    
    remember = BooleanField('Remember me')    

class RegisterForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
        message=u"A little too short or long for a username."),
        validators.InputRequired(u"Input is required.")])
    password = StringField('Password', [
        validators.Length(min=2, max=25,
        message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])    
   
def hash_password(password):
    return pwd_context.encrypt(password)

@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/secret")
@login_required
def secret():
    flash(f"Hello: {current_user.name}")
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit() and request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        app.logger.debug("USERNAME IN WEBSITE", username)
        app.logger.debug("PASSWORD IN WEBSITE", password)
        password = pwd_context.using(salt = secretSalt).encrypt(password)
        r = requests.get('http://restapi:5000/token/' + '?username=' +  username + '&password=' + password)
        response = r.json()
        app.logger.debug("RESPONSE FOR LOGIN", response)
        if r.status_code == 200:
            newUser = User(response["id"], username, response["token"])
            remember = request.form.get("remember", "false") == "true"
            flask.session["id"] = response["id"]
            flask.session["name"] = username
            flask.session["token"] = response["token"]
            if login_user(newUser, remember=remember):
                flash("Logged in!")
                flash("I'll remember you") if remember else None
                next = request.args.get("next")
                if not is_safe_url(next):
                    abort(400)
                return redirect(next or url_for('index'))
            else:
                flash("Sorry, but you could not log in.")
        else:
            flash(u"Invalid username.")
    return render_template("login.html", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit() and request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        app.logger.debug("USERNAME IN WEBSITE", username)
        app.logger.debug("PASSWORD IN WEBSITE", password)
       
        password = pwd_context.using(salt= secretSalt).encrypt(password)
        r = requests.post('http://restapi:5000/register/', {'username': username, 'password':  password})
        app.logger.debug("RESPONSE FROM API REGISTRATION", r)
        response = r.json()
        if r.status_code == 201:
            return response['message']
        else:
            return response['message']
    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))
    

@app.route('/listAll',  methods = ["POST"])
def listAll():
    # getting format and k values out
    format = request.form.get("format")
    k = request.form.get("k")
    
    # app.logger.debug(format); 
    # app.logger.debug(k); 

    # formatting and sending a request to the api.py using requests
    r = requests.get('http://restapi:5000/listAll' + "/" + format + "?top=" + k + "&token=" + current_user.token)
    return r.text

@app.route("/listOpenOnly",  methods = ["POST"])
def listOpenOnly():
    # getting format and k values out
    format = request.form.get("format")
    k = request.form.get("k")

    # app.logger.debug(format); 
    # app.logger.debug(k);

    # formatting and sending a request to the api.py using requests
    r = requests.get('http://restapi:5000/listOpenOnly' + "/" + format + "?top=" + k + "&token=" + current_user.token)
    return r.text

@app.route("/listCloseOnly",  methods = ["POST"])
def listCloseOnly():
    # getting format and k values out
    format = request.form.get("format")
    k = request.form.get("k")

    # app.logger.debug(format); 
    # app.logger.debug(k);

    # formatting and sending a request to the api.py using requests
    r = requests.get('http://restapi:5000/listCloseOnly' + "/" + format + "?top=" + k + "&token=" + current_user.token)    
    return r.text

def is_safe_url(target):
    """
    :source: https://github.com/fengsp/flask-snippets/blob/master/security/redirect_back.py
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc





if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
