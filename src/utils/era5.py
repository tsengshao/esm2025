import numpy as np
from netCDF4 import Dataset
import sys, os
from datetime import datetime, timedelta

class Era5Retriever:
  def __init__(self, fdir, stime, reg=None):
    self.FDIR  = fdir   #str
    self.STIME = stime  #datetime
    self.REGION = reg or [0, 360, -90, 90, 1000, 100]
    self.VARD   = self._get_var_dicts()
    self.LON, self.LAT, self.LEV, self._SUBIDX = \
       self._set_coord()

  def _get_var_dicts(self):
    # keys  : variable name
    # value : list(type, fname_with_time_fmt, varname, )
    vard = {\
            'cwv':['sl', 'ERA5_cwv_%Y%m%d.nc', 'tcwv'],\
            'u':  ['pl', 'ERA5_pressure_essentials_%Y%m%d%H.nc', 'u'],\
            'v':  ['pl', 'ERA5_pressure_essentials_%Y%m%d%H.nc', 'v'],\
            't':  ['pl', 'ERA5_pressure_essentials_%Y%m%d%H.nc', 't'],\
            'q':  ['pl', 'ERA5_pressure_essentials_%Y%m%d%H.nc', 'q'],\
           }
    return vard

  def _gen_fname(self, varn, nowtime):
    vard = self.VARD[varn]
    fname =  nowtime.strftime(vard[1])
    #return f'{self.FDIR}/{vard[0]}/{varn}/{fname}'
    # for mog107
    return f'{self.FDIR}/{vard[0]}/{fname}'

  def _set_coord(self):
    glon, glat, glev = self._get_glob_coord()
    subidx  = self._get_subdomain_idx(self.REGION, glon, glat, glev)
    lon    = glon[subidx[0]:subidx[1]]
    lat    = glat[subidx[2]:subidx[3]]
    lev    = glev[subidx[4]:subidx[5]]
    return lon, lat, lev, subidx
 
  def _get_subdomain_idx(self, reg, glon, glat, glev): 
    ilon0 = np.argmin(np.abs(glon-reg[0]))
    ilon1 = np.argmin(np.abs(glon-reg[1]))+1
    ilat0 = np.argmin(np.abs(glat-reg[2]))
    ilat1 = np.argmin(np.abs(glat-reg[3]))+1
    ilev0 = np.argmin(np.abs(glev-reg[4]))
    ilev1 = np.argmin(np.abs(glev-reg[5]))+1
    return [ilon0, ilon1, ilat0, ilat1, ilev0, ilev1]

  def _get_glob_coord(self):
    fname = self._gen_fname('u', self.STIME)
    nc = Dataset(fname, 'r')
    lat = nc.variables['latitude'][::-1]
    lon = nc.variables['longitude'][:]
    lev = nc.variables['pressure_level'][:]
    nc.close()
    self._GLAT = lat
    self._GLON = lon
    self._GLEV = lev
    return lon, lat, lev
    
  def read_single_data(self, nowtime, varn):
    fname = self._gen_fname(varn, nowtime)
    yyyymmdd = nowtime.strftime('%Y%m%d')

    if '%Y%m%d%H' in self.VARD[varn][1]:
        it = 0
    else:
        it = int((nowtime - datetime.strptime(yyyymmdd,'%Y%m%d')).total_seconds() / 3600)
    nc = Dataset(fname, 'r')
    var = nc.variables[self.VARD[varn][2]][it]
    nc.close()
    if len(var.shape) == 3:
      var = var[:, ::-1, :]
      var = var[\
                self._SUBIDX[4]:self._SUBIDX[5],\
                self._SUBIDX[2]:self._SUBIDX[3],\
                self._SUBIDX[0]:self._SUBIDX[1],\
               ]
    elif len(var.shape) == 2:
      var = var[ ::-1, :]
      var = var[\
                self._SUBIDX[2]:self._SUBIDX[3],\
                self._SUBIDX[0]:self._SUBIDX[1],\
               ]
    return var

  def get_data(self, nt, var, stime=None, mean=None):
    if type(mean)==type(None):
      interval_dt = timedelta(minutes=60)
    elif mean=='hourly':
      interval_dt = timedelta(hours=1)
    elif mean=='daily':
      interval_dt = timedelta(days=1)
    elif type(mean)==type(timedelta(minutes=60)):
      interval_dt = mean

    # get interval_nt and check Divisible
    interval_era5 = timedelta(minutes=60)
    interval_nt = interval_dt/interval_era5
    if ( np.abs(interval_nt - int(interval_nt)) >= 1e-4 ):
      sys.exit(f'get_data ERROR: cant divisible when mean data ({interval_nt})')
    interval_nt = int( interval_nt)

    # check start time 
    stime = stime or self.STIME

    dum = self.read_single_data(stime, var)
    shape = dum.shape #data shape

    time_series = [] 
    data_series = []
    for it in range(nt):
      nowtime = stime + it * interval_dt
      data = np.zeros(shape)
      for isub in range(interval_nt):
        subtime = nowtime + isub * interval_era5
        dum = self.read_single_data(subtime, var)
        data += dum / interval_nt
      time_series.append(nowtime)
      data_series.append(data)
    return time_series, np.squeeze(np.array(data_series))

if __name__=='__main__':
  import matplotlib.pyplot as plt
  #/data/C.shaoyu/data/era5/cwbgfs_hourly/pl/ERA5_pressure_essentials_2016072900.nc
  fdir  = '/data/C.shaoyu/data/era5/cwbgfs_hourly/'
  #fdir  = '/nwpr/gfs/xb117/shao/2024final/rawdata/era5/'
  stime = datetime(2016,8,1,0,0)
  reg   = [90, 180, -10, 45, 1000., 100.]
  era5 = Era5Retriever(fdir, stime, reg)

  ########
  # get u / 1hr
  ########
  tseries_1hr, data_1hr = era5.get_data(nt=2, var='u', mean=None, stime=datetime(2016,8,3,0,0))

  # draw figure
  plt.figure()
  it = 0
  ilev = np.argmin(np.abs(era5.LEV-850))
  levels = np.arange(-25,25,3)
  plt.contour(era5.LON, era5.LAT, data_1hr[it,ilev],levels=levels, cmap=plt.cm.bwr)
  plt.title(tseries_1hr[it], loc='left')
  plt.title(era5.LEV[ilev], loc='right')
  plt.show()

  sys.exit()
  ########
  # get 30-min data
  ########
  tseries_1hr, data_1hr = era5.get_data(nt=10, var='cwv', mean=None)

  # draw figure
  plt.figure()
  it = 5 
  levels = np.arange(20,71,5)
  plt.contour(era5.LON, era5.LAT, data_1hr[it],levels=levels)
  plt.title(tseries_1hr[it])
  plt.show()

  # get 30-min data
  t_u_1hr, t_u_1hr = era5.get_data(nt=1, var='u')

  # get hourly data (5 hours, start from anohter day)
  tseries_0821_1hr, data_0821_1hr = \
    era5.get_data(nt=2, var='cwv', stime=datetime(2016,8,21,1,0), mean='hourly')

  # get daily data (10 days, daily mean)
  tseries_daily, data_daily = era5.get_data(nt=2, var='cwv', mean='daily')

  # get customized range (4 hour)
  tseries_cu, data_cu = era5.get_data(nt=6, var='cwv', mean=timedelta(hours=4))

