from images_query_interface import db, bcrypt, login_manager
import os
from astropy.io import fits
from astropy.wcs import WCS
from images_query_interface.common_utils import boundry_points
import datetime
from dateutil.parser import parse
import numpy as np
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Image(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date_observed = db.Column(db.DateTime, unique=True, nullable=False)
    jd = db.Column(db.Float, unique=True, nullable=False)

    filter_used = db.Column(db.String(20))
    exposure = db.Column(db.Float)
    air_mass = db.Column(db.Float)
    ccd_temp = db.Column(db.Float)
    image_type = db.Column(db.String(20))  
    focus_value = db.Column(db.String(20))
    fwhm = db.Column(db.Float)
    lim_mag = db.Column(db.Float)
    psf_mag = db.Column(db.Float)
    psf_merr = db.Column(db.Float)
    apr_mag = db.Column(db.Float)
    apr_merr = db.Column(db.Float)

    filepath = db.Column(db.String(120), unique=True, nullable=False)

    tel_alt = db.Column(db.Float)
    tel_az = db.Column(db.Float)

    ref_ra =  db.Column(db.Float)
    ref_dec = db.Column(db.Float)

    tar_ra = db.Column(db.Float)
    tar_dec = db.Column(db.Float)
    tar_name = db.Column(db.String(20))

    boundry_points = db.Column(db.String(120))

    def __repr__(self):
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items())
    
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    history = db.Column(db.String(240))

    def __repr__(self):
        return ("User({self.username}, {self.email}").format()
 

def read_header(key,header_dict):
    try:
        return header_dict[key]
    except KeyError:
        return None


def remove_root(filepath):
    print(filepath)
    temp = filepath.replace('/mnt/growth/growth_data', '')
    temp = temp.replace('/home/growth', '')
    print(temp)
    return temp


def file_to_Image_obj(fits_image_filename):
    
    hdul = fits.open(fits_image_filename)
    hdr = hdul[0].header
    (y_end,x_end) = hdul[0].data.shape 
    hdul.close()
    wcs = WCS(hdr)
    
    n_of_div = 5

    this_image = Image(
    date_observed = parse(read_header('DATE-OBS',hdr)),
    jd = read_header('JD',hdr),

    filter_used = read_header('FILTER',hdr),
    exposure = read_header('EXPOSURE',hdr),
    air_mass = read_header('AIRMASS',hdr),
    ccd_temp = read_header('CCD_TEMP',hdr),
    image_type = read_header('IMAGETYP',hdr),
    focus_value = read_header('FOCUSER',hdr),
    fwhm = read_header('FWHM', hdr),
    lim_mag = read_header('LIM_MAG', hdr),

    psf_mag = read_header('PSF_mag', hdr),
    psf_merr = read_header('PSF_merr', hdr),
    apr_mag = read_header('Apr_mag', hdr),
    apr_merr = read_header('Apr_merr', hdr),

    filepath = (fits_image_filename) ,

    tel_alt = read_header('TEL_ALT',hdr),
    tel_az = read_header('TEL_AZ',hdr),

    ref_ra = read_header('CRVAL1',hdr),
    ref_dec = read_header('CRVAL2',hdr),

    tar_ra = read_header('TARRA',hdr),
    tar_dec = read_header('TARDEC',hdr),
    tar_name = read_header('OBJECT',hdr),

    boundry_points = boundry_points(x_end,y_end,wcs,n_of_div)
    )
    
    return this_image

def add_dir_to_db(dirpath, append):
    if not append:
        db.drop_all()
        db.create_all()
    
    for dirpath, dirnames, filenames in os.walk(dirpath):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if filepath.endswith('.proc.fits'):
                try :
                    this_image = file_to_Image_obj(filepath)
                    print(filepath, this_image.date_observed)
                    db.session.add(this_image)
                except Exception as e :
                    with open("error_report.txt","a") as logf:
                        logf.write("Failed to make db object {0}: {1}\n".format(filepath, str(e)))
                    print (str(e))
                
                
    db.session.commit()

# if __name__ == '__main__':

#     add_dir_to_db('/home/adeem/Desktop/growth/20190601')