import numpy as np
from netCDF4 import Dataset
import sys, os
from datetime import datetime, timedelta
import h5py

class ImergRetriever:
  def __init__(self, fdir, stime, reg=None):
    self.FDIR  = fdir   #str
    self.STIME = stime  #datetime
    self.REGION = reg or [0, 360, -90, 90]
    self.LON, self.LAT, self._SUBIDX, self._SHIFT_LON0 = \
       self._set_coord()

  def _gen_fname(self, nowtime):
    yyyymm = nowtime.strftime("%Y%m")
    tistr  = nowtime.strftime("%Y%m%d_%H%M%S")
    return f'{self.FDIR}/{yyyymm}/imerg_{tistr}.HDF5'

  def _set_coord(self):
    glon, glat, shift_lon0 = self._get_glob_coord()
    subidx  = self._get_subdomain_idx(self.REGION, glon, glat)
    lon    = glon[subidx[0]:subidx[1]]
    lat    = glat[subidx[2]:subidx[3]]
    return lon, lat, subidx, shift_lon0
 
  def _get_subdomain_idx(self, reg, glon, glat): 
    ilon0 = np.argmin(np.abs(glon-reg[0]))
    ilon1 = np.argmin(np.abs(glon-reg[1]))+1
    ilat0 = np.argmin(np.abs(glat-reg[2]))
    ilat1 = np.argmin(np.abs(glat-reg[3]))+1
    return [ilon0, ilon1, ilat0, ilat1]

  def _get_glob_coord(self):
    fname = self._gen_fname(self.STIME)
    f = h5py.File(fname, 'r')
    lon = f['Grid']['lon'][:]
    lat = f['Grid']['lat'][:]
    f.close()
    lon = (lon+360)%360
    shift_lon0 = -1 * np.argmin(np.abs(lon-0.001))
    lon = np.roll(lon, shift_lon0)
    return lon, lat, shift_lon0
    
  def read_single_rain_data(self, nowtime):
    fname = self._gen_fname(nowtime)
    f = h5py.File(fname, 'r')
    rain = f['Grid']['precipitation'][0,:,:].T #[y(1800),x(3600)]
    f.close()
    rain = np.roll(rain, self._SHIFT_LON0, axis=1)
    rain = rain[self._SUBIDX[2]:self._SUBIDX[3],\
                self._SUBIDX[0]:self._SUBIDX[1]]
    return rain

  def get_data(self, nt, stime=None, mean=None):
    if type(mean)==type(None):
      interval_dt = timedelta(minutes=30)
    elif mean=='hourly':
      interval_dt = timedelta(hours=1)
    elif mean=='daily':
      interval_dt = timedelta(days=1)
    elif type(mean)==type(timedelta(minutes=30)):
      interval_dt = mean

    # get interval_nt and check Divisible
    interval_imerg = timedelta(minutes=30)
    interval_nt = interval_dt/interval_imerg
    if ( np.abs(interval_nt - int(interval_nt)) >= 1e-4 ):
      sys.exit(f'imerge class / get_data error: cant divisible when mean data ({interval_nt})')
    interval_nt = int( interval_nt)

    # check start time 
    stime = stime or self.STIME

    time_series = [] 
    data_series = []
    for it in range(nt):
      nowtime = stime + it * interval_dt
      rain = np.zeros((self.LAT.size, self.LON.size))
      for isub in range(interval_nt):
        subtime = nowtime + isub * interval_imerg
        dum = self.read_single_rain_data(subtime)
        rain += dum / interval_nt
      time_series.append(nowtime)
      data_series.append(rain)
    return time_series, np.squeeze(np.array(data_series))

if __name__=='__main__':
  #fdir  = '/nwpr/gfs/xb117/shao/2024final/rawdata/imerg/all_rename'
  fdir  = '/data/C.shaoyu/ESM2025/data/imerg/all_rename'
  stime = datetime(2016,8,1,0,0)
  reg   = [100, 200, -10, 45]
  imerg = ImergRetriever(fdir, stime, reg)
  

  # get 30-min data
  tseries_30m, data_30m = imerg.get_data(nt=10, mean=None)

  # get hourly data (5 hours, start from anohter day)
  tseries_hourly, data_hourly = imerg.get_data(nt=5, stime=datetime(2016,8,21,1,0), mean='hourly')

  # get daily data (10 days, daily mean)
  tseries_daily, data_daily = imerg.get_data(nt=2, mean='daily')

  # get customized range (4 hour)
  tseries_cu, data_cu = imerg.get_data(nt=6, mean=timedelta(hours=4))

