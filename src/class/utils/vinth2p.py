import Ngl
from netCDF4 import Dataset
import numpy as np
import os, sys
from datetime import datetime, timedelta

def create_nc_copy_dims(fname, src, in_members=['lon','lat','time']):
  # src is the netCDF.Dataset
  # fname is the string
  dst = Dataset(fname,'w')
  # copy global attributes all at once via dictionary
  dst.setncatts(src.__dict__)
  dst.history  = "Created " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  # copy dimensions
  for name, dimension in src.dimensions.items():
    if name not in in_members: continue
    size=len(dimension)
    dst.createDimension(
      name, (size if not dimension.isunlimited() else None))
  # copy all file data except for the excluded
  for name in src.dimensions.keys():
    if name not in in_members: continue
    variable = src.variables[name]
    data  = variable[:]
    x = dst.createVariable(name, variable.datatype, variable.dimensions)
    # copy variable attributes all at once via dictionary
    dst[name].setncatts(src[name].__dict__)
    dst[name][:] = data
  return dst

def add_dims_into_nc(dst, varn, var, dims, attrs):
    _ = dst.createDimension(varn, var.size)
    x = dst.createVariable(varn, 'f8', dims, fill_value=-999000000)
    x[:] = var
    x.setncatts(attrs)
    return x

def create_nc_from_h0(in_nc, fname):
    pnew = np.array([100, 125, 150, 175, 200, 225, \
                     250, 300, 350, 400, 450, 500, \
                     550, 600, 650, 700, 750, 775, \
                     800, 825, 850, 875, 900, 925, \
                     950, 975, 1000])[::-1]
    nc2 = create_nc_copy_dims(fname,in_nc)
    _   = add_dims_into_nc(nc2, 'lev', pnew, ('lev'), {'units':'millibars','positive':'up','axis':'Z'})
    nc2.variables['lon'].axis  = 'X'
    nc2.variables['lat'].axis  = 'Y'
    nc2.variables['time'].axis = 'T'
    return nc2

def nc_put_variables(ncfile, varname, data, attrs):
    if len(data.shape)==3:
      vardims = ('time', 'lat', 'lon')
      chunks  = (1, data.shape[1], data.shape[2])
    elif len(data.shape)==4:
      vardims = ('time', 'lev', 'lat', 'lon')
      chunks  = (1, 1, data.shape[2], data.shape[3])
    else:
      print('error data input shape, not 2d or 3d')
      return
    var_nc  = ncfile.createVariable(varname, 'f4', vardims,\
                                     compression='zlib', complevel=4,\
                                     fill_value=-999000000,\
                                     chunksizes=chunks,\
                                    )
    for name, value in attrs.items():
        setattr(var_nc, name, value)
    var_nc[:]  = data
    return var_nc

def regrid_and_save_variables(varname, nc_coord, nc_var, nc_out):
    hyam = nc_coord.variables['hyam'][:]
    hybm = nc_coord.variables['hybm'][:]
    psfc = nc_coord.variables['PS'][:]
    pnew = nc_out.variables['lev'][:]
    var     = nc_var.variables[varname]
    VARnew= Ngl.vinth2p(var[:],hyam,hybm,pnew,psfc,1,1000.,1,False)
    VARnew[VARnew>=1e30] = np.nan
    VARattrs = {attr: var.getncattr(attr) for attr in var.ncattrs()}
    var_nc = nc_put_variables(nc_out, varname, VARnew, VARattrs)
    return var_nc



if __name__=='__main__':
    dpath = '/work1/umbrella0c/taiesm_work/archive/f09_B1850TAI_BC2000/atm/'
    fpath = os.path.join(dpath,'hist',"f09_B1850TAI_BC2000.cam.h0.0001-01.nc")
    nc_h0   = Dataset(fpath,'r')
    lon      = nc_h0.variables['lon'][:]
    lat      = nc_h0.variables['lat'][:]
    lev      = nc_h0.variables['lev'][:]
    
    fname = f'./newnc.nc'
    os.system(f'rm -rf {fname}')
    nc_out = create_nc_from_h0(nc_h0, fname)
    for varname in ['U', 'V', 'T', 'Q', 'Z3', 'OMEGA']:
        print(varname)
        var_nc  = regrid_and_save_variables(varname, nc_h0, nc_h0, nc_out)
    nc_out.close()
    sys.exit()


"""
pressure = (hyam[np.newaxis,:,np.newaxis,np.newaxis]*100000. + \
            hybm[np.newaxis,:,np.newaxis,np.newaxis]*psfc[:,np.newaxis,:,:])/100.
U     = nc.variables['U'][:]
V     = nc.variables['V'][:]
T     = nc.variables['T'][:]
Q     = nc.variables['Q'][:]
OMEGA = nc.variables['OMEGA'][:]
Z3    = nc.variables['Z3'][:] # Geopotential Height (above sea level)
sys.exit()

#
#  Define the output pressure levels.
#
pnew = np.array([1000.,900.,800.,700.,600.,500.,400.,200.,100.])

#
#  Do the interpolation.
#
Tnew= Ngl.vinth2p(T,hyam,hybm,pnew,psfc,1,1000.,1,False)
Tnew[Tnew>=1e30] = np.nan

ntime, output_levels, nlat, nlon = Tnew.shape
print("vinth2p: shape of returned array   = [{:1d},{:1d},{:2d},{:3d}]".format(*Tnew.shape))
print("  number of timesteps     = {:4d}".format((ntime)))
print("  number of input levels  = {:4d}".format((T.shape[1])))
print("  number of output levels = {:4d}".format((output_levels)))
print("  number of latitudes     = {:4d}".format((nlat)))
print("  number of longitudes    = {:4d}".format((nlon)))


import matplotlib.pyplot as plt
plt.plot(T[0,:,75,100],pressure[0,:,75,100],label='raw')
plt.plot(Tnew[0,:,75,100],pnew,label='plev')
plt.legend()
sys.exit()

#
#  Uncomment the following to print out the resultant array values.
#
# for m in xrange(ntime):
#   for i in xrange(output_levels):
#     for j in xrange(nlat):
#       for k in xrange(nlon):
#         print("%3d%3d%3d%4d%12.5f" % (m,i,j,k,Tnew[m,i,j,k]))
"""
