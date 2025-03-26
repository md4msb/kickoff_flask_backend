from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Player Table
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    position = db.Column(db.String(50), nullable=False)
    strength = db.Column(db.Integer, nullable=False)

# Match History Table
class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    winner = db.Column(db.String(10), nullable=False)  # "team1" or "team2"
    team1 = db.Column(db.JSON, nullable=False)
    team2 = db.Column(db.JSON, nullable=False)
