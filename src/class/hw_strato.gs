'reinit'
'set background 1'
'c'

***/work1/umbrella0c/taiesm_work/archive/f09.F2000.ESMclass.EAstrat/atm/hist_h1.ctl
case='f09.F2000.ESMclass.EAstrat'
apath='/work1/umbrella0c/taiesm_work/archive/'case'/atm/'
'xdfopen 'apath'/hist_h1.ctl'
'xdfopen 'apath'/pres_h1.ctl'

figpath='./fig_strato/'
'! mkdir -p 'figpath

***** set domain ****
lonrange='90 150'
latrange='0 50'
'set lon 'lonrange
'set lat 'latrange

***** figure setting *****
'set parea 1 10 1 7.5'
'set xlopts 1 10 0.2'
'set ylopts 1 10 0.2'
'set grads off'
'set timelab off'

tstr='01z01JAN0001'
'set time 'tstr
****** NSS ******
'c'
'set xlint 10'
'set ylint 10'
'set grads off'
'color 0 20 2 -gxout grfill -kind grainbow '
'd maskout(nss.1, ocnfrac.1-0.5)'
'xcbar 9.1 9.4 1 7.5'

'set cthick 10'
'set arrscl 0.3 15'
'd skip(u.2(lev=950),3);v.2(lev=950)'
varn='NSS [K] & wind@950mb'
'draw title 'case'\'varn' /  'tstr
'gxprint 'figpath'/nss_'case'.png white'

pull c

****** LTS ******
'c'
'set xlint 10'
'set ylint 10'
'set grads off'
'color -15 15  2 -gxout grfill'
'd maskout(lts.1, ocnfrac.1-0.5)'
'xcbar 9.1 9.4 1 7.5'

'set cthick 10'
'set arrscl 0.3 15'
'd skip(u.2(lev=950),3);v.2(lev=950)'
varn='LTS [K] & wind@950mb'
'draw title 'case'\'varn' /  'tstr
'gxprint 'figpath'/lts_'case'.png white'

pull c

***********************
*** hovmoller ***
***********************
'c'
'set grads off'
'set dfile 2'
'set lon 121'
'set lat 25'
'set z 1 27'
'set t 1 '24*3
'set yflip on'
'color 0 10 1 -gxout grfill -kind tan->deepskyblue->blue->mediumblue'
'd q*1000'
'xcbar 10.2 10.4 1 7.5'

varn='Qv[g/kg] @(27N,121E)'
'draw title 'case'\'varn''
'gxprint 'figpath'/hov_'case'.png white'

