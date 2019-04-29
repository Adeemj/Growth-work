from images_query_interface import db
import os
from astropy.io import fits
from astropy.wcs import WCS
from images_query_interface.boundry_pts import boundry_points
import datetime

class Image(db.Model):

    date_observed = db.Column(db.DateTime, unique=True, nullable=False)
    mjd = db.Column(db.Float, primary_key=True)

    filter_used = db.Column(db.String(20))
    exposure = db.Column(db.Float)
    air_mass = db.Column(db.Float)
    ccd_temp = db.Column(db.Float)
    image_type = db.Column(db.String(20))  
    focus_value = db.Column(db.String(20))

    file_path = db.Column(db.String(120), unique=True, nullable=False)

    tel_alt = db.Column(db.Float)
    tel_az = db.Column(db.Float)

    ref_ra =  db.Column(db.Float)
    ref_dec = db.Column(db.Float)

    tar_ra = db.Column(db.String(20))
    tar_dec = db.Column(db.String(20))
    tar_name = db.Column(db.String(20))

    boundry_points = db.Column(db.String(120))

    

    def __repr__(self):
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items())


def read_header(key,header_dict):
    try:
        return header_dict[key]
    except KeyError:
        return None
        



def date_time_object(string_input):
    datetime_list = string_input.split('T')
    date = datetime_list[0]
    time = datetime_list[1]
    date_object = datetime.datetime.strptime(date,"%Y-%m-%d")
    time_object = datetime.datetime.strptime(time,"%H:%M:%S.%f")
    date_time_object = datetime.datetime.combine(date_object, time_object.time())
    return date_time_object

def add_to_db(dirname,append):
    if not append:
        db.drop_all()
        db.create_all()

    for filename in os.listdir(dirname):
        fits_image_filename = os.path.join(dirname,filename)
        hdul = fits.open(fits_image_filename)
        hdr = hdul[0].header
        (y_end,x_end) = hdul[0].data.shape 
        hdul.close()
        wcs = WCS(hdr)
        
        n_of_div = 1

        image1 = Image(
        date_observed = date_time_object(read_header('DATE-OBS',hdr)),
        mjd = read_header('JD',hdr),

        filter_used = read_header('FILTER',hdr),
        exposure = read_header('EXPOSURE',hdr),
        air_mass = read_header('AIRMASS',hdr),
        ccd_temp = read_header('CCD_TEMP',hdr),
        image_type = read_header('IMAGETYP',hdr),
        focus_value = read_header('FOCUSER',hdr),

        file_path = fits_image_filename,

        tel_alt = read_header('TEL_ALT',hdr),
        tel_az = read_header('TEL_AZ',hdr),

        ref_ra = read_header('CRVAL1',hdr),
        ref_dec = read_header('CRVAL2',hdr),

        tar_ra = read_header('TARRA',hdr),
        tar_dec = read_header('TARDEC',hdr),
        tar_name = read_header('OBJECT',hdr),

        boundry_points = boundry_points(x_end,y_end,wcs,n_of_div)

        )
#/home/adeem/flask-tutorial/flaskr/drive-download-20190314T125514Z-001
        
        db.session.add(image1)

    db.session.commit()
