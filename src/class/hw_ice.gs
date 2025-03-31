'reinit'
'set background 1'
'c'

case='f09.F2000.ESMclass.ice_future'
case='f09.F2000.ESMclass.ice_preindustrial'
apath='/work1/umbrella0c/taiesm_work/archive/'case'/atm/'
'xdfopen 'apath'/hist_h0.ctl'
'xdfopen 'apath'/pres_h0.ctl'

figpath='./fig_ice/'
'! mkdir -p 'figpath

***** set domain ****
lonrange='80 180'
latrange='0 80'
'set lon 'lonrange
'set lat 'latrange

***** figure setting *****
'set parea 1 10 1 7.5'
'set xlopts 1 10 0.2'
'set ylopts 1 10 0.2'
'set grads off'
'set timelab off'

averange='t=9,t=11'
'define slpwin=ave(psl.1,'averange')/100.'
'define tswin=ave(ts.1,  'averange')'
'define t950=ave(t.2(lev=950),'averange')'
'define cwvwin=ave(tmq.1,'averange')'

****** mean sea level pressure ******
'c'
'set grads off'
'color 995 1040 5 -gxout grfill'
'd slpwin'
'xcbar 9.1 9.4 1 7.5'
varn='Mean sea level pressure [mb]'
'draw title 'case'\'varn' /  1`and`n DJF'
'gxprint 'figpath'/mslp_'case'.png white'

pull c
***** sourface temperature *****
'c'
'set grads off'
'set gxout grfill'
'color 220 310 5 -gxout grfill -kind grainbow'
'd tswin'
'xcbar 9.1 9.4 1 7.5'
varn='Surface Temperature [K]'
'draw title 'case'\'varn' /  1`and`n DJF'
'gxprint 'figpath'/ts_'case'.png white'
pull c

***** precipitable water *****
'c'
'set grads off'
'set gxout grfill'
'color -levs 1 2 3 4 5 10 15 20 25 30 40 50 -gxout grfill -kind grainbow'
'd maskout(cwvwin,cwvwin-1)'
'xcbar 9.1 9.4 1 7.5'
varn='Total precipitable water [mm]'
'draw title 'case'\'varn' /  1`and`n DJF'
'gxprint 'figpath'/cwv_'case'.png white'
pull c


***** T @950hPa *****
'c'
'set grads off'
'set gxout grfill'
'color 220 310 5 -gxout grfill -kind grainbow'
'd t950'
'xcbar 9.1 9.4 1 7.5'
varn='Air Temperature @950hPa [K]'
'draw title 'case'\'varn' /  1`and`n DJF'
'gxprint 'figpath'/t950_'case'.png white'
pull c

