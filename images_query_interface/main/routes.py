from flask import (render_template, url_for, flash,
                     request, Blueprint)
from images_query_interface.forms import NightDate

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    form = NightDate()
    return render_template('home.html', form=form, title='Home')

