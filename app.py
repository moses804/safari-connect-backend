from flask import Flask
from flask_migrate import Migrate
from models import db

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tickets.db"
app.config["SQLALCHEMY_ECHO"] = True  # Enable query logging

# Initialize migrations
migrate = Migrate(app, db)

# Link database to Flask app
db.init_app(app)