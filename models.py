# from flask_sqlalchemy import SQLAlchemy
#
# from app import app
#
# db = SQLAlchemy()
#
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), unique=True, nullable=False)
#     password = db.Column(db.String(128), nullable=False)
#
#     def __repr__(self):
#         return f"User('{self.username}')"
#
# # Create the database tables
# with app.app_context():
#     db.create_all()