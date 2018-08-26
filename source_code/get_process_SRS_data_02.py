import errno
import glob
import os
import re
import tarfile
import pandas as pd
from datetime import datetime
from ftplib import FTP
from collections import Counter, OrderedDict

# Constants
FTP_ADDRESS = 'ftp.swpc.noaa.gov'
BASE_DIR = 'pub/warehouse/'
MIN_YEAR = '2010'

# Valid Hale classes
HALE_CLASSES = ('alpha', 'beta', 'gamma', 'beta-gamma', 'beta-delta',
                'beta-gamma-delta', 'gamma-delta')

# Valid MaIntosh classes
MACINTOSH_CLASSES = ('axx', 'bxo', 'bxi', 'hrx', 'cro', 'cri', 'hax', 'cao',
                     'cai', 'hsx', 'cso', 'csi', 'dro', 'ero', 'fro', 'dri',
                     'eri', 'fri', 'dao', 'eao', 'fao', 'dai', 'eai', 'fai',
                     'dso', 'eso', 'fso', 'dsi', 'esi', 'fsi', 'dac', 'eac',
                     'fac', 'dsc', 'esc', 'fsc', 'hkx', 'cko', 'cki', 'hhx',
                     'cho', 'chi', 'dko', 'eko', 'fko', 'dki', 'eki', 'fki',
                     'dho', 'eho', 'fho', 'dhi', 'ehi', 'fhi', 'dkc', 'ekc',
                     'fkc', 'dhc', 'ehc', 'fhc')

# Date from which to fetch SRS data:
startdate = datetime(2010, 5, 1)

SRS_RE = re.compile(r'.*SRS.tar.gz')
ISSUE_TIME_RE = re.compile(r'^:Issued: (.*)$', flags=re.M)


# Functions: ************
def parse_SRS_data(srs_data):
    out = []
    # Empty SRS files
    if len(srs_data) > 0:
        match = ISSUE_TIME_RE.search(srs_data)
        issue_time = datetime.strptime(match.group(1), '%Y %b %d %H%M %Z')
        lines = srs_data.splitlines()
        for line in lines[10:]:
            tokens = line.split()
            # Make all lower case
            tokens = list(map(lambda x: x.lower(), tokens))
            # AR data entries all ways start with a number
            if tokens[0].isdigit():
                tokens.insert(0, issue_time)
                out.append(tokens)
            # If not number last AR entry so break
            else:
                return out
    else:
        # Info on empty files
        print("Empty SRS file {}".format(srs_file))


def hale_class_count(hale_class_list):
    # Calculate occurrence of each class
    count = Counter(hale_class_list)

    # Remove values not in the definition
    for e in list(set(count.keys()).difference(HALE_CLASSES)):
        count.pop(e)
        print('Removed key {} as not in Hale classification'.format(e))

    all_count = OrderedDict({key: 0 for key in HALE_CLASSES})
    for key, value in count.items():
        all_count[key] = value

    return all_count


def macintosh_class_count(mcintosh_class_list):
    count = Counter(mcintosh_class_list)

    # Remove strange values (only 1 count) and make too many classes 64 v 60:
    for e in list(set(count.keys()).difference(MACINTOSH_CLASSES)):
        count.pop(e)
        print('Removed key {} as not in McIntosh classification'.format(e))

    all_count = OrderedDict({key: 0 for key in MACINTOSH_CLASSES})

    for key, value in count.items():
        all_count[key] = value

    return all_count


# Splits coordinate data into latitude / longitude and replaces n/s/w/e in
# coords with +/-/+/-:
def split(st, num):
    return [st[start:start+num] for start in range(0, len(st), num)]


def changeWord1(word):
    for letter in word:
        if letter == "n":
            word = word.replace(letter, "")
        if letter == "s":
            word = word.replace(letter, "-")
    return word


def changeWord2(word):
    for letter in word:
        if letter == "w":
            word = word.replace(letter, "")
        if letter == "e":
            word = word.replace(letter, "-")
    return word

# ***********************

if __name__ == '__main__':

    # The following code downloads SRS data.

    # Now as current years not in tar.gz format
    current_year = str(datetime.now().year)

    # Open and login FTP
    ftp = FTP(FTP_ADDRESS)
    ftp.login()
    ftp.cwd(BASE_DIR)

    # Get dir list
    dir_list = ftp.nlst()

    # Filter out all but year dirs 2010, 2011 etc
    years = [x for x in dir_list if x.isdigit() and
             MIN_YEAR <= x < current_year]

    # Create data dir
    try:
        os.mkdir(os.path.join('..', 'data', 'raw',
                              'SRS'))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    # Loop over years and download tar files
    for year in years:
        file_name = year + "_SRS.tar.gz"
        path = os.path.join('..', 'data', 'raw',
                            'SRS', file_name)
        # Skip if we already have it
        if not os.path.exists(path):
            ftp.cwd(year)
            files = ftp.nlst()
            for srs in filter(SRS_RE.match, files):
                print("Starting download of {}".format(path))
                ftp.retrbinary("RETR " + str(srs), open(path, "wb").write)
                print("Finished download of {}".format(file_name))
            ftp.cwd('..')
        else:
            print("File exists, skipping {}".format(file_name))

    # Extract tar files to year directories
    tar_files = glob.glob(os.path.join('..', 'data', 'raw',
                                       'SRS', '*.tar.gz'))
    for file in tar_files:
        dir_name = file[16:20]
        print("Extracting {}".format(dir_name))
        path = os.path.join('..', 'data', 'raw',
                            'SRS', dir_name)
        tar = tarfile.open(file, 'r')

        for member in tar.getmembers():
            if member.isreg():
                member.name = os.path.basename(member.name)
                tar.extract(member, path)

        print("Finished Extracting {}".format(dir_name))

    # For the current year download individual files
    ftp.cwd(current_year + '/SRS/')
    files = ftp.nlst()
    current_path = os.path.join('..', 'data', 'raw',
                                'SRS', current_year)
    try:
        os.mkdir(current_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    # Download each file to current year dir
    for file in files:
        file_path = os.path.join(current_path, file)
        if not os.path.exists(file_path):
            print("Starting download of {}".format(file))
            ftp.retrbinary('RETR ' + file, open(file_path, 'wb').write)
            print("Finished download of {}".format(file))
        else:
            print("File exits skipping {}".format(file_path))

    # ***********************
    # The following code formats the downloaded SRS data.

    # from matplotlib import pyplot as plt

    # Open each file and parse out AR info
    res = []
    srs_files = glob.glob(os.path.join('..', 'data', 'raw',
                                       'SRS', '*', "*SRS.txt"))
    for srs_file in srs_files:
        with open(srs_file, 'r') as file:
            data = file.read()
            ar_data = parse_SRS_data(data)
            if ar_data:
                res.append(ar_data)

    res = [item for sublist in res for item in sublist]  # removes sub-lists,

    # Filter for events after HMI start and between 60 deg E/W
    post_hmi = list(filter(lambda x: x[0] >= startdate, res))
    post_hmi_pm60 = list(filter(lambda x: int(re.findall(r'\d+',
                                              x[2])[1]) <= 60, post_hmi))

    # Extract data, date, macintosh, mag class
    dates = [x[0] for x in post_hmi_pm60]
    hale = [x[-1] for x in post_hmi_pm60]
    coords = [x[2] for x in post_hmi_pm60]
    # macintosh = [x[5] for x in res]

    for i in post_hmi_pm60:
        i[2:3] = split(i[2], 3)
        i[2] = int(changeWord1(i[2]))
        i[3] = int(changeWord2(i[3]))

    hale_class_occurrence = hale_class_count(hale)
    print("Hale class occurrence = ")
    print(hale_class_occurrence)

    # Creates a df for SRS data:
    SRS_df = pd.DataFrame(post_hmi_pm60, columns=['Date', 'Number', 'Latitude',
                                                  'Longitude', 'Lo', 'Area',
                                                  'Z', 'LL', 'NN',
                                                  'Hale Class'])

    # Create data dir
    try:
        os.mkdir(os.path.join('..', 'data', 'processed',
                              'SRS'))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    # Stores DataFrame as a pickle object:
    SRS_df.to_pickle(os.path.join('..', 'data', 'processed',
                                  'SRS', 'SRS_df_pickle'))

    print("Done")
