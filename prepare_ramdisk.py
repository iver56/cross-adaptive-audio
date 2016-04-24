import settings
import os
import shutil
from distutils import dir_util

if not settings.USE_RAM_DISK:
    raise Exception('You should set USE_RAM_DISK to True in settings.py first')


all_paths = [
    settings.CSD_DIRECTORY,
    settings.INPUT_DIRECTORY,
    settings.OUTPUT_DIRECTORY,
    settings.PROJECT_DATA_DIRECTORY,
    settings.STATS_DATA_DIRECTORY,
    settings.INDIVIDUAL_DATA_DIRECTORY
]

input_dir_not_ramdisk = os.path.join('.', 'input')
web_client_dir_name = 'web_client'
node_server_dir_name = 'node_server'

for path in all_paths:
    if not os.path.exists(path):
        print('Creating directory {}'.format(path))
        os.makedirs(path)

print('Copying input audio files to input folder in RAM disk...')
dir_util.copy_tree(
    input_dir_not_ramdisk,
    settings.INPUT_DIRECTORY
)

print('Copying web client files to RAM disk...')
dir_util.copy_tree(
    os.path.join('.', web_client_dir_name),
    os.path.join(settings.BASE_DIR, web_client_dir_name)
)
shutil.copyfile(
    os.path.join('.', 'index.html'),
    os.path.join(settings.BASE_DIR, 'index.html')
)

print('Copying node server files to RAM disk...')
dir_util.copy_tree(
    os.path.join('.', node_server_dir_name),
    os.path.join(settings.BASE_DIR, node_server_dir_name)
)

print('Done')
