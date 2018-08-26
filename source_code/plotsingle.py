# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 11:58:36 2017

@author: power

The following will take URL and display in matplotlib.
"""
def plotsingle(url):
    import matplotlib.pyplot as plt
    from astropy.utils.data import download_file
    from astropy.io import fits
    
    image_file = download_file(url, cache=True)
    
    image_data = fits.getdata(image_file, ext=1)
    
    plt.figure()
    plt.imshow(image_data, cmap='gray')
    plt.colorbar()