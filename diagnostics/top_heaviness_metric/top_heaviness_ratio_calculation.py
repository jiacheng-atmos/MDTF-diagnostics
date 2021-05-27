# 26 May top_heaviness_ratio_calculation.py
#Python packages/ modules imported for the diagnostic
# the sample monthly data is from ERA5 in July from 2000 to 2019 
import os
import xarray as xr
import numpy as np
from scipy import integrate
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


#Setting variables equal to environment variables set by the diagnostic
lat_coord = os.environ["lat_coord"]
lon_coord = os.environ["lon_coord"]
lev_coord = os.environ["lev_coord"]
omega_var = os.environ["omega_var"] 


def top_heaviness_ratio_calculation(reanalysis_path, reanalysis_var):
    # read omega and land-sea fraction data
    ds= xr.open_dataset(reanalysis_path)
    lev_obs=ds[lev_coord].values
    lat_obs=ds[lat_coord].values
    lon_obs=ds[lon_coord].values
    isort=np.argsort(lev_obs)[::-1] # descending
    mid_omega_obs=ds[reanalysis_var].values # mon x lev x lat x lon; for the sample data (July over 2000-2019) 
    mid_omega_obs=mid_omega_obs[:,isort]
    #======================deriving O1 and O2=======================
    # construct Q1_obs as half a sine wave and Q2_obs as a full sine wave
    # two base functions; Q1: idealized deep convection profile; Q2: Deep stratiform profile (Back et al. 2017)
    Q1_obs=np.zeros(len(lev_obs))
    Q2_obs=np.zeros(len(lev_obs))
    dp=lev_obs[-1]-lev_obs[0]
    for i in range(len(lev_obs)):
        Q1_obs[i]=-np.sin(np.pi*(lev_obs[i]-lev_obs[0])/dp)
        Q2_obs[i]=np.sin(2*np.pi*(lev_obs[i]-lev_obs[0])/dp)
    #Normalize 
    factor=integrate.trapz(Q1_obs*Q1_obs,lev_obs)/dp
    Q1_obs=Q1_obs/np.sqrt(factor)
    factor=integrate.trapz(Q2_obs*Q2_obs,lev_obs)/dp
    Q2_obs=Q2_obs/np.sqrt(factor)
    # deriving O1 and O2; O1 and O2 are coefs of Q1 and Q2
    mid_omega_obs_ltm=np.nanmean(mid_omega_obs,axis=0)
    O1_obs=integrate.trapz(mid_omega_obs_ltm*Q1_obs[:,None,None],lev_obs,axis=0)/dp
    O2_obs=integrate.trapz(mid_omega_obs_ltm*Q2_obs[:,None,None],lev_obs,axis=0)/dp
    #====================== set up figures =======================
    #====================== O1 =======================
    fig, axes = plt.subplots(figsize=(8,4))
    ilat=np.argsort(lat_obs)
    ilon=np.argsort(lon_obs)
    x,y = np.meshgrid(lon_obs,lat_obs) 
    m = Basemap(projection="cyl",llcrnrlat=lat_obs[ilat][0],urcrnrlat=lat_obs[ilat][-1],\
            llcrnrlon=lon_obs[ilon][0],urcrnrlon=lon_obs[ilon][-1],ax=axes,resolution='c')
    m.drawcoastlines(linewidth=1, color="k")
    m.drawparallels(np.arange(lat_obs[ilat][0],lat_obs[ilat][-1],30),labels=[1,0,0,0],linewidth=0.,fontsize=16)
    m.drawmeridians(np.arange(lon_obs[ilon][0],lon_obs[ilon][-1],60),labels=[0,0,0,1],linewidth=0.,fontsize=16)
    X,Y = m(x,y)
    clevs=np.arange(-0.06,0.07,0.01)
    im0 = m.contourf(X,Y,O1_obs,clevs,cmap = plt.get_cmap('RdBu_r'),extend='both')
    cbar = fig.colorbar(im0, ax=axes, orientation="horizontal", pad=0.15,shrink=.9,aspect=45)
    axes.set_title('O1 [Pa/s]',loc='center',fontsize=16)
    fig.tight_layout() 
    fig = fig.savefig("{WK_DIR}/model/Long term mean of O1.png", format='png',bbox_inches='tight')
    #====================== O2 =======================
    fig, axes = plt.subplots(figsize=(8,4))
    x,y = np.meshgrid(lon_obs,lat_obs) 
    m = Basemap(projection="cyl",llcrnrlat=lat_obs[ilat][0],urcrnrlat=lat_obs[ilat][-1],\
            llcrnrlon=lon_obs[ilon][0],urcrnrlon=lon_obs[ilon][-1],ax=axes,resolution='c')
    m.drawcoastlines(linewidth=1, color="k")
    m.drawparallels(np.arange(lat_obs[ilat][0],lat_obs[ilat][-1],30),labels=[1,0,0,0],linewidth=0.,fontsize=16)
    m.drawmeridians(np.arange(lon_obs[ilon][0],lon_obs[ilon][-1],60),labels=[0,0,0,1],linewidth=0.,fontsize=16)
    X,Y = m(x,y)
    clevs=np.arange(-0.06,0.07,0.01)
    im0 = m.contourf(X,Y,O2_obs,clevs,cmap = plt.get_cmap('RdBu_r'),extend='both') 
    cbar = fig.colorbar(im0, ax=axes, orientation="horizontal", pad=0.15,shrink=.9,aspect=45)
    axes.set_title('O2 [Pa/s]',loc='center',fontsize=16)
    fig.tight_layout()
    fig = fig.savefig("{WK_DIR}/model/Long term mean of O2.png", format='png',bbox_inches='tight')    
    #====================== O2/O1 top-heaviness ratio =======================
    fig, axes = plt.subplots(figsize=(8,4))
    mmid1=O2_obs/O1_obs
    midi=O1_obs<0.01   # We only investigate areas with O1 larger than zero
    mmid1[midi]=np.nan
    x,y = np.meshgrid(lon_obs,lat_obs)
    m = Basemap(projection="cyl",llcrnrlat=lat_obs[ilat][0],urcrnrlat=lat_obs[ilat][-1],\
            llcrnrlon=lon_obs[ilon][0],urcrnrlon=lon_obs[ilon][-1],ax=axes,resolution='c')
    m.drawcoastlines(linewidth=1, color="k")
    m.drawparallels(np.arange(lat_obs[ilat][0],lat_obs[ilat][-1],30),labels=[1,0,0,0],linewidth=0.,fontsize=16)
    m.drawmeridians(np.arange(lon_obs[ilon][0],lon_obs[ilon][-1],60),labels=[0,0,0,1],linewidth=0.,fontsize=16)
    X,Y = m(x,y)
    clevs=np.arange(-0.6,0.7,0.1)
    im0 = m.contourf(X,Y,mmid1,clevs,cmap = plt.get_cmap('RdBu_r'),extend='both') 
    cbar = fig.colorbar(im0, ax=axes, orientation="horizontal", pad=0.15,shrink=.9,aspect=45)
    axes.set_title('Top-heaviness Ratio (O2/O1)',loc='center',fontsize=18)
    fig = fig.savefig("{WK_DIR}/model/Top-Heaviness Ratio.png", format='png',bbox_inches='tight') 
    
    print("Plotting Completed")
        

top_heaviness_ratio_calculation(os.environ["OMEGA_FILE"],os.environ["omega_var"])
