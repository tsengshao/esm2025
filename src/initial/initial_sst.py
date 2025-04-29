import numpy as np
import numba
import xarray as xr
import sys, os
from netCDF4 import Dataset
from datetime import datetime, timedelta

sourcefile='/work1/j07hcl00/inidata/OISST_BC/sst_OISST-V2_bc_0.23x0.31_20150101-20250101_c250401.nc'
outpath='../../data/sst_initial'
outfile=f'{outpath}/sst_p3k_OISST-V2_bc_0.23x0.31_20150101-20250101_c250401.nc'

os.system(f'mkdir -p {outpath}')
#os.system(f'rsync -avh {sourcefile} {outfile} --progress')

ref  = Dataset(sourcefile, mode='r')
save = Dataset(outfile, mode='r+')
nt   = ref.variables['time'].size
#for i in range(ref.variables['time'].size):
for i in range(nt):
    print(f'{i} / {nt}')
    for varn in ['SST_cpl', 'SST_cpl_prediddle']:
        refvar  =  ref.variables[varn]
        savevar = save.variables[varn]
        print(f'[pre] {varn} ...', refvar[i,:].min(), refvar[i,:].max())
        savevar[i,:]  = np.where(refvar[i,:]>0, refvar[i,:] + 3., refvar[i,:])
        print(f'[p3k] {varn} ...', savevar[i,:].min(), savevar[i,:].max())
    print(' ')
ref.close()
save.close()

sys.exit()
