import os


class Config:
    SECRET_KEY = 'lhvurvrq3si7tftl45479m8va5h15n2e'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///images.db'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'growthIndiaDb@gmail.com'
    MAIL_PASSWORD = 'growth20190426'

