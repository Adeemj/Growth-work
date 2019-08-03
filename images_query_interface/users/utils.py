from flask import current_app, url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Message
from images_query_interface import mail


def get_reset_token(username, email, hashed_password, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'username':username, 'email': email, 'password':hashed_password}).decode('utf-8')


def send_verification_email(username, email, hashed_password):
    token = get_reset_token(username, email, hashed_password, expires_sec=1800)
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients='99adeem@gmail.com')
    msg.body = ("To verify this account, visit the following link:{}").format(url_for('users.verify_token', token=token, _external=True))
    mail.send(msg)