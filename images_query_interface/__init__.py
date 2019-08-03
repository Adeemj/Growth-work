from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from images_query_interface.config import Config



db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from images_query_interface.users.routes import users
    from images_query_interface.images.routes import images
    from images_query_interface.nightly.routes import nightly
    from images_query_interface.main.routes import main
    app.register_blueprint(users)
    app.register_blueprint(images)
    app.register_blueprint(main)
    app.register_blueprint(nightly)

    return app
