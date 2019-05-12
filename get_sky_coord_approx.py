import numpy as np
from regions import PixCoord, PolygonPixelRegion
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import os
import pandas as pd

def give_boolean(ref_ra, ref_dec, ra, dec, image_diagnol, buffer):
    ra_min = ra-(image_diagnol/2 + buffer)/np.cos(np.deg2rad(dec))
    ra_max = ra+(image_diagnol/2 + buffer)/np.cos(np.deg2rad(dec))

    if ra_min<0.0:
        ra_condition = ((ref_ra>=0.0) & (ref_ra<=ra_max)) | ((ref_ra>=360.0+ra_min) & (ref_ra<=360.0))
    elif ra_max>360.0:
        ra_condition = ((ref_ra>=0.0) & (ref_ra<=-360.0+ra_max)) | ((ref_ra>=ra_min) & (ref_ra<=360))
    else :
        ra_condition = ((ref_ra>=ra_min) & (ref_ra<=ra_max))
    
    dec_min = dec-(image_diagnol/2 + buffer)
    dec_max = dec+(image_diagnol/2 + buffer)

    if dec_min<(-90.0):
        dec_condition = (ref_dec<=dec_max)
    elif dec_max>(90.0):
        dec_condition = (ref_dec>=dec_min)
    else :
        dec_condition = ((ref_dec>=dec_min) & (ref_dec<=dec_max))

    return ra_condition and dec_condition


dirname = '/home/adeem/Desktop/growth/20190428'
csv_galaxies = '/home/adeem/Desktop/growth/ned_galaxies_A.csv'
image_diagnol = 1
buffer = 0.1

df_galaxies = pd.read_csv(csv_galaxies)

galaxies_bool = pd.DataFrame(columns= df_galaxies['Galaxy'])
i=0
for filename in os.listdir(dirname):
    # print(filename)
    print(i)
    i+=1
    fits_image_filename = os.path.join(dirname,filename)

    hdu_list = fits.open(fits_image_filename)
    header = hdu_list[0].header
    ref_ra = header['CRVAL1']
    ref_dec = header['CRVAL2']
    hdu_list.close()

    bool_lst = []
    for galaxy in df_galaxies['Galaxy']:
        df_temp = df_galaxies[df_galaxies['Galaxy']==galaxy]
        ra = float(df_temp['RA'])
        dec = float(df_temp['Dec'])

        # print(give_boolean(ref_ra, ref_dec, ra, dec, image_diagnol, buffer))        
        bool_lst.append(give_boolean(ref_ra, ref_dec, ra, dec, image_diagnol, buffer))
    
    galaxies_bool.loc[filename] = bool_lst

print(galaxies_bool)

exact = pd.read_csv('/home/adeem/Desktop/growth/ned_bool_20190428.csv')
exact = exact.set_index(exact.columns[0]) 

# print(exact.columns)
# print(len(galaxies_bool.columns))
print(exact==galaxies_bool)
galaxies_bool.to_csv('approx20190428.csv')

        