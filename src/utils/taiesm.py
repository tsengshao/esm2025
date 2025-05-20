import numpy as np
import os, sys, re, glob
from datetime import datetime, timedelta
from netCDF4 import Dataset

class TaiESMRetriever:
  def __init__(self, esm_archive_dir, exp, reg=None, iens=-1):

    #self.EXPDIR   = f'{esm_archive_dir}/{exp}/'   #str
    self.ARCDIR   = esm_archive_dir
    self.EXPROOT  = exp
    self.ENSLIST  = self._find_ens_folders(self.EXPROOT)  #list ['16080100', '16081100']
    _             = self.set_ens(iens)
    self.REGION = reg or [0, 360.001, -90, 90.001, 1000, 100]
    self.LON, self.LAT, self.LEV, self.MLEV, self._SUBIDX, = \
       self._set_coord()
    self.VARINFO   = self._build_variable_to_h_type_map()
  
  def set_ens(self, iens=-1):
    if (iens==-1): # no ensumble
      self.EXP      = f'{self.EXPROOT}'
      self.EXPDIR   = f'{self.ARCDIR}/{self.EXP}'
    elif (iens >= len(self.ENSLIST)):
      print(f'ERROR cant set ens, iens({iens}) >= num_of_ens({len(self.ENSLIST)})')
      sys.exit()
    else:
      self.ENS      = self.ENSLIST[iens]
      self._iENS    = iens
      self.EXP      = f'{self.EXPROOT}_{self.ENS}'
      self.EXPDIR   = f'{self.ARCDIR}/{self.EXP}'
      print(f'{self.__class__.__name__} ... set ENS to {self.ENS} ({iens})')
      return 

  def _build_variable_to_h_type_map(self):
      nowtime = datetime.strptime(self.ENS, '%Y%m%d%H')
      fname = self._gen_fname(nowtime, 'h*')
      nc_files = glob.glob(fname)
      var_info = {}

      for nc_file in nc_files:
          h_match = re.search(r'\.cam\.(h\d+)\.', nc_file)
          if not h_match:
              continue
          htype = h_match.group(1)  # e.g., 'h0', 'h1'

          try:
              with Dataset(nc_file, 'r') as ds:
                  for var_name, var_obj in ds.variables.items():
                      dims = len(var_obj.shape)
                      dim_type = '3d' if dims==4 else '2d'

                      if var_name not in var_info:
                          var_info[var_name] = {'htypes': [htype], 'dims': [dim_type]}
                      else:
                          if htype not in var_info[var_name]['htypes']:
                              var_info[var_name]['htypes'].append(htype)
                              var_info[var_name]['dims'].append(dim_type)
          except Exception as e:
                print(f"Error reading {nc_file}: {e}")
      return var_info

  def _find_ens_folders(self, experiment_name):
      dates = []
      pattern = re.compile(rf"^{re.escape(experiment_name)}_([0-9]{{10}})$")
  
      for name in os.listdir(f'{self.ARCDIR}'):
          match = pattern.match(name)
          if match:
              dates.append(match.group(1))
      return sorted(dates)

  def _gen_fname(self, nowtime, hstr:str='h0'):
    dstr = nowtime.strftime('%Y-%m-%d-00000')
    fname = f'{self.EXPDIR}/atm/hist/{self.EXP}.cam.{hstr}.{dstr}.nc'
    #print(fname)
    return fname

  def _set_coord(self):
    glon, glat, glev, gmlev = self._get_glob_coord()
    subidx  = self._get_subdomain_idx(self.REGION, glon, glat, glev)
    lon    = glon[subidx[0]:subidx[1]]
    lat    = glat[subidx[2]:subidx[3]]
    lev    = glev[subidx[4]:subidx[5]]
    mlev   = gmlev
    return lon, lat, lev, gmlev, subidx
 
  def _get_subdomain_idx(self, reg, glon, glat, glev): 
    ilon0 = np.argmin(np.abs(glon-reg[0]))
    ilon1 = np.argmin(np.abs(glon-reg[1]))+1
    ilat0 = np.argmin(np.abs(glat-reg[2]))
    ilat1 = np.argmin(np.abs(glat-reg[3]))+1
    ilev0 = np.argmin(np.abs(glev-reg[4]))
    ilev1 = np.argmin(np.abs(glev-reg[5]))+1
    return [ilon0, ilon1, ilat0, ilat1, ilev0, ilev1]

  def _get_glob_coord(self):
    nowtime = datetime.strptime(self.ENS, '%Y%m%d%H')
    fname = self._gen_fname(nowtime, 'h1')
    nc = Dataset(f'{fname}')
    inlon = nc.variables['lon'][:]
    inlat = nc.variables['lat'][:]
    inmlev = nc.variables['lev'][:]
    inlev = np.array([100, 125, 150, 175, 200, 225, \
                     250, 300, 350, 400, 450, 500, \
                     550, 600, 650, 700, 750, 775, \
                     800, 825, 850, 875, 900, 925, \
                     950, 975, 1000])[::-1]
    dlon = inlon[1] - inlon[0]
    dlat = inlat[1] - inlat[0]
    nlon = inlon.size
    nlat = inlat.size
    nmlev = inmlev.size
    nlev = inlev.size
    

    self._NGLON  = nlon
    self._NGLAT  = nlat
    self._NGLEV  = nlev
    self._NGMLEV = nmlev
    
    self._GLON = inlon
    self._GLAT = inlat
    self._GLEV = inlev
    self._GMLEV = inmlev
    return self._GLON, self._GLAT, self._GLEV, self._GMLEV

  def get_availble_varlists_and_timesteps(self, show=False):
    varlist = self.VARINFO.keys()

    hstr = self.VARINFO['lon']['htypes'][0]
    pattern = os.path.join(self.EXPDIR, "**", f"*.cam.{hstr}.*.nc")
    h1_files = glob.glob(pattern, recursive=True)
    sorted(h1_files)
    # first file
    filename = os.path.basename(h1_files[0])
    sdate = re.search(r'\.(\d{4}-\d{2}-\d{2}-\d{5})\.nc$', filename).group(1)
    filename = os.path.basename(h1_files[-1])
    edate = re.search(r'\.(\d{4}-\d{2}-\d{2}-\d{5})\.nc$', filename).group(1)
    nfiles = len(h1_files)
    if show:
      print(f'------ available variables ------')
      for key in varlist:
          print(key, self.VARINFO[key]['htypes'][0])
    if show:
      print(f'------ available date : {sdate} to {edate} ({nfiles} files)------')
    return varlist, nfiles

  def read_single_data_data(self, var, nowtime):
    hstr = sorted(self.VARINFO[var]['htypes'])[0]
    it   = int((nowtime-datetime(nowtime.year, nowtime.month, nowtime.day)).total_seconds()/3600)
    #print(it)
    fname = self._gen_fname(nowtime, hstr)
    if not os.path.isfile(fname) or var not in self.VARINFO.keys():
      _ = self.get_availble_varlists_and_timesteps(True)
      print('ERROR !! can not find the file')
      print('please check the available timestep and variable name ... ')
      sys.exit()
    
    vartype = self.VARINFO[var]['dims'][0]
    if vartype=='3d':
      nc    = Dataset(fname,'r')
      data  = nc.variables[var][it,:,\
                        self._SUBIDX[2]:self._SUBIDX[3],\
                        self._SUBIDX[0]:self._SUBIDX[1]]
      # if pressure:
      #     # do interpolate in pressure levels.
      #     continue
    elif vartype=='2d':
      nc = Dataset(fname,'r')
      data = nc.variables[var][it,\
                        self._SUBIDX[2]:self._SUBIDX[3],\
                        self._SUBIDX[0]:self._SUBIDX[1]]
    return data

  def get_data(self, nt, var, stime=None, mean=None):

    # prepare time interval for mean range
    if type(mean)==type(None):
      interval_dt = timedelta(hours=1)
    elif mean=='hourly':
      interval_dt = timedelta(hours=1)
    elif mean=='daily':
      interval_dt = timedelta(days=1)
    elif type(mean)==type(timedelta(hours=1)):
      interval_dt = mean

    # get interval_nt and check Divisible
    interval_data = timedelta(hours=1)
    interval_nt = interval_dt/interval_data
    if ( np.abs(interval_nt - int(interval_nt)) >= 1e-4 ):
      sys.exit(f'get_data ERROR: cant divisible when mean data ({interval_nt})')
    interval_nt = int( interval_nt)
   
    #print(mean, interval_dt, interval_nt)
    # create ens initiation time
    enstime = datetime.strptime(self.ENS, '%Y%m%d%H')

    # set and check start time 
    stime = stime or enstime
    if stime < enstime:
      print('get_data ERROR, the start_time need to be later than ens_start time')
      print('please checke the start time input and the ens case')
      sys.exit()

    vartype = self.VARINFO[var]['dims'][0]
    # start to read 
    shape = self.read_single_data_data(var, stime).shape
    time_series = [] 
    data_series = []
    for it in range(nt):
      nowtime = stime + it * interval_dt
      data = np.zeros(shape)
      for isub in range(interval_nt):
        subtime = nowtime + isub * interval_data
        ii = int((subtime - enstime).total_seconds() // interval_data.seconds)
        dum = self.read_single_data_data(var, subtime)
        data += dum / interval_nt

      time_series.append(nowtime)
      data_series.append(data)
    return time_series, np.squeeze(np.array(data_series))


if __name__=='__main__':
  fdir  = '/data/C.shaoyu/TaiESM/archive/'
  exp   = 'f02.F2000.hindcast'
  reg   = [100, 180, -10, 45, 1000, 500]
  esm   =  TaiESMRetriever(fdir, exp, reg, iens=0)

  print('hourly test ...')
  # get hourly data
  esm.set_ens(18)
  tseries_1hr, data_1hr = esm.get_data(nt=10, var='U', stime=datetime(2016,8,25), mean=None)

  print('daily test ...')
  esm.set_ens(2)
  # get daily data (2 days, daily mean)
  tseries_daily, data_daily = esm.get_data(nt=2, var='TMQ', mean='daily')

  # get customized range (4 hour)
  esm.set_ens(18)
  tseries_cu, data_cu = esm.get_data(nt=6, var='PRECT', stime=datetime(2016,8,25), mean=timedelta(hours=4))
  sys.exit()


