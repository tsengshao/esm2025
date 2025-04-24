import numpy as np
import numba
import xarray as xr
import sys, os

@numba.njit(parallel=True)
def vintp(var, pres1d, plevs):
    s = var.shape # time, lev, lat, lon
    out = np.zeros((s[0],len(plevs[0,:,0,0]),s[2],s[3]))
    for t in numba.prange(s[0]):
        for j in range(s[2]):
            for i in range(s[3]):
                out[t,:,j,i] = np.interp(plevs[t,:,j,i], pres1d, var[t,:,j,i])
                out[t,:,j,i] = np.where(plevs[t,:,j,i] > pres1d[-1], np.nan, out[t,:,j,i])
    return out

## python vintp.py daily f02 2016080507 "/data/C.shaoyu/ESM2025/src/initial/ref_file" "./initial" 
## python vintp.py hourly f02 2016080507 "./ref_file" "/home/umbrella0c/data_wt/taiesm_initial"
print(sys.argv)
dataset    = sys.argv[1] #daily, hourly
res        = sys.argv[2] #f09, f02
yyyymmddhh = sys.argv[3] #yyyymmddhh, 2016080100
refpath    = sys.argv[4] #"/data/C.shaoyu/ESM2025/src/initial/ref_file"
filepath    = sys.argv[5] #"/data/C.shaoyu/ESM2025/data/initial/"

print(f'{dataset}\n{res}\n{yyyymmddhh}\n{refpath}\n{filepath}')

ofile_fmt  = f'{filepath}/processing/ERA5_{res}_{{varname}}_{yyyymmddhh}_{dataset}.nc'
outpath    = f'{filepath}/ERA5_{res}/{yyyymmddhh[:6]}'
os.makedirs(outpath, exist_ok=True)
out_ncfname = f'{outpath}/ERA5_{res}_{yyyymmddhh}_{dataset}_initial.nc'
print(out_ncfname)

## ---- prepare the reference netcdf file and read sigma levels
if res=='f09':
    ref_ncfname = f'{refpath}/cami-mam3_0000-01-01_0.9x1.25_L30_c100618.nc'
elif res=='f02':
    ref_ncfname = f'{refpath}/cami-mam3_0000-01-01_0.23x0.31_L30_c110527.nc'
else:
    print("please input correct resolution or prepare")
    print("the corrisponding resolution restartfile")
    sys.exit()

dum_fname=os.path.realpath(ref_ncfname)
os.system(f'rsync -avh {dum_fname} {out_ncfname}')
ref = xr.open_dataset(out_ncfname, engine='netcdf4', mode='r+')
hyam = ref.hyam
hybm = ref.hybm
P0 = ref.P0

if dataset=='hourly':
    tstr='valid_time'
    zstr='pressure_level'
elif dataset=='daily':
    tstr='time'
    zstr='level'
sp = xr.open_dataset(ofile_fmt.format(varname='sp')).sp
spslat = xr.open_dataset(ofile_fmt.format(varname='spslat')).sp
spslon = xr.open_dataset(ofile_fmt.format(varname='spslon')).sp
us = xr.open_dataset(ofile_fmt.format(varname='uslat')).u[:,::-1,:,:]
vs = xr.open_dataset(ofile_fmt.format(varname='vslon')).v[:,::-1,:,:]
t  = xr.open_dataset(ofile_fmt.format(varname='t')).t[:,::-1,:,:]
q  = xr.open_dataset(ofile_fmt.format(varname='q')).q[:,::-1,:,:]


pres_era5_1d = xr.open_dataset(ofile_fmt.format(varname='q'))[zstr].values*100.
pres_era5_1d = pres_era5_1d[::-1]
pres_cam = (hyam * P0 + hybm * sp).transpose(tstr, ...).values

us_np = vintp(us.values, pres_era5_1d, pres_cam)
vs_np = vintp(vs.values, pres_era5_1d, pres_cam)
t_np = vintp(t.values, pres_era5_1d, pres_cam)
q_np = vintp(q.values, pres_era5_1d, pres_cam)

ref.PS.data = sp.data
ref.US.data = us_np
ref.VS.data = vs_np
ref.T.data = t_np
ref.Q.data = q_np
# ref.CLDICE.data = 0.
# ref.CLDLIQ.data = 0.

print('start to write files')
encoding = {var: {'_FillValue': None, 'zlib':True} for var in ref.variables}
ref.to_netcdf(out_ncfname,
        mode='a',
        encoding=encoding,
        format="NETCDF4_CLASSIC")
