from images_query_interface.models import Image
from images_query_interface.common_utils import form_attributes, date_in_ist2min_max_jd
import datetime
import pytz
import julian
import numpy as np
from matplotlib import path 


#takes request.form as input and returns a dictionary
#containing the query for example
# {'exposure': {'min': '100', 'max': '500'}, 'filter_used': 'i', 'date_observed': '2019-07-03', 'tar_name': 'Uscorpii'}
def request_form2dict_query(request_form):
    dict_query = {}

    for attribute in form_attributes['String Valued']:
        value = request_form[attribute]
        if value != '':
            dict_query[attribute] = value

    for attribute in form_attributes['Real Valued']:
        real_val_cond2query_dict(request_form, attribute, dict_query)

    ra = request_form['ra']
    dec = request_form['dec']
    ra_filled = (ra!='')
    dec_filled = (dec!='')
    if ra_filled!=dec_filled :
        return 'Enter both RA & DEC'
    if(ra_filled & dec_filled):
        ra = float(ra)
        dec = float(dec)
        dict_query['ra'] = ra
        dict_query['dec'] = dec

    return dict_query


def real_val_cond2query_dict(request_form, str_attribute, dict_query):
    attribute_min = request_form[str_attribute+'_min']
    attribute_max = request_form[str_attribute+'_max']
    if attribute_min!='' or attribute_max!='':
        dict_query[str_attribute] = {}
        if attribute_min!='':
            dict_query[str_attribute]['min'] = attribute_min
        if attribute_max!='':
            dict_query[str_attribute]['max'] = attribute_max


def dict_query2list_images(dict_query):
    conditions_list = []
    
    if 'tar_name' in dict_query.keys():
        conditions_list.append(Image.tar_name==dict_query['tar_name'])

    if 'filter_used' in dict_query.keys():
        conditions_list.append(Image.filter_used==dict_query['filter_used'])
    
    if 'date_observed' in dict_query.keys():
        jd_min,jd_max = date_in_ist2min_max_jd(dict_query['date_observed'])
        conditions_list.append(Image.jd>=jd_min)
        conditions_list.append(Image.jd<=jd_max)

    for attribute in form_attributes['Real Valued']:
        if attribute in dict_query.keys():
            if 'min' in (dict_query[attribute]).keys():
                conditions_list.append(eval('Image.'+attribute)>=dict_query[attribute]['min'])
            if 'max' in (dict_query[attribute]).keys():
                conditions_list.append(eval('Image.'+attribute)<=dict_query[attribute]['max'])
            
    if 'ra' in dict_query.keys():
        ra = dict_query['ra']
        dec = dict_query['dec']
        conditions_list.append(ra_dec_condition(ra, dec))
        list_images = Image.query.filter(*conditions_list).all()
        list_images = second_approx(list_images, ra, dec)

    else:
        list_images = Image.query.filter(*conditions_list).all()
    
    return list_images

def ra_dec_condition(ra, dec):
    #given an ra and dec return sql query
    image_diagnol = 1
    buffer = 0.1
    ra_min = ra-(image_diagnol/2 + buffer)/np.cos(np.deg2rad(dec))
    ra_max = ra+(image_diagnol/2 + buffer)/np.cos(np.deg2rad(dec))

    if ra_min<0.0:
        ra_condition = ((Image.tar_ra>=0.0) & (Image.tar_ra<=ra_max)) | ((Image.tar_ra>=360.0+ra_min) & (Image.tar_ra<=360.0))
    elif ra_max>360.0:
        ra_condition = ((Image.tar_ra>=0.0) & (Image.tar_ra<=-360.0+ra_max)) | ((Image.tar_ra>=ra_min) & (Image.tar_ra<=360))
    else :
        ra_condition = ((Image.tar_ra>=ra_min) & (Image.tar_ra<=ra_max))
    
    dec_min = dec-(image_diagnol/2 + buffer)
    dec_max = dec+(image_diagnol/2 + buffer)

    if dec_min<(-90.0):
        dec_condition = (Image.tar_dec<=dec_max)
    elif dec_max>(90.0):
        dec_condition = (Image.tar_dec>=dec_min)
    else :
        dec_condition = ((Image.tar_dec>=dec_min) & (Image.tar_dec<=dec_max))

    return ra_condition & dec_condition

#checks if ra dec in the polygon
def condition_bool_polgn(polygon, ra, dec):
    image_diagnol = 1
    buffer = 0.1

    ra_min = ra-(image_diagnol/2 + buffer)/np.cos(np.deg2rad(dec))
    ra_max = ra+(image_diagnol/2 + buffer)/np.cos(np.deg2rad(dec))
    
    
    if ra_min<0+(image_diagnol/2 + buffer) or ra_max>360-(image_diagnol/2 + buffer):
        polygon_rotated = np.zeros(polygon.shape)
        polygon_rotated[:,0] = (polygon[:,0]+180)%360
        polygon_rotated[:,1] = polygon[:,1]
        ra_rotated = (ra+180)%360
        p_rotated = path.Path(polygon_rotated)
        return p_rotated.contains_point([ra_rotated, dec])
        
    else:
        p = path.Path(polygon)
        return p.contains_point([ra, dec])


def second_approx(first_approx_list, ra, dec):

    second_approx_list = first_approx_list
    for image in first_approx_list:
        polygon_sky_points = np.array(eval(image.boundry_points))
        if not (condition_bool_polgn(polygon_sky_points, ra, dec)):
            second_approx_list.remove(image)
    return second_approx_list


