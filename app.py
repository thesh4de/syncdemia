from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session
#from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FieldList, SelectField
from wtforms.validators import InputRequired
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import datetime
import json
import sign
import datab
import attendance
import gcal


app = Flask(__name__)
SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRET = 'secret/credentials.json'
app.secret_key = "secret69basedgamer"
#app.config["SESSION_PERMANENT"] = False
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cookies.db"
app.config["SESSION_TYPE"] = "filesystem"
#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
MONTHS = [(1, "January"), (2, "February"), (3, "March"), (4, "April"), (5, "May"), (6, "June"), (7, "July"), (8, "August"), (9, "September"), (10, "October"), (11, "November"), (12, "December")]


#db = SQLAlchemy(app)
#app.config['SESSION_SQLALCHEMY'] = db
Session(app)


class loginform(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])


class meet(FlaskForm):
    link = FieldList(StringField('Link'))
    months = SelectField(u'Enter Month')


@app.route('/')
def home():
    if session.get('token'):
        return render_template('index.html', log=1)
    else:
        return render_template('index.html', log=0)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('token'):
        return redirect(url_for('home'))
    error = None
    lform = loginform()
    if lform.validate_on_submit():
        response = sign.getoken(lform.username.data, lform.password.data)
        if response["status"] == "error":
            error = response["msg"]
        else:
            session['token'] = response['token']
            return redirect(url_for('home'))
    return render_template('login.html', error=error, form=lform)


@app.route("/logout", methods=['GET'])
def logout():
    session.clear()
    attendance.clear_tt()
    return redirect(url_for('home'))


@app.route("/details", methods=['GET'])
def details():
    if not session.get('token'):
        return redirect(url_for('login'))
    else:
        personal = attendance.get_personal_and_tt(
            session.get('token'), "personal")
        if personal == "error":
            session.clear()
            return redirect(url_for('login'))
        slots = datab.getslots(attendance.get_batch_no(session.get('token')))
        if not slots["isholiday"]:
            time_table = attendance.get_personal_and_tt(
                session.get('token'), "tt")
            periods_for_slots = gcal.get_periods_for_slots(
                time_table, slots["slots"])
            return render_template('details.html', time=datab.gethead(), periods=periods_for_slots, perlist=personal, do=datab.getdo(), isholiday=slots["isholiday"])
        else:
            return render_template('details.html', perlist=personal, isholiday=slots["isholiday"])


@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(CLIENT_SECRET, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    auth_url, state = flow.authorization_url(
        access_type='offline', 
        include_granted_scopes='true', prompt='consent'
        )
    session['state'] = state
    return redirect(auth_url)


@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    auth_response = request.url
    flow.fetch_token(authorization_response=auth_response)
    creds = flow.credentials
    session['gtoken'] = json.loads(creds.to_json())
    return redirect(url_for('sync'))


@app.route("/sync", methods=['GET', 'POST'])
def sync():
    if not session.get('token'):
        return redirect(url_for('login'))

    gtoken = session.get('gtoken')
    if gtoken:
        gtoken = Credentials.from_authorized_user_info(session.get('gtoken'))
    if not gtoken or not gtoken.valid:
        if gtoken and gtoken.expired and gtoken.refresh_token:
            gtoken.refresh(Request())
            session['gtoken'] = json.loads(gtoken.to_json())
        else:
            return redirect(url_for('authorize'))

    links = meet()
    time_table = attendance.get_personal_and_tt(session.get('token'), "tt")
    date = datetime.datetime.now()
    month_no = int(date.strftime("%m"))
    links.months.choices = MONTHS[month_no - MONTHS[0][0]:]
    gcalendar = None
    if links.validate_on_submit():
        for n, (key, _) in enumerate(time_table.items()):
            time_table[key].append(links.link[n].data)
        batch_no = attendance.get_batch_no(session.get('token'))
        gcalendar = gcal.calsync(batch_no, time_table, gtoken, int(
            links.months.data) - month_no + 1)
    return render_template('sync.html', tt=time_table, links=links, msg=gcalendar)


if __name__ == "__main__":
    app.run(debug=True)
