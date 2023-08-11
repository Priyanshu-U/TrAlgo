from datetime import date
from sqlalchemy.orm import defaultload, query
from . import db
from flask_login import UserMixin
from sqlalchemy import func
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True)
    cards = db.relationship('Card', backref='author', lazy='dynamic')
    bio=db.relationship('Bio',backref='author',lazy='dynamic')
    def __repr__(self):
        return '<User %r>' % self.username

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_in=db.Column(db.String(64))
    date = db.Column(db.String(64))
    res=db.Column(db.Integer,default=-1)
    type=db.Column(db.String(64), default='None')
    time=db.Column(db.String(64), default='None')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Bio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data=db.Column(db.String(140),default='None')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Pred(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date=db.Column(db.String(25))
    data=db.Column(db.String(20),default='None') 
    