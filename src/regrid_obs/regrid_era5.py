import numpy as np
import numpy as np
import sys, os
sys.path.insert(0, '../')
import utils.era5  as uera5
import utils.imerg as uimg
import utils.taiesm as utai
from datetime import datetime, timedelta
from netCDF4  import Dataset, date2num
from scipy.interpolate import RegularGridInterpolator
import multiprocessing



stime = datetime(2016,8,1)
lonb  = [0, 360.0001]
latb  = [-90, 90.0001]

nhr = int((datetime(2016,11,1)-stime).total_seconds()/3600)
nday = int((datetime(2016,11,1)-stime).total_seconds()/86400)
tunits = 'hourly'

# read era5 dataset 
fdir  = '/data/C.shaoyu/data/era5/cwbgfs_hourly/'
reg   = lonb+latb+[850,300]
era5 = uera5.Era5Retriever(fdir, stime, reg)
ilev_850 = np.argmin(np.abs(era5.LEV-850))
ilev_300 = np.argmin(np.abs(era5.LEV-300))

fdir  = '/data/C.shaoyu/ESM2025/data/imerg/all_rename'
reg   = lonb+latb
imerg = uimg.ImergRetriever(fdir, stime, reg)

# read taiesm
fdir  = '/data/C.shaoyu/TaiESM/archive/'
exp   = 'f02.F2000.hindcast'
reg   = lonb+latb+[850,300]
tai   = utai.TaiESMRetriever(fdir, exp, reg, iens=0)
nc_tai = Dataset('/data/C.shaoyu/TaiESM/archive/f02.F2000.hindcast_2016080200/atm/hist/f02.F2000.hindcast_2016080200.cam.h1.2016-08-02-00000.nc', 'r')

def create_nc_file(fname, times, levels, lats, lons):
    ncfile = Dataset(fname, mode="w", format="NETCDF4_CLASSIC")
    # -------------------------
    # Define dimensions
    # -------------------------
    ncfile.createDimension("time", None)
    ncfile.createDimension("level", levels.size)
    ncfile.createDimension("lat", lats.size)
    ncfile.createDimension("lon", lons.size)

    # -------------------------
    # Define coordinate variables
    # -------------------------
    time_var = ncfile.createVariable("time", "f8", ("time",))
    time_var.units = "hours since 1970-01-01 00:00:00"
    time_var.calendar = "gregorian"
    time_var.standard_name = "time"
    time_var.long_name = "Time"
    time_var[:] = date2num(times, units=time_var.units, calendar=time_var.calendar)
    
    level_var = ncfile.createVariable("level", "f4", ("level",))
    level_var.units = "hPa"
    level_var.positive = "down"
    level_var.standard_name = "air_pressure"
    level_var.long_name = "Pressure Level"
    level_var[:] = levels
    
    lat_var = ncfile.createVariable("lat", "f4", ("lat",))
    lat_var.units = "degrees_north"
    lat_var.standard_name = "latitude"
    lat_var.long_name = "Latitude"
    lat_var[:] = lats
    
    lon_var = ncfile.createVariable("lon", "f4", ("lon",))
    lon_var.units = "degrees_east"
    lon_var.standard_name = "longitude"
    lon_var.long_name = "Longitude"
    lon_var[:] = lons
    return ncfile

def input_nc_var(ncfile, data, ndim, varname, **attrs):
    if ndim==4:
        dim=("time", "level", "lat", "lon")
    elif ndim==3:
        dim=("time", "lat", "lon")
    var = ncfile.createVariable(
        varname,
        "f4",
        dim,
        zlib=True,           # Enable compression
        complevel=4,         # Optional: compression level (1–9)
        #shuffle=True         # Optional: improves compression
    )
    for key, value in attrs.items():
        setattr(var, key, value)
    if data is not None:
        var[:] = data
    return var

def regrid_func(src_grid, re_grid, src_data):
  # ===== interpolate data (era5 and imerg)
  # 0: lat, 1:lon
  lon2, lat2 = np.meshgrid(re_grid[1], re_grid[0])

  dim = src_data.shape
  if len(dim)==3:
    nt=dim[0]
    nz=1
    outdata = np.zeros((nt,re_grid[0].size,re_grid[1].size))
    for it in range(dim[0]):
      interp = RegularGridInterpolator(src_grid, src_data[it,...], bounds_error=False)
      outdata[it] = interp((lat2, lon2))
  if len(dim)==4:
    nt=dim[0]
    nz=dim[1]
    outdata = np.zeros((nt,nz,re_grid[0].size,re_grid[1].size))
    for it in range(dim[0]):
      for iz in range(dim[1]):
        interp = RegularGridInterpolator(src_grid, src_data[it,iz,...], bounds_error=False, fill_value = None)
        outdata[it,iz] = interp((lat2, lon2))
  return outdata

## 
outdir='/data/C.shaoyu/ESM2025/data/obs_taigrid'
os.system(f'! mkdir -p {outdir}')

def main(idy):
    nowdate = stime+timedelta(days=idy)
    print(idy, nowdate)
    nowdate_str = nowdate.strftime('%Y-%m-%d')

    fname=f'{outdir}/obs_f02_{nowdate_str}.nc'
    times = [nowdate + timedelta(hours=i) for i in range(24)]

    # ----- nc -----
    fdir  = '/data/C.shaoyu/data/era5/cwbgfs_hourly/'
    reg   = lonb+latb+[850,300]
    era5 = uera5.Era5Retriever(fdir, nowdate, reg)
    ncfile = create_nc_file(fname,times,era5.LEV,tai.LAT,tai.LON)
    re_grid   = [tai.LAT, tai.LON]


    # ----- nc - era5 -----
    src_grid  = [era5.LAT,  era5.LON]
    
    # read era5 dataset 
    fdir  = '/data/C.shaoyu/data/era5/cwbgfs_hourly/'

    for lev in [850, 300]:
        for var in ['u', 'v']:
            print(var, lev)
            reg   = lonb+latb+[lev,lev]
            era5 = uera5.Era5Retriever(fdir, nowdate, reg)
            tseries, data = era5.get_data(24, f'{var}', stime=nowdate)
            redata = regrid_func(src_grid, re_grid, data)
            ncvar  = input_nc_var(ncfile, redata, 3, f'{var.upper()}{lev}')


    # ----- nc - rain -----
    src_grid  = [imerg.LAT,  imerg.LON]
    tseries, data = imerg.get_data(nt=24, stime=nowdate, mean='hourly')
    data = np.where(data<0,0,data)
    redata = regrid_func(src_grid, re_grid, data)
    ncvar  = input_nc_var(ncfile, redata, 3, 'rain')
    ncfile.close()


#for idy in range(nday):
# Use multiprocessing to fetch variable data in parallel
with multiprocessing.Pool(processes=5) as pool:
    results = pool.starmap(main, [(iday,) for iday in range(nday)])

