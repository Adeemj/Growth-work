from flask import render_template, url_for, flash, redirect, request
from images_query_interface import app,db
# from images_query_interface.forms import QueryForm, dict_for_checkboxes
from images_query_interface.images_db import Image, add_to_db
import datetime
import julian
import pytz
import matplotlib.path as mpltPath
import numpy as np
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, DateTimeField, BooleanField
from wtforms.validators import DataRequired


class QueryForm(FlaskForm):

    mjd_min = DecimalField('Min MJD')
    mjd_max = DecimalField('Max MJD')
    date_observed = DateTimeField('Date Observed')
    ra = DecimalField('RA')
    dec = DecimalField('DEC')
    target_name = StringField('Target name')
    query = SubmitField('Query Targets')

dict_for_checkboxes = {'date_observed_check':'Date Observed', 'mjd':'MJD',
'filter_used':'Filter Used', 'exposure':'Exposure',
'air_mass':'Air Mass','ccd_temp':'CCD Temp',
'image_type': 'Image Type', 'focus_value':'Focus Value',
'file_path':'File Path', 'tel_alt':'Tel Alt', 'tel_az':'Tel Az',
'ref_ra':'Ref RA', 'ref_dec':'Ref DEC', 'tar_ra':'Tar RA','tar_dec':'Tar DEC',
'tar_name_check':'Target Name', 'boundry_points':'Boundry Points'}



list_attributes = ['date_observed', 'mjd', 'filter_used', 'exposure', 'air_mass', 'ccd_temp', 'image_type', 'focus_value',
    'file_path', 'tel_alt', 'tel_az', 'ref_ra', 'ref_dec', 'tar_ra', 'tar_dec', 'tar_name', 'boundry_points']


def date_in_ist2min_max_mjd(date_observed):
    date_time_object_ist = datetime.datetime.strptime(date_observed,"%Y-%m-%d")
    date_time_object_ist = date_time_object_ist.replace(tzinfo=pytz.timezone('Asia/Calcutta'))
    date_time_object_ist_noon = date_time_object_ist.replace(hour=12, minute=00)
    date_time_object_utc = date_time_object_ist_noon.astimezone(pytz.timezone('UTC'))
    min_mjd = julian.to_jd(date_time_object_utc, fmt = 'jd')
    max_mjd = min_mjd+1
    return min_mjd,max_mjd


@app.route("/query", methods=['GET'])
def query():
    global list_attributes, dict_for_checkboxes

    form = QueryForm()

    for key,value in dict_for_checkboxes.items():
        setattr(form,key,BooleanField(value))
    print(form.__dict__.keys())
    return render_template('request_query_db.html', form=form, dict_for_checkboxes=dict_for_checkboxes)


@app.route("/display", methods=['POST'])
def display():
    global list_attributes

    conditions_list = []

    target_name = request.form['target_name']
    if target_name!='':
        conditions_list.append(Image.tar_name==target_name)
    
    mjd_min = request.form['mjd_min']
    mjd_max = request.form['mjd_max']

    date_observed = request.form['date_observed']
    if date_observed!='':
        mjd_min,mjd_max = date_in_ist2min_max_mjd(date_observed)

    if mjd_max!='':
        conditions_list.append(Image.mjd>=mjd_min)
    if mjd_min!='':
        conditions_list.append(Image.mjd<=mjd_max)

    ra = request.form['ra']
    dec = request.form['dec']

    ra_filled = (ra!='')
    dec_filled = (dec!='')
    if(ra_filled!=dec_filled):
        return 'Enter both RA & DEC'

    if(ra_filled & dec_filled):
        ra = float(ra)
        dec = float(dec)

        image_diagnol = 1
        buffer = 0.1

        ra_min = ra-(image_diagnol/2 + buffer)/np.cos(np.deg2rad(dec))
        ra_max = ra+(image_diagnol/2 + buffer)/np.cos(np.deg2rad(dec))

        if ra_min<0.0:
            ra_condition = ((Image.ref_ra>=0.0) & (Image.ref_ra<=ra_max)) | ((Image.ref_ra>=360.0+ra_min) & (Image.ref_ra<=360.0))
        elif ra_max>360.0:
            ra_condition = ((Image.ref_ra>=0.0) & (Image.ref_ra<=-360.0+ra_max)) | ((Image.ref_ra>=ra_min) & (Image.ref_ra<=360))
        else :
            ra_condition = ((Image.ref_ra>=ra_min) & (Image.ref_ra<=ra_max))
        conditions_list.append(ra_condition)

        dec_min = dec-(image_diagnol/2 + buffer)
        dec_max = dec+(image_diagnol/2 + buffer)

        if dec_min<(-90.0):
            dec_condition = (Image.ref_dec<=dec_max)
        elif dec_max>(90.0):
            dec_condition = (Image.ref_dec>=dec_min)
        else :
            dec_condition = ((Image.ref_dec>=dec_min) & (Image.ref_dec<=dec_max))
        conditions_list.append(dec_condition)

    # print(conditions_list)
    list_images = Image.query.filter(*conditions_list).all()




    # first_approximation = Image.query.filter_by().all()
    
    # for image in first_approximation:
    #     polygon = image.boundry_points['coordinates']
    #     path = mpltPath.Path(polygon)
    #     inside = path.contains_points(points)

    

    return render_template('display_result.html', list_images = list_images, list_attributes = list_attributes )
