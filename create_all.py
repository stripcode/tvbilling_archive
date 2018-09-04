from app import db
from app import app

db.init_app(app)
db.create_all(app = app)