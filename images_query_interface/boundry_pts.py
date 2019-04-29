from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import numpy as np
import json

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
    coords = np.concatenate((ra.reshape((l,1)) ,dec.reshape((l,1))) ,axis=1)
    json_object = '{"coordinates":' + str(coords.tolist()) +' }'
    return json_object




