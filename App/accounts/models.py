from datetime import datetime

import pyotp
from flask_login import UserMixin

from App import bcrypt, db
from config import Config

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    emailaddress = db.Column(db.String, nullable=False) # email
    password = db.Column(db.String, nullable=False)
    device_saved =  db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    is_two_factor_authentication_enabled = db.Column(
        db.Boolean, nullable=False, default=False)
    two_factor_secret = db.Column(db.String(32))
    secret_token = db.Column(db.String, unique=True)

    def __init__(self, username, emailaddress, password):
        self.username = username
        self.emailaddress = emailaddress # email
        self.password = bcrypt.generate_password_hash(password)
        self.device_saved = "None"
        self.created_at = datetime.now()
        self.secret_token = pyotp.random_base32()

    def get_authentication_setup_uri(self):
        return pyotp.totp.TOTP(self.secret_token).provisioning_uri(
            name=self.username, issuer_name=Config.APP_NAME)

    def is_otp_valid(self, user_otp):
        totp = pyotp.parse_uri(self.get_authentication_setup_uri())
        return totp.verify(user_otp)

    def __repr__(self):
        return f"<user {self.username} email {self.emailaddress}>" # email
