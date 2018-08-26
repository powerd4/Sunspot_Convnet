import os
import errno

import pandas as pd
import numpy as np

from astropy.time import Time
import matplotlib.pyplot as plt

# function to find index of drms entry closest to srs date.
def nearest(drms_dates, srs_date):
    min_diff = np.min(np.abs(drms_dates - srs_date))
    matches = np.where(np.abs(drms_dates - srs_date) == min_diff)
    return matches[0].tolist()
    # return drms_df.Date[drms_df.Date ==
    #                     min(drms_dates,
    #                         key=lambda x: abs(x - srs_date))].index.tolist()

def in_sharp_box(row, i):
    # if within SHARP box:
    if (row.Longitude > drms_df['BL LONG'][i] and
        row.Longitude < drms_df['TR LONG'][i] and
        row.Latitude > drms_df['BL LAT'][i] and
        row.Latitude < drms_df['TR LAT'][i]):

        return True
    else:
        return False


if __name__ == '__main__':

    drms_df = pd.read_pickle(os.path.join('..', 'data', 'processed',
                                          'drms', 'drms_df_pickle'))

    srs_df = pd.read_pickle(os.path.join('..', 'data', 'processed',
                                         'SRS', 'SRS_df_pickle'))

    # Converts from UTC to TAI time and to datetime64:
    t = Time([i for i in srs_df.Date], scale='utc', out_subfmt='datetime')
    srs_df.Date = [np.datetime64(i) for i in [str(j) for j in t.tai]]

    drms_indices = []
    drms_entry = []

    for index, row in srs_df.iterrows():  # for each SRS row:

        drms_entries_indices = nearest(drms_df.Date, row.Date)
        drms_indices.append(drms_entries_indices)

        # print(f'{len(drms_entries_indices)}: {drms_entries_indices}')

        for i in drms_entries_indices:

            # if within SHARP box:
            if in_sharp_box(row, i):

                # Distance between NOAA and flux-weighted centre of SHARP:
                dist = np.sqrt((row.Latitude - drms_df.iloc[i].Latitude)**2. +
                               (row.Longitude - drms_df.iloc[i].Longitude)**2.)

               # sextuple (SRS row index, drms index, # of NOAAs, NOAA numbers,
               # distance from NOAA to flux weighted drms centre, URL's) :
                drms_entry.append((index, i, drms_df['Number of NOAAs'][i],
                                   drms_df['NOAA numbers'][i], dist,
                                   drms_df.url[i]))

        print('iteration ' + str(index + 1) + " / " + str(len(srs_df.Date)) +
              " complete")

    result = pd.DataFrame(drms_entry, columns=['SRS index', 'drms index',
                                               '# of NOAAs', 'NOAA #s',
                                               'NOAA/drms distance', 'URL'])

    # Create data dir
    # try:
      #   os.mkdir(os.path.join('..', 'data', 'processed',
            #                   'SRS', 'result'))
    # except OSError as exception:
      #   if exception.errno != errno.EEXIST:
        #     print('Pickle object exists.')
    # result = pd.read_pickle(os.path.join('..', 'data', 'processed',
    # 'SRS', 'result'))
    print('len raw df: ' + str(len(result)))

    print('# of NOAAs per SHARP region:')
    print(pd.value_counts(result['# of NOAAs']))

    # Of the entries, check if SRS NOAA is one of them,
    # else delete the row:
    result_temp = result  # Required for below
    for index, row in result.iterrows():
        if srs_df['Number'][row['SRS index']] in row['NOAA #s']:
            pass
        else:
            result_temp.drop(index)
    result = result_temp
    print('Len result after drms/SRS comparison: ' + str(len(result)))


    # Keeps only rows with 1 NOAA:
  #  result = result[(result['# of NOAAs'] == 1)]
#    print('len of df with only 1 NOAA per SHARP: ' +
  #        str(len(result[(result['# of NOAAs'] == 1)])))

    # Optional filtration by maximum distance below:
    # result = result[(result['NOAA/drms distance'] <= 5)]
    # print('len of df with distance <= 5 degrees: ' + str(len(result)))

    # Drops duplicate SRS rows:
    result = result.drop_duplicates(subset='SRS index', keep="first")
    print('len of df with duplicate SRS rows removed: ' + str(len(result)))

    result = result.set_index('SRS index')
    df = pd.concat([srs_df, result], axis=1)  # merges result by SRS index
    print('length of concatenated df with no NaN drops: ' + str(len(df)))
    df = df.dropna()  # removes NaN values in URL column
    df = df.reset_index(drop=True)
    print('length of concatenated df without NaN: ' + str(len(df)))

    plt.figure(1)
    plt.plot(df['Date'], df['NOAA/drms distance'], 'o')
    plt.title('drms / SRS coordinate distances')
    plt.xlabel('Date')
    plt.ylabel('Distance (degrees)')
    plt.show()

    print('Hale class counts for final df:')
    print(pd.value_counts(df['Hale Class']))
    plt.figure(2)
    pd.value_counts(df['Hale Class']).plot.bar()

    # Stores DataFrame as a pickle object:
    df.to_pickle(os.path.join('..', 'data', 'processed',
                              'SRS', 'df'))
