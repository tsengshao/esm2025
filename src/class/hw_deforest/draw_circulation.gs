'reinit'
'set background 1'
'c'

exp='deforest'
'xdfopen pres_f09_'exp'.ctl'


'set t 12 14'
'set x 1 228'
'set y 1 192'
'set z 1 27'
'define w=-1*omega*287*t*(1+0.61*q)/lev/9.8'

'set lat -30 60'

lonrange="lon=90,lon=160"
'set lon 120'
'set z 1 27'
'set t 12 14'
'define vmean=ave(v,'lonrange')'
'define wmean=ave(w,'lonrange')'

'set t 12'
trange='t=12, t=14'
'define vdraw=ave(vmean,'trange')'
'define wdraw=ave(wmean,'trange')'

***** figure setting *****
'set parea 1 10 1.5 7.5'
'set xlopts 1 10 0.2'
'set ylopts 1 10 0.2'
'set grads off'
'set timelab off'

'set yflip on'
'color -10 10 -gxout grfill'
'd vdraw'
'set gxout contour'
'set cthick 10'
'set clevs -0.5 0.5'
'd wdraw'
'cbar'

'draw title 'exp'(f09), DJF_mean, 'lonrange
'printim circulation_DJF_'exp'.png'




