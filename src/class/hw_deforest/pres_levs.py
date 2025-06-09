import numpy as np
import sys, os 
sys.path.insert(0, '../')
import utils.vinth2p as vint
import glob
from netCDF4 import Dataset


#dpath = '/work1/umbrella0c/taiesm_work/archive/f09_B1850TAI_BC2000/atm/'
#fpath = os.path.join(dpath,'hist',"f09_B1850TAI_BC2000.cam.h0.0001-01.nc")
exp = 'f09.F2000_MCDEF'
exp = 'f09.F2000_TAI_CTR'
dpath = f'./{exp}/*.nc'
flist = glob.glob(dpath)
# fname = f'./newnc.nc'
# os.system(f'rm -rf {fname}')
os.system(f'mkdir -p ./pres/{exp}')
for i in range(len(flist)):
    fpath   = flist[i]
    print(fpath)
    nc_h0   = Dataset(fpath,'r')
    lon      = nc_h0.variables['lon'][:]
    lat      = nc_h0.variables['lat'][:]
    lev      = nc_h0.variables['lev'][:]

    fname  = f'./pres/{exp}/pres_'+fpath.split('.')[-2]+'.nc'
    nc_out = vint.create_nc_from_h0(nc_h0, fname)
    for varname in ['U', 'V', 'T', 'Q', 'Z3', 'OMEGA']:
        print(varname)
        var_nc  = vint.regrid_and_save_variables(varname, nc_h0, nc_h0, nc_out)
    nc_out.close()
sys.exit()

