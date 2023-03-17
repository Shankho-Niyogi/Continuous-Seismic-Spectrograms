#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 12:26:07 2023

@author: Shankho
"""

import numpy as np                
import matplotlib.pyplot as plt   
import obspy                      
import os
from obspy.core import read
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from datetime import datetime, timedelta
import numpy as np

client = Client("IRIS")
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = 20, 10

parentdir = '/bigdata/aghoshlab/sniyo001/Anza/' # location where spectrograms will be saved under YMD folder

interval = 10*60 # window of data to be displayed as spectrogram and trace 
starttime = obspy.UTCDateTime(2019, 4, 3, 0, 0, 0) # set start time here, the format is YMDhms 
endtime = obspy.UTCDateTime(2019, 4, 4, 0, 0, 0) # set end time here, preferably should align with the interval set earlier
duration = endtime - starttime

freqmin_trace = 1 # min freq of trace
freqmax_trace = 10 # max freq of trace

freqmin_spec = 1 # min freq of spectrogram
freqmax_spec = 25 # max freq of spectrogram

network = 'PB' # enter network name here
st_list=['B081','B082','B082A','B084','B086','B086A','B087','B088','B088A','B093','B946','B087','B946','P482','P484','P797','PMOB'] # enter station list here
ch_list = ['HHZ','EHZ','HNZ'] # enter channel list here

for idx2,channel_current in enumerate(ch_list):
    for i in range(0,int(duration/interval)):
      os.chdir(parentdir)
      st_start = starttime + i*interval
      st_end = st_start + interval
      for idx,st_current in enumerate(st_list):
          print(st_list[idx])
          try:
              st = client.get_waveforms(network=network, station=st_list[idx], location='*',channel=ch_list[idx2], starttime=st_start, endtime=st_end)
              st2 = st.copy()
              sps = int(st2[0].stats.sampling_rate)
              st2.detrend('linear')
              st2.detrend('demean')
              st2.taper(max_percentage=0.05, type='hann')
              st2.filter('bandpass',freqmin=freqmin_trace, freqmax=freqmax_trace, corners=4, zerophase=True)
              
              tr = st[0].copy()
              
              fig = plt.figure()
              ax1 = fig.add_axes([0.1, 0.75, 0.7, 0.2]) #[left bottom width height]
              ax2 = fig.add_axes([0.1, 0.1, 0.7, 0.60], sharex=ax1)
              ax3 = fig.add_axes([0.83, 0.1, 0.03, 0.6])
              
              t = np.arange(st2[0].stats.npts) / st2[0].stats.sampling_rate
              ax1.plot(t, st2[0].copy().data, 'k')
              ax1.set_title(str(tr.id) +str(' :Start of Trace: ')+ str(st[0].stats.starttime) + '\n' + 'Bandpass filtering of trace: '+ str(freqmin_trace)+' - '+str(freqmax_trace)+' Hz') # Add a title to the plot
              
              utc_datetime = datetime.strptime(str(st[0].stats.starttime), '%Y-%m-%dT%H:%M:%S.%fZ')
              t_datetime = [utc_datetime + timedelta(seconds=float(x)) for x in t] # Convert the time values to datetime objects
              t_mins_secs = [x.strftime('%M:%S') for x in t_datetime] # Format the datetime objects as strings
              
              x_tick_pos_int = 2 #intervals in minute
              
              ax1.set_xticks(t[::x_tick_pos_int*3000]) # Set the x-tick positions to every minute
              ax1.set_xticklabels(t_mins_secs[::x_tick_pos_int*3000]) # Set the x-tick labels to the formatted strings
              
              tr.spectrogram(wlen=0.05*sps, per_lap=0.90, dbscale=True, log=False, axes=ax2, cmap='jet')
              
              ax2.set_ylim((freqmin_spec,freqmax_spec))
              
              ax2.set_ylabel('Frequency (Hz)', fontsize = 18)
              ax1.set_xticks(t[::x_tick_pos_int*3000]) # Set the x-tick positions to every minute
              ax1.set_xticklabels(t_mins_secs[::x_tick_pos_int*3000]) # Set the x-tick labels to the formatted strings
              ax2.set_xlabel('Time (mm:ss)', fontsize = 18) # Set the x-axis label
              mat_values = ax2.images[0].get_array()
              mean = np.mean(mat_values)
              std = np.std(mat_values)
              vmin = mean - 3 * std
              vmax = mean + 3 * std
              ax2.images[0].set_clim(vmin = vmin, vmax=vmax)
              mappable = ax2.images[0]
              cb = plt.colorbar(mappable=mappable, cax=ax3)
              cb.set_label('Power (dB/Hz)')
              
              dayname = parentdir+str(tr.stats.starttime.strftime('%Y'))+str(tr.stats.starttime.strftime('%m'))+str(tr.stats.starttime.strftime('%d'))+str('/')+str(st[0].stats.network)+str('.')+str(st[0].stats.station)+str('.')+str(st[0].stats.location)+str('.')+str(st[0].stats.channel)+str('/')
              if os.path.exists(dayname):
                  os.chdir(dayname)
              else:
                  os.makedirs(dayname)
                  os.chdir(dayname)
    
    
              plt.savefig('Spectrogram_'+network+'_'+st_list[idx]+'_'+str(tr.stats.starttime.strftime('%Y'))+str(tr.stats.starttime.strftime('%m'))+str(tr.stats.starttime.strftime('%d'))+'T'+str(tr.stats.starttime.strftime('%H'))+str(tr.stats.starttime.strftime('%M'))+str(tr.stats.starttime.strftime('%S'))+'.png',facecolor='w', edgecolor='w')
              plt.close(fig)
              del st
          except:
              os.chdir(parentdir)
              pass
              