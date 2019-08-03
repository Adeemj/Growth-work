import matplotlib
import matplotlib.pyplot as plt
from astropy.io import fits
import numpy as np
import os
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.coordinates import EarthLocation
from astropy.time import Time
from astropy.coordinates import AltAz
from astropy.coordinates import ICRS
from astropy import coordinates as coord
import argparse
import pandas as pd
from collections import OrderedDict
from matplotlib.figure import Figure

def date2list_filepaths(date):
	reqfiles=[]
	for path, subdirs, files in os.walk('/home/user/Documents/seeing/{}'.format(date),topdown=True):
    		for x in files:
        		if x.endswith("proc.cr.fits") == True:
           		 	reqfiles.append(os.path.join(path, x))
	return reqfiles

def list_filepaths2data(list_filepaths):
	tar_ra=[]
	tar_dec=[]
	fwhm=[]
	date_obs=[]
	filters=[]
	jd=[]
	lim_mag=[]
	exp_time=[]
	iaohanle = EarthLocation(lat=32.778889*u.deg , lon=78.964722*u.deg ,height=4500*u.m)
	
	for file in list_filepaths:
		hdu = fits.open(file)[0]
		data=hdu.data
		header=hdu.header
	
		tar_ra.append(header['TARRA'])
		tar_dec.append(header['TARDEC'])
		fwhm.append(header['MED_FWHM']) 
		date_obs.append(header['DATE-OBS'])
		filters.append(header['FILTER'])
		jd.append(header['JD'])
		lim_mag.append(header['LIM_MAG'])
		exp_time.append(header['EXPTIME'])
		
	tar_ra=np.array(tar_ra)
	tar_dec=np.array(tar_dec)
	fwhm=np.array(fwhm)
	filters=np.array(filters)
	date_obs=np.array(date_obs)
	observing_time = Time(date_obs)
	aa=coord.AltAz(location=iaohanle,obstime=observing_time)
	target = coord.SkyCoord(tar_ra * u.deg, tar_dec * u.deg, frame='icrs')
	x=target.transform_to(aa)
	az=x.az.value
	alt=x.alt.value
	table=pd.DataFrame({'observing_time':jd,'exposure_time':exp_time,'azimuth':az,'altitude':alt,'fwhm':fwhm,'lim_mag':lim_mag,'filter':filters},columns=['observing_time','exposure_time','azimuth','altitude','fwhm','lim_mag','filter'])
	return table
	

def marker():
	marker_dict=OrderedDict()
	marker_dict['z']='>'
	marker_dict['u']='v'
	marker_dict['i']='^'
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
	axis.set_title('Date of observation : {}'.format(args.date))
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

def subplot_alt_az_fwhm(data_df,marker_dict):
	fig=plt.figure()
	axis1 = fig.add_subplot(1,2,1)
	for kind in marker_dict.keys():
		d=data_df[data_df['filter']==kind]
		img1=axis1.scatter(d['altitude'],d['fwhm'],marker=marker_dict[kind],s=50,edgecolor='none')
	axis1.set_ylim(min(data_df['fwhm'])-0.2,max(data_df['fwhm'])+0.2)
	axis1.set_xlabel('altitude (degree)')
	axis1.set_ylabel('FWHM')
	plt.grid()
	axis1.set_title('Date of observation : {}'.format(args.date))
	plt.legend(['z-filter','u-filter','i-filter','g-filter','r-filter'],loc='upper center',bbox_to_anchor= (0.5,-0.05), ncol=6, fancybox=True)
	axis2 = fig.add_subplot(1,2,2)
	for kind in marker_dict.keys():
		d=data_df[data_df['filter']==kind]
		img2=axis2.scatter(d['azimuth'],d['fwhm'],marker=marker_dict[kind],s=50,edgecolor='none')
	axis2.set_ylim(min(data_df['fwhm'])-0.2,max(data_df['fwhm'])+0.2)
	axis2.set_xlabel('azimuth (degree)')
	axis2.set_ylabel('FWHM')
	plt.grid()
	axis2.set_title('Date of observation : {}'.format(args.date))
	return fig

def plot_limmagVSobstime(data_df,marker_dict):
	fig=plt.figure()
	axis = fig.add_subplot(1,1,1)
	for kind in marker_dict.keys():
		d=data_df[data_df['filter']==kind]
		img=axis.scatter(d['observing_time'],d['lim_mag'],c=d['exposure_time'],cmap='viridis',marker=marker_dict[kind],s=50,edgecolor='none')
	clb=plt.colorbar(img)
	clb.set_label('exposure time (seconds)')
	axis.set_ylim(max(data_df['lim_mag'])+0.2,min(data_df['lim_mag'])-0.2)
	axis.set_xlabel('observation time (JD)')
	axis.set_ylabel('limiting magnitude')
	axis.set_title('Date of observation : {}'.format(args.date))
	plt.legend(['z-filter','u-filter','i-filter','g-filter','r-filter'],loc='upper center',bbox_to_anchor= (0.5,-0.05), ncol=6, fancybox=True)
	plt.grid()
	return fig

def plot_limmagVSexptime(data_df,marker_dict):
	fig=plt.figure()
	axis = fig.add_subplot(1,1,1)
	for kind in marker_dict.keys():
		d=data_df[data_df['filter']==kind]
		img=axis.scatter(d['exposure_time'],d['lim_mag'],marker=marker_dict[kind],s=50,edgecolor='none')
	axis.set_ylim(max(data_df['lim_mag'])+0.2,min(data_df['lim_mag'])-0.2)
	axis.set_xlabel('exposure time (seconds)')
	axis.set_ylabel('limiting magnitude')
	axis.set_title('Date of observation : {}'.format(args.date))
	plt.legend(['z-filter','u-filter','i-filter','g-filter','r-filter'],loc='upper center',bbox_to_anchor= (0.5,-0.05), ncol=6, fancybox=True)
	plt.grid()
	return fig


