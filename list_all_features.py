from __future__ import print_function
from analyze import Analyzer


if __name__ == '__main__':
    import natsort
    for analyzer_class in Analyzer.AVAILABLE_ANALYZERS:
        relevant_features = natsort.natsorted(analyzer_class.AVAILABLE_FEATURES)
        print()
        print('===== {} ====='.format(analyzer_class.__name__))
        for feature in relevant_features:
            print('  ' + feature)
