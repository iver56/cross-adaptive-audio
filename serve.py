import settings
from whichcraft import which
import subprocess
import os


command = []
if which('node') is not None:
    command.append('node')
elif which('nodejs') is not None:
    command.append('nodejs')
else:
    raise Exception('NodeJS is not installed. Please install it.')

command.append(os.path.join(settings.BASE_DIR, 'node_server', 'server.js'))
print(str(command))

p = subprocess.Popen(command)
p.wait()
