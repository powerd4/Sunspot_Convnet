
from os import path
from datetime import datetime
from itertools import chain

from ..source_code.get_process_SRS_data_02 import parse_SRS_data, \
    hale_class_count, macintosh_class_count, HALE_CLASSES, MACINTOSH_CLASSES


class TestAnalyseSRS(object):
    def test_parse_SRS(self):
        with open(path.join('tests', 'data', '20120105SRS.txt')) as file:
            data = file.read()
            res = parse_SRS_data(data)

            assert res[0] == [datetime(2012, 1, 5, 0, 30), '1386', 's17w87', '150', '0030', 'hsx',
                              '03', '01', 'alpha']

            assert len(res) == 6

    def test_hale_class_count(self):
        # Create test data each class occurs i time for i 1 ... 7
        test_classes = [[cls for j in range(i+1)] for i, cls in enumerate(HALE_CLASSES)]
        # Flatten nested lists
        test_classes = list(chain.from_iterable(test_classes))
        # Add incorrect class which should be dropped
        test_classes.append('wrong')

        count = hale_class_count(test_classes)

        assert len(count) == len(HALE_CLASSES)
        assert sorted(list(count.values())) == list(range(1, len(HALE_CLASSES) + 1))

    def test_macintosh_class_count(self):
        # Create test data each class occurs i time for i 1 ... 7
        test_classes = [[cls for j in range(i+1)] for i, cls in enumerate(MACINTOSH_CLASSES)]
        # Flatten nested lists
        test_classes = list(chain.from_iterable(test_classes))
        # Add incorrect class which should be dropped
        test_classes.append('wrong')

        count = macintosh_class_count(test_classes)

        assert len(count) == len(MACINTOSH_CLASSES)
        assert sorted(list(count.values())) == list(range(1, len(MACINTOSH_CLASSES) + 1))
