from flask import (render_template, url_for, flash,
                redirect, request, send_file, Blueprint)
from flask_login import  login_required
from images_query_interface.common_utils import (dict_attributes,
                                list_images2list_filepaths, date_in_ist2min_max_jd)
from images_query_interface.nightly.utils import (date2dict_times, list_images2obs_start_end,
                list_images2dict_targets_time, list_filepaths2data, plt_altVSfwhm, marker, histogram_fwhm)
from images_query_interface.models import Image

nightly = Blueprint('nightly', __name__)

@nightly.route("/nightly_page", methods=['POST'])
@login_required
def nightly_page():

    date = request.form['date']

    jd_min,jd_max = date_in_ist2min_max_jd(date)
    list_images = Image.query.filter(Image.jd>=jd_min, Image.jd<=jd_max).all()
    list_filepaths = list_images2list_filepaths(list_images)
    str_list_filepaths = str(list_filepaths)
    str_list_filepaths = (str_list_filepaths).replace('/','*')
    
    dict_times = date2dict_times(date)
    total_observable_time = (dict_times['Twelve degree Morning Twilight ']['utc'] 
    - dict_times['Twelve degree Evening Twilight ']['utc']  ).total_seconds()
    
    obs_start_time, obs_end_time = list_images2obs_start_end(list_images)
    total_observed_time = (obs_end_time['utc']-obs_start_time['utc']).total_seconds()
    
    dict_targets, total_exposure = list_images2dict_targets_time(list_images)
    sc_obs_frac = total_observed_time/total_observable_time
    sc_duty_cycle = total_exposure/total_observable_time

    

    return render_template('nightly.html',title='Nightly Page', date=date, dict_times=dict_times,
    list_attributes=dict_attributes.keys(), dict_attributes=dict_attributes, 
    list_images=list_images,  str_list_filepaths=str_list_filepaths,
    obs_start_time=obs_start_time, obs_end_time=obs_end_time,
    sc_obs_frac=sc_obs_frac, sc_duty_cycle=sc_duty_cycle, dict_targets=dict_targets)
    
import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


@nightly.route('/plot_altVsfwhm.png/<string:str_list_filepaths>')
def plt_altVSfwhm_png(str_list_filepaths):
    str_list_filepaths =  str_list_filepaths.replace('*','/')
    list_filepaths = eval(str_list_filepaths)
    df = list_filepaths2data(list_filepaths)
    fig = plt_altVSfwhm(df, marker())
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


# @nightly.route('/histogram_fwhm.png/<string:str_list_filepaths>')
# def plt_altVSfwhm_png(str_list_filepaths):
#     str_list_filepaths =  str_list_filepaths.replace('*','/')
#     list_filepaths = eval(str_list_filepaths)
#     df = list_filepaths2data(list_filepaths)
#     fig = histogram_fwhm(df, marker())
#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     return Response(output.getvalue(), mimetype='image/png')
