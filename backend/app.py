from flask import Flask
from api.models import db
from constants import DATABASE_URL

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db.init_app(app)

# ... (rest of your Flask app setup)