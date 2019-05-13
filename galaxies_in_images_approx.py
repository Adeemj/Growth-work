import numpy as np
from astropy.io import fits
import os
import pandas as pd
import argparse
from galaxies_in_images import bool_df2list_of_galaxies, tile_id_df


def condition_bool(ref_ra, ref_dec, ra, dec, image_diagnol, buffer):
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


def boolean_df_approx(csv, dirname, image_diagnol, buffer):
    df_galaxies = pd.read_csv(csv)
    galaxies_bool = pd.DataFrame(columns= df_galaxies['Galaxy'])
    i=0
    for filename in os.listdir(dirname):
        print(i)
        i+=1
        fits_image_filename = os.path.join(dirname,filename)
        if fits_image_filename.endswith('wcs.fits'):
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
                bool_lst.append(condition_bool(ref_ra, ref_dec, ra, dec, image_diagnol, buffer))
            
            galaxies_bool.loc[filename] = bool_lst

    return galaxies_bool

parser = argparse.ArgumentParser(description='Galaxies in images')
parser.add_argument('-d', '--dirname', type=str, required=True, help='Path of directory containing images')
parser.add_argument('-c','--csv_galaxies', type=str, required=True, help='Path of csv containing images')
parser.add_argument('-t', '--tile_id_in_csv', type=bool, required=True, help='Does csv contain id')

args = parser.parse_args()

dirname = args.dirname
csv_galaxies = args.csv_galaxies
image_diagnol = 1
buffer = 0.1

bool_df = boolean_df_approx(csv_galaxies, dirname, image_diagnol, buffer)
bool_df.to_csv(os.path.join(dirname, 'approx_bool.csv'))

galaxies_df = pd.read_csv(csv_galaxies)
list_of_galaxies_df = bool_df2list_of_galaxies(bool_df)
list_of_galaxies_df.to_csv(os.path.join(dirname, 'approx_list.csv'))

if args.tile_id_in_csv:
    tile_id_df = tile_id_df(bool_df,galaxies_df)
    tile_id_df.to_csv(os.path.join(dirname, 'approx_tile_id.csv'))