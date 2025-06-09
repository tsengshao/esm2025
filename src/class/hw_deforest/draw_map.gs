'reinit'
'set background 1'
'c'
exp="control"
*exp="deforest"
'xdfopen f09_'exp'.ctl'


***** figure setting *****
'set parea 1 10 1 7.5'
'set xlopts 1 10 0.2'
'set ylopts 1 10 0.2'
'set grads off'
'set timelab off'

'set lon 80 180'
'set lat -20 20'
'define sh=ave(shflx,t=12,t=14)'
'define lh=ave(lhflx,t=12,t=14)'

'set gxout grfill'
'color 0 160 20 -gxout grfill -kind grainbow'
'd maskout(sh, ocnfrac<1)'
'cbar'
'draw title 'exp'(f09), DJF_mean, SH[W/m2]'
'printim SH_DJF_'exp'.png'
pull c

***** figure setting *****
'c'
'set parea 1 10 1 7.5'
'set xlopts 1 10 0.2'
'set ylopts 1 10 0.2'
'set grads off'
'set timelab off'

'set lon 80 180'
'set lat -20 20'
'define sh=ave(shflx,t=12,t=14)'
'define lh=ave(lhflx,t=12,t=14)'

'set gxout grfill'
'color 0 160 20 -gxout grfill -kind grainbow'
'd maskout(lh, ocnfrac<1)'
'cbar'
'draw title 'exp'(f09), DJF_mean, LH[W/m2]'
'printim LH_DJF_'exp'.png'

