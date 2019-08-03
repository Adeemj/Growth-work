import datetime
import pytz
import julian
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import numpy as np
from collections import OrderedDict 




dict_attributes = OrderedDict()
dict_attributes['date_observed'] = 'Date Observed'
dict_attributes['jd'] = 'JD'

dict_attributes['filter_used'] = 'Filter'
dict_attributes['exposure'] = 'Exposure'
dict_attributes['air_mass'] = 'Air Mass'
dict_attributes['ccd_temp'] = 'CCD Temp'
dict_attributes['image_type'] = 'Image Type'
dict_attributes['focus_value'] = 'Focus Value'
dict_attributes['fwhm'] = 'FWHM'
dict_attributes['lim_mag'] = 'Lim Mag'

dict_attributes['psf_mag'] = 'PSF Mag'
dict_attributes['psf_merr'] = 'PSF Error'
dict_attributes['apr_mag'] = 'Apr Mag'
dict_attributes['apr_merr'] = 'Apr Error'

dict_attributes['tel_alt'] = 'Tel Alt'
dict_attributes['tel_az'] = 'Tel Az'
dict_attributes['ref_ra'] = 'Ref RA'
dict_attributes['ref_dec'] = 'Ref DEC'

dict_attributes['tar_ra'] = 'Tar RA'
dict_attributes['tar_dec'] = 'Tar DEC'
dict_attributes['tar_name'] = 'Target'



real_valued_attributes = ['jd', 'exposure', 'air_mass', 'ccd_temp']
string_valued_attributes = ['tar_name','date_observed', 'filter_used']
form_attributes = { 'String Valued' : string_valued_attributes, 'Real Valued' : real_valued_attributes }


def date_in_ist2min_max_jd(date_observed):
    # given a date observed give the max_jd and min jd corresponding to it
    date_time_object_ist = datetime.datetime.strptime(date_observed,"%Y-%m-%d")
    date_time_object_ist = date_time_object_ist.replace(tzinfo=pytz.timezone('Asia/Calcutta'))
    date_time_object_ist_noon = date_time_object_ist.replace(hour=12, minute=00)
    date_time_object_utc = date_time_object_ist_noon.astimezone(pytz.timezone('UTC'))
    min_jd = julian.to_jd(date_time_object_utc, fmt = 'jd')
    max_jd = min_jd+1
    return min_jd,max_jd

def list_images2list_filepaths(list_images):
    list_filepaths = []
    for image in list_images:
        list_filepaths.append(image.filepath)
    return list_filepaths

def rect2polygon(x_end,y_end,n_of_div):
    n = n_of_div
    corners = np.array([[0,0],[x_end,0],[x_end,y_end],[0,y_end]])
    output = np.zeros((4*n,2))
    for i in range(4):
        x_points = np.linspace(corners[i][0], corners[(i+1)%4][0], n+1)[:-1]
        y_points = np.linspace(corners[i][1], corners[(i+1)%4][1], n+1)[:-1]
        output[i*n:(i+1)*n] = np.concatenate((x_points.reshape((n,1)) ,y_points.reshape((n,1))) ,axis=1)
    return output

def boundry_points(x_end, y_end, wcs, n_of_div):
    polygon_pixel_points = rect2polygon(x_end, y_end, n_of_div)
    sky_coords = SkyCoord.from_pixel(polygon_pixel_points[:,0], polygon_pixel_points[:,1], wcs)
    ra = np.array(sky_coords.ra.value)
    dec = np.array(sky_coords.dec.value)
    l = 4*n_of_div
    coords = (np.concatenate((ra.reshape((l,1)) ,dec.reshape((l,1))) ,axis=1) ).tolist()
    return(str(coords))