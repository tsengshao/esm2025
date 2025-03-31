'reinit'
'set background 1'
'c'

apath='/work1/umbrella0c/taiesm_work/archive/f09_B1850TAI_BC2000/atm/'
'xdfopen 'apath'/pres_h0.ctl'
'xdfopen 'apath'/hist_h0.ctl'
'xdfopen 'apath'/hist_h1.ctl'

figpath='./fig_aresol/'
'! mkdir -p 'figpath

***** figure setting *****
'set parea 1 10 1 7.5'
'set xlopts 1 10 0.2'
'set ylopts 1 10 0.2'
'set grads off'
'set timelab off'
*'set xlabs 0|288|576|864|1152'
*'set ylabs 0|288|576|864|1152'


averange='t=12,t=14'
'define fsnt=ave(fsnt.3,'averange')'
'define flnt=ave(flnt.3,'averange')'
'define sst=ave(sst.3,  'averange')'
'define u200=ave(u200.3,'averange')'

****** Net TOA imbalance ******
'c'
'set grads off'
'd fsnt - flnt'
varn='Net TOA imbalance [W/m2]'
'draw title 'varn' /  2`and`n DJF'
'gxprint 'figpath'/netTOA.png white'
pull c

***** SST surface wind
'c'
'set grads off'
'set gxout grfill'
'color 240 310 5 -gxout grfill -kind rainbow'
'd maskout(sst,sst-0.5)'
'cbar'
'set arrscl 0.1 5'
'd skip(u.1(lev=950),5);v.1'
varn='SST[K] + 950mb U[m/s]'
'draw title 'varn' /  2`and`n DJF'
'gxprint 'figpath'/sst_wind.png white'
pull c

***** 200hPa U
'c'
'set grads off'
'set gxout contour'
'd u.1(lev=200)'
varn='200mb U[m/s]'
'draw title 'varn' /  2`and`n DJF'
'gxprint 'figpath'/u200.png white'
pull c

***** zonal mean T + U
'c'
'set grads off'
'set parea 1 10 1.5 7.5'
averange='t=12,t=14'
'set x 1'
'set z 1 27'
'set t 12 14'
'define zu=ave(u,lon=0,lon=360)'
'define zt=ave(t,lon=0,lon=360)'
'set t 1'
'define djfzu=ave(zu,t=12,t=14)'
'define djfzt=ave(zt,t=12,t=14)'
'set yflip on'
'color 200 290 -gxout grfill -kind grainbow'
'd djfzt'
'cbar'
'set gxout contour'
'd djfzu'

varn='zonal mean U[m/s,contour]+T[K,shaded]'
'draw title 'varn' /  2`and`n DJF'
*'zonal mean U[m/s,contour]+T[K,shaded] / 2`and`n DJF'

'gxprint 'figpath'/zonalut.png white'




