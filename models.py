from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(100))
    data_type = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

