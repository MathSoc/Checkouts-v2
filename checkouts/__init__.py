from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

__author__ = 'Ford Peprah'

app = Flask('checkouts')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

import views
