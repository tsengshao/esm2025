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

## python vintp.py daily f02 2016080507 "/data/C.shaoyu/ESM2025/src/initial/ref_file" "./initial" "/data/C.shaoyu/ESM2025/data/initial"
dataset    = sys.argv[1] #daily, hourly
res        = sys.argv[2] #f09, f02
yyyymmddhh = sys.argv[3] #yyyymmddhh, 2016080100
refpath    = sys.argv[4] #"/data/C.shaoyu/ESM2025/src/initial/ref_file"
inpath     = sys.argv[5] #"./initial"
outpath    = sys.argv[6] #"/data/C.shaoyu/ESM2025/data/initial/"

ofile_fmt  = f'{inpath}/ERA5_{res}_{{varname}}_{yyyymmddhh}_{dataset}.nc'
outpath    = f'{outpath}/ERA5_{res}/{yyyymmddhh[:6]}'
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
ref = xr.open_dataset(ref_ncfname)
hyam = ref.hyam
hybm = ref.hybm
P0 = ref.P0

sp = xr.open_dataset(ofile_fmt.format(varname='sp')).sp
spslat = xr.open_dataset(ofile_fmt.format(varname='spslat')).sp
spslon = xr.open_dataset(ofile_fmt.format(varname='spslon')).sp
us = xr.open_dataset(ofile_fmt.format(varname='uslat')).u
vs = xr.open_dataset(ofile_fmt.format(varname='vslon')).v
t  = xr.open_dataset(ofile_fmt.format(varname='t')).t
q  = xr.open_dataset(ofile_fmt.format(varname='q')).q


pres_era5_1d = xr.open_dataset(ofile_fmt.format(varname='q')).level.values*100.
pres_cam = (hyam * P0 + hybm * sp).transpose('time', ...).values

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

encoding = {var: {'_FillValue': None} for var in ref.variables}
ref.to_netcdf(out_ncfname,
        encoding=encoding,
        format="NETCDF3_CLASSIC")
