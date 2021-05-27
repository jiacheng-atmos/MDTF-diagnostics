# 26 May top_heaviness_ratio_robustness_calc.py
import os
import xarray as xr
import numpy as np
import scipy 
from scipy import interpolate
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


#Setting variables equal to environment variables set by the diagnostic
time_coord = os.environ["time_coord"]
lat_coord = os.environ["lat_coord"]
lon_coord = os.environ["lon_coord"]
lev_coord = os.environ["lev_coord"]
omega_var = os.environ["omega_var"] 

#from numba import jit
#@jit(nopython=True)
def corr2d(a1,a2):
    ij=np.shape(a1[:])
    mid_corr=np.zeros(ij[1:])
    for i in np.arange(ij[1]):
        for j in np.arange(ij[2]):
            mid_corr[i,j]=np.corrcoef(a1[:,i,j],a2[:,i,j])[0,1]
    return mid_corr

def top_heaviness_ratio_robustness_calc(reanalysis_path, reanalysis_var):
    # read omega and land-sea fraction data
    ds= xr.open_dataset(reanalysis_path)
    lev_obs=ds[lev_coord].values
    lat_obs=ds[lat_coord].values
    lon_obs=ds[lon_coord].values
    isort=np.argsort(lev_coord)[::-1] # descending
    mid_omega_obs=ds[reanalysis_var].values # mon x lev x lat x lon; for the sample data (JAS over 2000-2019) 
    mid_omega_obs=mid_omega_obs[:,isort]
    #======================Interpolation=======================
    dp=lev_obs[-1]-lev_obs[0]
    levs_interp=np.linspace(lev_obs[0], lev_obs[-1], num=len(lev_obs))
    f=interpolate.interp1d(lev_obs, mid_omega_obs, kind='cubic', axis=1) # you can choose linear which consumes less time
    mid_omega_obs=f(levs_interp) 
    #======================deriving O1 and O2=======================
    # construct Q1_obs as half a sine wave and Q2_obs as a full sine wave
    # two base functions; Q1: idealized deep convection profile; Q2: Deep stratiform profile (Back et al. 2017)
    Q1_obs=np.zeros(len(levs_interp))
    Q2_obs=np.zeros(len(levs_interp))
    for i in range(len(levs_interp)):
        Q1_obs[i]=-np.sin(np.pi*(levs_interp[i]-levs_interp[0])/dp)
        Q2_obs[i]=np.sin(2*np.pi*(levs_interp[i]-levs_interp[0])/dp)
    #Normalize 
    factor=scipy.integrate.trapz(Q1_obs*Q1_obs,lev_obs)/dp
    Q1_obs=Q1_obs/np.sqrt(factor)
    factor=scipy.integrate.trapz(Q2_obs*Q2_obs,lev_obs)/dp
    Q2_obs=Q2_obs/np.sqrt(factor)
    #======================calculate explained variance over the globe=======================
    # Often times, the pres level is not equally distributed. People tend to increase density in the 
    # ... upper and lower atmopshere, leaving a less dense distribution in the mid atmosphere. 
    # ... Thus, it is important to weight Q1 and Q2 before we calculate explained variance
    # Remember, we already take weights into account when calculating O1 and O2
    mid_Q1_obs=Q1_obs/np.sqrt(np.sum(Q1_obs**2)) # unitize Q1
    mid_Q2_obs=Q2_obs/np.sqrt(np.sum(Q2_obs**2)) # unitize Q2
    OQ1_obs=np.nansum(mid_Q1_obs[None,:,None,None]*mid_omega_obs,axis=1)
    OQ2_obs=np.nansum(mid_Q2_obs[None,:,None,None]*mid_omega_obs,axis=1)
    total_variance_obs=np.nansum(np.nanvar(mid_omega_obs,axis=0),axis=0)
    Q1_explained_obs=np.nanvar(OQ1_obs,axis=0)
    Q2_explained_obs=np.nanvar(OQ2_obs,axis=0)
    total_explained_obs=Q1_explained_obs+Q2_explained_obs
    # calc ltm O1 and O2, because calculating correlation is not a linear operation
    mid_omega_obs_ltm=np.nanmean(mid_omega_obs,axis=0)
    OQ1_obs_ltm=np.nansum(mid_Q1_obs[:,None,None]*mid_omega_obs_ltm,axis=0)
    OQ2_obs_ltm=np.nansum(mid_Q2_obs[:,None,None]*mid_omega_obs_ltm,axis=0)
    OQQ1_obs=OQ1_obs_ltm[None,:,:]*mid_Q1_obs[:,None,None] # reconstruct Q1 field
    OQQ2_obs=OQ2_obs_ltm[None,:,:]*mid_Q2_obs[:,None,None] # reconstruct Q2 field
    OQQ_sum=OQQ1_obs+OQQ2_obs
    corr2d_obs=corr2d(mid_omega_obs_ltm,OQQ_sum)
    R2_obs=corr2d_obs**2
    #====================== setting up figures =======================
    ilat=np.argsort(lat_obs)
    ilon=np.argsort(lon_obs)
    #====================== R2 =======================
    # R2 measures the proportion of ltm omega profile explained by Q1 and Q2  
    fig, axes = plt.subplots(figsize=(8,4))
    mmid=R2_obs
    x,y = np.meshgrid(lon_obs,lat_obs) 
    m = Basemap(projection="cyl",llcrnrlat=lat_obs[ilat][0],urcrnrlat=lat_obs[ilat][-1],\
            llcrnrlon=lon_obs[ilon][0],urcrnrlon=lon_obs[ilon][-1],ax=axes,resolution='c')
    m.drawcoastlines(linewidth=1, color="k")
    m.drawparallels(np.arange(lat_obs[ilat][0],lat_obs[ilat][-1],30),labels=[1,0,0,0],linewidth=0.,fontsize=16)
    m.drawmeridians(np.arange(lon_obs[ilon][0],lon_obs[ilon][-1],60),labels=[0,0,0,1],linewidth=0.,fontsize=16)
    X,Y = m(x,y)
    clevs=np.arange(0,1.,0.1)
    im0 = m.contourf(X,Y,mmid,clevs,cmap = plt.get_cmap('RdBu_r'),extend='max') 
    cbar = fig.colorbar(im0, ax=axes, orientation="horizontal", pad=0.15,shrink=.9,aspect=45)
    axes.set_title('$R^{2}$ Between Recon. Omega & Original',loc='center',fontsize=18)
    fig = fig.savefig("{WK_DIR}/model/R2 Between Recon. Omega & Original.png", format='png',bbox_inches='tight')    
    #====================== explained interannual variance =======================
    fig, axes = plt.subplots(figsize=(8,4))
    mmid=(Q2_explained_obs+Q1_explained_obs)/total_variance_obs
    x,y = np.meshgrid(lon_obs,lat_obs) 
    m = Basemap(projection="cyl",llcrnrlat=lat_obs[ilat][0],urcrnrlat=lat_obs[ilat][-1],\
            llcrnrlon=lon_obs[ilon][0],urcrnrlon=lon_obs[ilon][-1],ax=axes,resolution='c')
    m.drawcoastlines(linewidth=1, color="k")
    m.drawparallels(np.arange(lat_obs[ilat][0],lat_obs[ilat][-1],30),labels=[1,0,0,0],linewidth=0.,fontsize=16)
    m.drawmeridians(np.arange(lon_obs[ilon][0],lon_obs[ilon][-1],60),labels=[0,0,0,1],linewidth=0.,fontsize=16)
    X,Y = m(x,y)
    cmap = plt.get_cmap('RdBu_r')
    clevs=np.arange(0,1.0,.1)
    im = m.contourf(X,Y,mmid,clevs,cmap=cmap,extend='max')
    axes.set_title('Prop. of Interannual Var. Explained by Q1 & Q2',loc='center',fontsize=16,y=1.02)
    plt.colorbar(im,orientation='horizontal', pad=0.15,shrink=.9,aspect=45)
    fig = fig.savefig("{WK_DIR}/model/Proportion of explained Interannual Variance.png", format='png',bbox_inches='tight')    

    print("Plotting Completed")
    

top_heaviness_ratio_robustness_calc(os.environ["OMEGA_FILE"],os.environ["omega_var"])



