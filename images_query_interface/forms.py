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


form = QueryForm()

for key,value in dict_for_checkboxes.items():
    setattr(form,key,BooleanField(value))
