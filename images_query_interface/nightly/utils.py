from astropy.io import fits
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.coordinates import EarthLocation
from astroplan import Observer
from dateutil.parser import parse
import pytz
import datetime
import numpy as np
import pandas as pd
from collections import OrderedDict 
from matplotlib import pyplot as plt


def time2utc_ist(time):
    date_time_object_utc = parse(time.iso).replace(tzinfo=pytz.timezone('UTC'))
    date_time_object_ist = date_time_object_utc.astimezone(pytz.timezone('Asia/Calcutta'))
    return {'utc':date_time_object_utc, 'ist':date_time_object_ist}


def utc2ist(date_utc):
    date_time_object_utc = date_utc.replace(tzinfo=pytz.timezone('UTC'))
    date_time_object_ist = date_time_object_utc.astimezone(pytz.timezone('Asia/Calcutta'))
    return date_time_object_ist


def date2dict_times(date):
    day = Time(date, format='iso')

    longitude = '78d57m53s'
    latitude = '32d46m44s'
    elevation = 4500 * u.m
    location = EarthLocation.from_geodetic(longitude, latitude, elevation)
    iaohanle = Observer(location = location,name = "IAO", timezone='Asia/Kolkata',description = "GROWTH-India 70cm telescope")
    
    
    sunset_iao = iaohanle.sun_set_time(day, which='next')
    sunrise_iao = iaohanle.sun_rise_time(day, which='next')
    twelve_twil_eve_iao = iaohanle.twilight_evening_nautical(day,which='next')
    eighteen_twil_eve_iao = iaohanle.twilight_evening_astronomical(day, which='next')
    twelve_twil_morn_iao = iaohanle.twilight_morning_nautical(day,which='next')
    eighteen_twil_morn_iao = iaohanle.twilight_morning_astronomical(day, which='next')


    dict_times = OrderedDict()
    dict_times['Sunset '] = time2utc_ist(sunset_iao)
    dict_times['Sunrise '] = time2utc_ist(sunrise_iao)
    dict_times['Twelve degree Evening Twilight '] = time2utc_ist(twelve_twil_eve_iao)
    dict_times['Eighteen degree Evening Twilight '] = time2utc_ist(eighteen_twil_eve_iao)
    dict_times['Twelve degree Morning Twilight '] = time2utc_ist(twelve_twil_morn_iao)
    dict_times['Eighteen degree Morning Twilight '] = time2utc_ist(eighteen_twil_morn_iao)
    return dict_times


def list_images2dict_targets_time(list_images):
    dict_targets = {}
    total_exposure = 0
    for image in list_images:
        total_exposure+=image.exposure
        if image.tar_name in dict_targets.keys():
            dict_targets[image.tar_name].append(image.filter_used)
        else:
            dict_targets[image.tar_name] = [image.filter_used]
    
    return dict_targets, total_exposure


def list_images2obs_start_end(list_images):
    obs_start_time = {}
    obs_start_time['utc'] = list_images[0].date_observed
    obs_start_time['ist'] = utc2ist(obs_start_time['utc'])
    obs_end_time = {}
    obs_end_time['utc'] = list_images[-1].date_observed+ datetime.timedelta(seconds=list_images[-1].exposure)
    obs_end_time['ist'] = utc2ist(obs_end_time['utc'])
    
    return obs_start_time, obs_end_time

def list_filepaths2data(list_filepaths):
    tar_ra=[]
    tar_dec=[]
    fwhm=[]
    date_obs=[]
    filters=[]
    jd=[]
    lim_mag=[]
    exp_time=[]
    az = []
    alt = []
	
    for file in list_filepaths:
        hdu = fits.open(file)[0]
        data=hdu.data
        header=hdu.header

        tar_ra.append(header['TARRA'])
        tar_dec.append(header['TARDEC'])
        fwhm.append(header['FWHM']) 
        date_obs.append(header['DATE-OBS'])
        filters.append(header['FILTER'])
        jd.append(header['JD'])
        exp_time.append(header['EXPTIME'])
        az.append(header['TEL_AZ'])
        alt.append(header['TEL_ALT'])

    tar_ra=np.array(tar_ra)
    tar_dec=np.array(tar_dec)
    fwhm=np.array(fwhm)
    filters=np.array(filters)
    jd = np.array(jd)
    exp_time = np.array(exp_time)
    date_obs=np.array(date_obs)
    observing_time = Time(date_obs)
    az = np.array(az)
    alt = np.array(alt)
    print(len(tar_ra), len(tar_dec), len(fwhm), len(filters), len(date_obs), )
    table=pd.DataFrame({'observing_time':jd,'exposure_time':exp_time,'azimuth':az,'altitude':alt,'fwhm':fwhm,'filter':filters},columns=['observing_time','exposure_time','azimuth','altitude','fwhm','filter'])
    return table
def marker():
	marker_dict=OrderedDict()
	marker_dict['z']='X'
	marker_dict['u']='v'
	marker_dict['i']='*'
	marker_dict['g']=','
	marker_dict['r']='o'
	return marker_dict

def plt_altVSfwhm(data_df,marker_dict):
	fig=plt.figure()
	axis = fig.add_subplot(1,1,1)
	for kind in marker_dict.keys():
		d=data_df[data_df['filter']==kind]
		img=axis.scatter(d['altitude'],d['fwhm'],c=d['azimuth'],cmap='viridis',s=50,marker=marker_dict[kind],edgecolor='none')
	clb=plt.colorbar(img)
	clb.set_label('azimuth (degree)')
	axis.set_xlabel('altitude (degree)')
	axis.set_ylabel('FWHM')
	axis.set_title('Alt VS FWHM')
	plt.grid()
	plt.legend(['z-filter','u-filter','i-filter','g-filter','r-filter'],loc='upper center',bbox_to_anchor= (0.5,-0.05), ncol=6, fancybox=True)
	return fig

def histogram_fwhm(data_df):
	fig=plt.figure()
	axis = fig.add_subplot(1,1,1)
	img=axis.hist(data_df['fwhm'])
	axis.set_xlabel('FWHM')
	axis.set_ylabel('frequency')
	axis.set_title('Date of observation : {}'.format(args.date))
	plt.grid()
	return fig