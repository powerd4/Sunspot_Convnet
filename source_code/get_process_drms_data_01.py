# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 12:15:54 2017

@author: Dean Power

drms data: ‘hmi.sharp_cea_720s’
segment = 'continuum'
Example format: 'hmi.sharp_cea_720s[][2012.03.07_17:45_TAI/30m]'
"""
import os
import errno
import drms
from time import sleep

import urllib.request
import urllib.error

import pandas as pd

timestamps = ["2010.01.01_00:30:00_TAI/365d@24h",
              "2011.01.01_00:30:00_TAI/365d@24h",
              "2012.01.01_00:30:00_TAI/365d@24h",
              "2013.01.01_00:30:00_TAI/365d@24h",
              "2014.01.01_00:30:00_TAI/365d@24h",
              "2015.01.01_00:30:00_TAI/365d@24h",
              "2016.01.01_00:30:00_TAI/365d@24h",
              "2017.01.01_00:30:00_TAI/365d@24h"]

cli = drms.Client()  # Create an instance of the drms.Client class


# DRMS query funcions:
def query_drms(timestamps, cli):  # drms query of interest

    drms_param = 'hmi.sharp_cea_720s[][' + timestamps + ']'

    # DRMS query:
    drms_df = cli.query(drms_param, key='T_REC, HARPNUM, NOAA_AR, NOAA_NUM, \
                        NOAA_ARS, NPIX, CRPIX1, CRPIX2, LAT_MIN, LON_MIN, \
                        LAT_MAX, LON_MAX, LAT_FWT, LON_FWT, LAT_FWTPOS, \
                        LON_FWTPOS, LAT_FWTNEG, LON_FWTNEG')

    # Renames columns:
    drms_df.columns = ['Date', 'HARPNUM', 'NOAA Number', 'Number of NOAAs',
                       'NOAA numbers',  'No. pixels', 'LLC-Centre x',
                       'LLC-Centre y', 'BL LAT', 'BL LONG', 'TR LAT',
                       'TR LONG', 'Latitude', 'Longitude', 'FWT POS LAT',
                       'FWT POS LONG', 'FWT NEG LAT', 'FWT NEG LONG']

    drms_df['Date'] = drms_df['Date'].str.replace(r'_TAI$', '')
    drms_df['Date'] = drms_df['Date'].apply(lambda x: pd.to_datetime(x,
                                            format='%Y.%m.%d_%H:%M:%S'))
    return drms_df


def query_url(timestamps, cli):  # URL's of interest

    seg_param = 'hmi.sharp_cea_720s[][' + timestamps + ']'

    # AR query:
    get_cont = cli.query(seg_param, seg='continuum')

    url = ['http://jsoc.stanford.edu' + j for j in get_cont.continuum]
    url = pd.DataFrame(url, columns=['url'])
    return url

if __name__ == '__main__':

    dataframes_list = []
    urls_list = []

    for i in timestamps:
        try:
            dataframes_list.append(query_drms(i, cli))
            urls_list.append(query_url(i, cli))

        except (urllib.request.URLError, OSError) as e:
            print("Connection lost, retrying in 20 seconds...")
            sleep(20)
            continue
        print("Year " + str(i) + " complete.")

    drms_data = pd.concat(dataframes_list, ignore_index=True)
    url_data = pd.concat(urls_list, ignore_index=True)
    drms_data = pd.concat([drms_data, url_data], axis=1)
    print("Done.")

    # Create data dir
    try:
        os.mkdir(os.path.join('..', 'data', 'processed',
                              'drms'))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    drms_data.to_pickle(os.path.join('..', 'data', 'processed',
                                     'drms', 'drms_df_pickle'))
