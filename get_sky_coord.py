import numpy as np
from regions import PixCoord, PolygonPixelRegion
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import os
import pandas as pd

def rect2polygon(x_end,y_end,n_of_div):
    n = n_of_div
    corners = np.array([[0,0],[x_end,0],[x_end,y_end],[0,y_end]])
    output = np.zeros((4*n,2))
    for i in range(4):
        x_points = np.linspace(corners[i][0], corners[(i+1)%4][0], n+1)[:-1]
        y_points = np.linspace(corners[i][1], corners[(i+1)%4][1], n+1)[:-1]
        output[i*n:(i+1)*n] = np.concatenate((x_points.reshape((n,1)) ,y_points.reshape((n,1))) ,axis=1)
    return output


def polygon_pix_pts2polygon_sky_reg(polygon_points,wcs):
    x_coord = polygon_points[:,0]
    y_coord = polygon_points[:,1]
    polygon_pix_reg = PolygonPixelRegion(vertices=PixCoord(x=x_coord, y=y_coord))
    polygon_sky_reg = polygon_pix_reg.to_sky(wcs)
    return polygon_sky_reg


def csv_points_in_image(image,points_array):
    hdu_list = fits.open(image)
    image_data = hdu_list[0].data
    (y_end,x_end) = image_data.shape
    wcs = WCS(hdu_list[0].header)
    hdu_list.close()

    corners = np.array([[0,0],[x_end,0],[x_end,y_end],[0,y_end]])
    polygon_sky_reg = polygon_pix_pts2polygon_sky_reg(corners,wcs)

    ra = points_array[:,0]
    dec = points_array[:,1]
    skycoord = SkyCoord(ra, dec, unit='deg')
    output_array = polygon_sky_reg.contains(skycoord, wcs)
    return output_array




ned_csv = '/home/adeem/Desktop/growth/ned_galaxies_A.csv'
glade_csv = '/home/adeem/Desktop/growth/glade_galaxies_A.csv'
dirname = '/home/adeem/Desktop/growth/20190505'
n_of_div = 1


df_ned_full = pd.read_csv(ned_csv)
points_array_ned = df_ned_full.iloc[:,[2,3]].values
df_ned_bool = pd.DataFrame(columns=df_ned_full.iloc[:,4])

df_glade_full = pd.read_csv(glade_csv)
points_array_glade = df_glade_full.iloc[:,[3,4]].values
df_glade_bool = pd.DataFrame(columns=df_glade_full.iloc[:,5])

# print(df_ned_full[df_ned_full['Galaxy']==galaxy])
df_sky_coords = pd.DataFrame(columns=['image','ra','dec','tile_id'])





i=0
j=0
for filename in (os.listdir(dirname)):
    fits_image_filename = os.path.join(dirname,filename)
    # try:
    hdu_list = fits.open(fits_image_filename)
    wcs = WCS(hdu_list[0].header)
    print(wcs)
    hdu_list.close()
    try:
        if fits_image_filename.endswith('wcs.fits'):
            
            df_ned_bool.loc[filename] = csv_points_in_image(fits_image_filename, points_array_ned, n_of_div)

            lst_sky_coords = []
            for galaxy in df_ned_bool.columns :
                if df_ned_bool.loc[filename][galaxy] :
                    df_temp = df_ned_full[df_ned_full['Galaxy']==galaxy]
                    # print(df_temp)
                    ra_ned = df_temp.iloc[0]['RA']
                    dec_ned = df_temp.iloc[0]['Dec']
                    tile_id_ned = df_temp.iloc[0]['id']
                    lst_sky_coords.append([ra_ned, dec_ned,tile_id_ned])

            df_glade_bool.loc[filename] = csv_points_in_image(fits_image_filename, points_array_glade, n_of_div)
            
            for galaxy in df_glade_bool.columns :
                # print(df_glade_bool.loc[filename][galaxy])
                if df_glade_bool.loc[filename][galaxy] :
                    df_temp = df_glade_full[df_glade_full['Galaxy']==galaxy]
                    # print(df_temp)
                    ra_glade = df_temp.iloc[0]['RA']
                    dec_glade = df_temp.iloc[0]['Dec']
                    tile_id_glade = str(df_temp.iloc[0]['id'])
                    lst_sky_coords.append([ra_glade, dec_glade,tile_id_glade])

            for ra_dec_id in(lst_sky_coords):
                df_sky_coords.loc[str(j)] = [filename, ra_dec_id[0], ra_dec_id[1],ra_dec_id[2]]
                j+=1

            
            print(i)
            i+=1
    except Exception :
        print(Exception)
        print('this file threw error')
        print(fits_image_filename)
        continue



# df_ned_bool.to_csv('ned_bool_20190501.csv')
# df_glade_bool.to_csv('glade_bool_20190501.csv')
# df_of_galaxies.to_csv('ned&glade_20190501.csv')
df_sky_coords.to_csv('/home/adeem/Desktop/growth/sky_coords_20190505.csv')


print(df_sky_coords)