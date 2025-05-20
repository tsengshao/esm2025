import matplotlib.pyplot as plt 
import matplotlib as mpl
import cartopy.mpl as cmpl
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt 
import matplotlib as mpl
import xarray as xr
import numpy as np


# Utilities
class PlotTools_cartopy():
    def __init__(self):
        return
 
    def get_region_boundary_and_interval(self,region_str):
        if region_str.lower()=='taiwan':
            lonb=[119.95, 122.05]
            latb=[21.85, 25.5]
            lonlint = 1
            latlint = 1
        if region_str.lower()=='tropics':
            lonb=[0, 359.999]
            latb=[-30, 30]
            lonlint = 60
            latlint = 10
        if region_str.lower()=='nwpac':
            lonb=[110, 180.00001]
            latb=[0, 40]
            lonlint = 20
            latlint = 10
        return lonb, latb, lonlint, latlint

    def create_fig(self, region_str):
        lonb, latb, lonlint, latlint = self.get_region_boundary_and_interval(region_str)
        xlen, ylen = lonb[-1]-lonb[0], latb[-1]-latb[0]
        ratio_xy   = ylen/xlen*1.2

        fig   = plt.figure(figsize=(8, ratio_xy*8))
        ax1   = self.Axe_map(fig, 111, xlim_=lonb, ylim_=latb,)
        ax1.set_extent(lonb+latb, crs=ccrs.PlateCarree())

        # Add specific gridlines
        gl = ax1.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.xlocator = plt.MultipleLocator(lonlint)   # every 60 degrees longitude
        gl.ylocator = plt.MultipleLocator(latlint)   # every 10 degrees latitude
        gl.xlabel_style = {'size': 16}
        gl.ylabel_style = {'size': 16}
        gl.top_labels = False
        gl.right_labels = False

        cax0  = fig.add_axes([ax1.get_position().x1+0.02, 
                              ax1.get_position().y0,
                              0.015,
                              ax1.get_position().height])
        cax1  = fig.add_axes([ax1.get_position().x1+0.1, 
                              ax1.get_position().y0,
                              0.015,
                              ax1.get_position().height])
        self.Plot_cartopy_map(ax1)
        return fig, ccrs.PlateCarree(), ax1, cax0, cax1

    def Axe_map(self, fig, gs,
                xlim_, ylim_, **grid_info):
        proj = ccrs.PlateCarree(central_longitude=np.mean(xlim_))
        # Set map extent
        axe  = fig.add_subplot(gs, projection=proj)
        axe.set_extent([xlim_[0], xlim_[-1], ylim_[0], ylim_[-1]], crs=proj)
        # Set additional grid information
        if len(grid_info)>0:
            if grid_info['xloc_'] is not None:
                axe.set_xticks(grid_info['xloc_'], crs=proj)
                #axe.set_xticklabels(['' for i in range(len(grid_info['xloc_']))])  # default: no tick labels
                axe.set_xticklabels([f'{int(i)}E' for i in grid_info['xloc_']],fontsize=16)
            if grid_info['yloc_'] is not None:
                axe.set_yticks(grid_info['yloc_'], crs=proj)
                #axe.set_yticklabels(['' for i in range(len(grid_info['yloc_']))])
                axe.set_yticklabels([f'{int(i)}N' for i in grid_info['yloc_']],fontsize=16)
            gl = axe.gridlines(xlocs=grid_info['xloc_'], ylocs=grid_info['yloc_'],
                               draw_labels=False)
        return axe

    def Plot_cartopy_map(self, axe):
        axe.add_feature(cfeature.LAND,color='grey',alpha=0.1)
        axe.coastlines(resolution='110m', color='black', linewidth=1)

    def get_cmap_of_pcp(self,bounds=[2, 5, 10, 15, 25]):
        # Define the level bounds
        #bounds = [2, 5, 10, 15, 25]
        
        # Colors:
        #  - First is for values < 2 (under)
        #  - Next 4 are for bins: [2-5), [5-10), [10-15), [15-25)
        #  - Last is for values >= 25 (over)
        rgba_colors = [
            (255, 255, 255, 0),    # under: transparent white
            (0, 84, 104, 255),     # [2–5)
            (11, 191, 38, 255),    # [5–10)
            (242, 226, 5, 255),    # [10–15)
            (242, 5, 5, 255),      # [15–25)
            (204, 7, 204, 255)     # over: magenta
        ]
        
        # Normalize RGBA (0–1 scale)
        rgba_colors = [(r/255, g/255, b/255, a/255) for r, g, b, a in rgba_colors]
        
        # Create colormap for middle bins (exclude under/over)
        cmap = mpl.colors.ListedColormap(rgba_colors[1:-1])
        
        # Set under and over colors
        cmap.set_under(rgba_colors[0])
        cmap.set_over(rgba_colors[-1])
        
        # Create norm
        norm = mpl.colors.BoundaryNorm(bounds, ncolors=len(rgba_colors), extend='max')
        return bounds, norm, cmap
        
