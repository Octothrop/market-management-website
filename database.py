from sqlalchemy import create_engine, text
from flask import request, jsonify, render_template
import json, re, hashlib

db_string = "mysql+pymysql://6dodeptmo0rbxmzr2qms:pscale_pw_6UHZHXqyci9GtuVL38R7l7tJxmIcOihvuxtv9heGRVB@aws.connect.psdb.cloud/test_flask?charset=utf8mb4"

engine = create_engine(
    db_string,
    connect_args={
        "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"
        }
    }
)




def get_db():
  data1 = request.form
  req = data1.get('rp')
  z = hashlib.sha256(req.encode('utf-8')).hexdigest()
  with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM User WHERE username = :user and password_hash = :ps and user_role = :ur"),
        user=data1.get('ru'),
        ps=z,
        ur=data1.get('ur')
    )
  if result.fetchall() == []:
      return False
  else:
      return True
 

def insert_db():
    data = request.form
    password = data.get('rp')

    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    with engine.connect() as conn:
      conn.execute(text("INSERT INTO User (first_name, last_name, username, password_hash, phone_number, user_role) "
               "VALUES (:fn, :ln, :ru, :rp, :ph, :ur)"),
          fn=data.get('fn'),
          ln=data.get('ln'),
          ru=data.get('ru'),
          rp=hashed_password,
          ph=data.get('ph'),
          ur=data.get('ur')
      );



