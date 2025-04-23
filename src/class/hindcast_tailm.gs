'reinit'
'set background 1'
'c'

figpath='./fig_hindcast/talim/'
'! mkdir -p 'figpath

'sdfopen /work1/umbrella0c/data/imerg/imerg_daily_201709.nc'
'sdfopen /work1/umbrella0c/data/era5/SFC/ERA5_SFC_msl_201709_r1440x721_day.nc'

*** color map setting ***
clevs=' 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1 2 3 5 7'
ccols='(255,255,255)->deepskyblue->blue->mediumslateblue->blueviolet'


dd=7
while(dd<=14)

'c'
'set time 00z'dd'sep2017'
cdd=math_format( '%02.0f', dd )

***** set domain ****
lonrange='105 150'
latrange='0 40'
*lonrange='90 150'
*latrange='-10 50'
'set lon 'lonrange
'set lat 'latrange

***** figure setting *****
'set parea 1 10 1 7.5'
'set xlopts 1 10 0.2'
'set ylopts 1 10 0.2'
'set grads off'
'set timelab off'
'set xlint 10'
'set ylint 10'

'set lwid 47 3.5'
'set rgb 40 0 110 40'
'set mpt 1 12 1 47'


***** obs ***
*X Limits = 2.45313 to 8.54688
*Y Limits = 1 to 7.5

'define mrain=rain.1(t='dd')'
'color -levs 'clevs' -kind 'ccols' -gxout shaded'
'set rgb 30 250 0 153'
'd mrain'
'xcbar 8.7 9 1 6 -ft 10 -fs 1 -fw 0.2 -fh 0.2'

'set string 1 bl 10 0'
'set strsiz 0.15'
'draw string 8.7 6.1 [mm/hr]'


'set gxout contour'
'set cmax 2000' 
'set cmin 850'
'set cint 2'
'set clopts -1 5 0.15'
'set cthick 5'
'set clab masked'
'define mslp=msl.2(t='dd')/100.'
*'d lterp(mslp,psl.3(t=1))'
'd mslp'

'q time'
tstr=subwrd(result,3)
tstr=substr(tstr,4,100)
say tstr
'set string 1 bl 10 0'
'set strsiz 0.25'
'draw string 2.45313 7.9 ERA5/IMERG'
'set string 1 bl 5 0'
'set strsiz 0.15'
'draw string 2.45313 7.6 mslp[hPa]/rain[mm hr`a-1`n]'

'set string 1 br 10 0'
'set strsiz 0.25'
'draw string  8.54688 7.6 'tstr

'gxprint 'figpath'/obs_hres_09'cdd'.png x1600 y1200 white'

pull c
dd=dd+1
endwhile

exit
