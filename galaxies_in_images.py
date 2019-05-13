import numpy as np
from regions import PixCoord, PolygonPixelRegion
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import os
import pandas as pd
import argparse

def polygon_pix_pts2polygon_sky_reg(polygon_points,wcs):
    x_coord = polygon_points[:,0]
    y_coord = polygon_points[:,1]
    polygon_pix_reg = PolygonPixelRegion(vertices=PixCoord(x=x_coord, y=y_coord))
    polygon_sky_reg = polygon_pix_reg.to_sky(wcs)
    return polygon_sky_reg


def csv_points_in_image(image,points_array):
    hdu_list = fits.open(image)
    (y_end,x_end) = (hdu_list[0].data).shape
    wcs = WCS(hdu_list[0].header)
    hdu_list.close()

    corners = np.array([[0,0],[x_end,0],[x_end,y_end],[0,y_end]])
    polygon_sky_reg = polygon_pix_pts2polygon_sky_reg(corners,wcs)

    ra = points_array[:,0]
    dec = points_array[:,1]
    skycoord = SkyCoord(ra, dec, unit='deg')
    output_array = polygon_sky_reg.contains(skycoord, wcs)
    return output_array


def boolean_df(csv, dirname):
    galaxy_df = pd.read_csv(csv)
    galaxy_points_array = galaxy_df.loc[:,['RA','Dec']].values
    galaxy_bool_df = pd.DataFrame(columns=galaxy_df['Galaxy'])

    i=0
    for filename in (os.listdir(dirname)):
        print(i)
        i+=1
        fits_image_filename = os.path.join(dirname,filename)

        try:
            if fits_image_filename.endswith('wcs.fits'):            
                galaxy_bool_df.loc[filename] = csv_points_in_image(fits_image_filename, galaxy_points_array)

        except Exception :
            print('this file threw error '+ fits_image_filename)
            continue

    return galaxy_bool_df


def bool_df2list_of_galaxies(bool_df):
    list_of_galaxies_df = pd.DataFrame(columns=['Galaxies'])
    
    for filename, row_booleans in bool_df.iterrows():
        list_galaxies=[]
        for galaxy in bool_df.columns:
            if bool(row_booleans[galaxy]):
                list_galaxies.append(galaxy) 

        list_of_galaxies_df.loc[filename] = str(list_galaxies)[1:-1]
    return list_of_galaxies_df
        

def tile_id_df(bool_df, galaxy_df):

    tile_id_df = pd.DataFrame(columns=['image','ra','dec','tile_id', 'galaxy'])
    lst_sky_coords = []
    for filename, row_booleans in bool_df.iterrows():
        for galaxy in bool_df.columns :
            if bool_df.loc[filename][galaxy] :
                df_temp = galaxy_df[galaxy_df['Galaxy']==galaxy]
                ra = df_temp.iloc[0]['RA']
                dec = df_temp.iloc[0]['Dec']
                tile_id = df_temp.iloc[0]['id']
                lst_sky_coords.append([ra, dec,tile_id, galaxy])
    
    j=0
    for ra_dec_id_name in(lst_sky_coords):
        tile_id_df.loc[j] = [filename, ra_dec_id_name[0], ra_dec_id_name[1],ra_dec_id_name[2], ra_dec_id_name[3]]
        j+=1

    return tile_id_df

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Galaxies in images')
    parser.add_argument('-d', '--dirname', type=str, required=True, help='Path of directory containing images')
    parser.add_argument('-c','--csv_galaxies', type=str, required=True, help='Path of csv containing images')
    parser.add_argument('-t', '--tile_id_in_csv', type=bool, required=True, help='Does csv contain id')

    args = parser.parse_args()

    dirname = args.dirname
    csv_galaxies = args.csv_galaxies
    image_diagnol = 1
    buffer = 0.1

    bool_df = boolean_df(csv_galaxies, dirname)
    bool_df.to_csv(os.path.join(dirname, 'exact_bool.csv'))

    galaxies_df = pd.read_csv(csv_galaxies)
    list_of_galaxies_df = bool_df2list_of_galaxies(bool_df)
    list_of_galaxies_df.to_csv(os.path.join(dirname, 'exact_list.csv'))

    if args.tile_id_in_csv:
        tile_id_df = tile_id_df(bool_df,galaxies_df)
        tile_id_df.to_csv(os.path.join(dirname, 'exact_tile_id.csv'))