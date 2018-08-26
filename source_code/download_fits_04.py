import os
import errno
import urllib.request

from  concurrent.futures import ThreadPoolExecutor, wait
from time import sleep

import pandas as pd

DATA_DIR = os.path.join('..', 'data', 'raw',
                              'fits_files')

def download_save(args):
    url, file_name = args
    try:
        f = open(os.path.join(DATA_DIR, file_name), 'wb')
        u = urllib.request.urlopen(url)
        f.write(u.read())
        f.close()
        print(f'File {file_name} done')
    except (urllib.request.URLError, OSError) as e:
        print(e)


if __name__ == '__main__':

    # Load dataframe:
    df = pd.read_pickle(os.path.join('..', 'data', 'processed',
                                     'SRS', 'df'))

    # Create data dir
    try:
        os.mkdir(DATA_DIR)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            pass
    
    data = []

    for index, row in df.iterrows():

        url_date = row.Date.strftime('%Y_%m_%d_%H_%M_%S')
        url_Number = row['Number']
        # Renames fits files "yyyy_mm_dd_HH_MM_SS_Number_index":
        file_name = url_date + '_' + url_Number + '_' + str(index) + '.fits'

        # Skip if filename exists:
        if os.path.isfile(os.path.join(DATA_DIR, file_name)):
            print('entry ' + str(index) + ' / ' + str(len(df)) + ' exists')
        else:
            data.append((row.URL, file_name))

    executor = ThreadPoolExecutor(max_workers=7)
    res = executor.map(download_save, data)