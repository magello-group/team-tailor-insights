__author__ = 'jens.tinglev@magello.se'

import os
import datetime
import requests
import sqlite3
from flask import Flask, request, render_template
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from dateutil.relativedelta import relativedelta

# Pre-flight checks
if not os.environ.get("USER"):
    print("Missing USER env var for BasicAuth username.")
    exit()
if not os.environ.get("PASSWORD"):
    print("Missing PASSWORD env var BasicAuth usernames password.")
    exit()
if not os.environ.get("API_TOKEN"):
    print("Missing API_TOKEN env var, this is found in TeamTailor.")
    exit()

app = Flask(__name__)

# Set up basic auth
auth = HTTPBasicAuth()
users = {
    os.environ.get("USER"): generate_password_hash(os.environ.get("PASSWORD"))
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@app.route("/", methods=["GET"])
@auth.login_required
def get_index():
    data = get_data()
    return render_template('index.html', data=data)

def get_data():
    # Get month req param (if provided)
    since = datetime.datetime.now()
    if 'months' in request.args:
        months = int(request.args['months'])
        now = datetime.datetime.now()
        since = now - relativedelta(months=months)

    # Connect to DB
    connection = sqlite3.connect("teamtailor.db")
    cursor = connection.cursor()

    # Setup tables (if non-existant)
    create_tables(cursor)

    # Query data
    data = [
        {
            'Link': f'https://app.teamtailor.com/companies/KBWY-SMQuOQ/candidates/segment/all/candidate/{c[0]}',
            'CreatedAt': c[1],
            'Name': f'{c[2].strip()} {c[3].strip()}',
            'Email': "" if not c[4] else c[4],
            'Note': c[5],
            'User': c[6],
            'LinkedIn': "" if not c[7] else c[7]

        } for c in cursor.execute(
            "SELECT c.Id, DATE(n.CreatedAt), c.FirstName, c.LastName, c.Email, n.Note, u.Name, c.LinkedIn "
            "FROM Candidates AS c "
            "JOIN Notes as n ON n.CandidateId = c.Id "
            "JOIN Users as u ON n.UserId = u.Id "
            "GROUP BY c.Id "
            f"HAVING MAX(n.CreatedAt) < '{since}' "
            "ORDER BY n.CreatedAt DESC"
        )
    ]
    connection.close()

    if 'user' in request.args and request.args['user']:
        data = [d for d in data if d['User'] == request.args['user']]

    return data

@app.route("/reload", methods=["GET"])
@auth.login_required
def reload_data():
    # Set API headers
    headers = {
        'Authorization': f"Token token={os.environ.get('API_TOKEN')}",
        'X-Api-Version': '20210218'
    }
    
    # Connect to DB
    connection = sqlite3.connect("teamtailor.db")
    cursor = connection.cursor()

    # Setup tables (if non-existant)
    create_tables(cursor)
    
    # Clear data
    cursor.execute("DELETE FROM Notes")
    cursor.execute("DELETE FROM Candidates")

    # Users
    page_size = requests.utils.quote('page[size]=30')
    users = requests.get(
        f'https://api.teamtailor.com/v1/users?{page_size}',
        headers=headers,
        hooks={'response': request_hook}
    )
    users.raise_for_status()
    users_json = users.json()
    while ('links' in users_json and 
            'next' in users_json['links'] and 
            users_json['links']['next']):
        data = [
        (
            u['id'],
            u['attributes']['name'],
        ) for u in users_json['data']]
        cursor.executemany(
            "INSERT INTO Users (Id, Name) VALUES (?, ?)", 
            data
        )
        connection.commit()
        users = requests.get(
            users_json['links']['next'],
            headers=headers,
            hooks={'response': request_hook}
        )
        users_json = users.json()

    # Notes
    notes = requests.get(
        'https://api.teamtailor.com/v1/notes',
        headers=headers,
        hooks={'response': request_hook}
    )  

    data = [
        (
            n['data']['id'],
            n['data']['attributes']['created-at'],
            n['data']['attributes']['candidate-id'],
            n['data']['attributes']['note'],
            n['data']['attributes']['user-id']
        ) for n in notes.json()['notes']]
    cursor.executemany(
        "INSERT INTO Notes (Id, CreatedAt, CandidateId, Note, UserId) VALUES (?, ?, ?, ?, ?)", 
        data
    )
    connection.commit()

    # Candidates
    candidates = requests.get(
        f'https://api.teamtailor.com/v1/candidates?{page_size}',
        headers=headers,
        hooks={'response': request_hook}
    )

    # We need to do a pagination loop, because of a bug in team tailors api
    # that paginates the candidate endpoint, when it shouldn't
    candidates_json = candidates.json()
    while ('links' in candidates_json and 
            'next' in candidates_json['links'] and 
            candidates_json['links']['next']):
        data = [
        (
            c['id'],
            c['attributes']['first-name'],
            c['attributes']['last-name'],
            c['attributes']['email'],
            c['attributes']['linkedin-url'],
            
        ) for c in candidates_json['data']]
        cursor.executemany(
            "INSERT INTO Candidates (Id, FirstName, LastName, Email, LinkedIn) VALUES (?, ?, ?, ?, ?)", 
            data
        )
        connection.commit()
        candidates = requests.get(
            candidates_json['links']['next'],
            headers=headers,
            hooks={'response': request_hook}
        )
        candidates_json = candidates.json()

    connection.close()

    return "OK", 200

def request_hook(r, *args, **kwargs):
    print(f'Calling API at {r.url}')

def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Notes (
            Id INTEGER,
            CreatedAt DATETIME,
            CandidateId INTEGER,
            Note VARCHAR(100),
            UserId INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Candidates (
            Id INTEGER,
            FirstName VARCHAR(100),
            LastName VARCHAR(100),
            Email VARCHAR(100),
            LinkedIn VARCHAR(100)
        )
    """) 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            Id INTEGER,
            Name VARCHAR(100)
        )
    """) 
