import numpy as np
import numpy as np
import sys, os
sys.path.insert(0, '../')
from datetime import datetime, timedelta
from netCDF4  import Dataset, date2num
import multiprocessing

stime = datetime(2016,8,1)
lonb  = [0, 360.0001]
latb  = [-90, 90.0001]

nhr = int((datetime(2016,11,1)-stime).total_seconds()/3600)
nday = int((datetime(2016,11,1)-stime).total_seconds()/86400)
tunits = 'hourly'

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

## 
outdir='/data/C.shaoyu/ESM2025/data/obs_taigrid/merge'
os.system(f'! mkdir -p {outdir}')

## open a file to get coordinate
nc = Dataset('/data/C.shaoyu/ESM2025/data/obs_taigrid/processing/ERA5_f02_v_2016103114_hourly.nc', 'r')
levels = nc.variables['pressure_level'][:]
lons   = nc.variables['lon'][:]
lats   = nc.variables['lat'][:]

def main(idy):
    nowdate = stime+timedelta(days=idy)
    print(idy, nowdate)
    nowdate_str = nowdate.strftime('%Y-%m-%d')

    fname=f'{outdir}/obs_f02_{nowdate_str}.nc'
    times = [nowdate + timedelta(hours=i) for i in range(24)]

    # ----- nc -----
    ncfile = create_nc_file(fname,times,levels,lats,lons)

    # read u
    fdir = '/data/C.shaoyu/ESM2025/data/obs_taigrid/processing'
    for var in ['u','v','t','q']:
        out = np.zeros((24,levels.size,lats.size,lons.size))
        ncvar  = input_nc_var(ncfile, None, 4, var)
        for it in range(len(times)):
            print(var, it)
            nowtime = nowdate+timedelta(hours=it)
            tstr = nowtime.strftime('%Y%m%d%H')
            nc = Dataset(fdir+f'/ERA5_f02_{var}_{tstr}_hourly.nc')
            out[it,...] = nc.variables[var][0,...]
            nc.close()
        ncvar[:] = out

    # read cwv
    fdir = '/data/C.shaoyu/ESM2025/data/obs_taigrid/processing'
    for var in ['mslp']:
        if var=='cwv':
            var_src='tp'
            var_out='tmq'
        elif var=='mslp':
            var_src='msl'
            var_out='psl'
        out = np.zeros((24,lats.size,lons.size))
        ncvar  = input_nc_var(ncfile, None, 3, var_out)
        for it in range(len(times)):
            print(var, it)
            nowtime = nowdate+timedelta(hours=it)
            tstr = nowtime.strftime('%Y%m%d%H')
            nc = Dataset(fdir+f'/ERA5_f02_{var}_{tstr}_hourly.nc')
            out[it, ...] = nc.variables[var_src][0,...]
            nc.close()
        ncvar[:] = out

    # read rain
    fdir = '/data/C.shaoyu/ESM2025/data/obs_taigrid/wind_rain'
    tstr = nowtime.strftime('%Y-%m-%d')
    nc = Dataset(fdir+f'/obs_f02_{tstr}.nc')
    for var in nc.variables.keys():
        if var in ['time', 'lon', 'lat', 'level']:
            continue
        print(var)
        data   = nc.variables[var][:]
        ncvar  = input_nc_var(ncfile, data, 3, var.lower())
    nc.close()

    # read sst
    print('sst')
    fname = '/data/C.shaoyu/ESM2025/data/obs_taigrid/'+\
            'oisst_f02_2016autumn_daily.nc'
    nc = Dataset(fname)
    it = (nowdate-datetime(2016,8,1)).total_seconds()/86400
    out = np.zeros((24,lats.size,lons.size))
    data   = nc.variables['SST_cpl'][it,...]
    nc.close()

    for i in range(24):
        out[i,...] = data
    ncvar  = input_nc_var(ncfile, data, 3, 'sst')

    ncfile.close()

#for idy in range(nday):
# for idy in range(1):
#     main(idy)
# Use multiprocessing to fetch variable data in parallel
with multiprocessing.Pool(processes=5) as pool:
    results = pool.starmap(main, [(iday,) for iday in range(nday)])

