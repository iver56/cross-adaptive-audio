import settings
import os


class Clean(object):
    def __init__(self):
        """
        Remove all feature data and meta data cache
        :return:
        """
        for path in [settings.META_DATA_CACHE_DIRECTORY, settings.FEATURE_DATA_DIRECTORY, settings.CSD_DIRECTORY]:
            for root, dirs, files in os.walk(path):
                for currentFile in files:
                    extensions = ('.json', '.csd')
                    if any(currentFile.lower().endswith(ext) for ext in extensions):
                        print "Removing file: " + currentFile
                        os.remove(os.path.join(root, currentFile))

if __name__ == '__main__':
    Clean()
