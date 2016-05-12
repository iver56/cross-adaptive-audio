# Fitness of transformations in cross-adaptive audio effects

The project will investigate methods of evaluating the musical applicability of cross-adaptive audio effects. The field of adaptive audio effects has been researched during the last 10-15 years, where analysis of various features of the audio signal is used to adaptively control parameters of audio processing of the same signal. Cross-adaptivity has been used similarly in automatic mixing algorithms. The relatively new field of signal interaction relates to the use of these techniques where features of one signal affect the processing of another in a live performance setting. As an example, the pitch tracking data of vocals used to control the reverberation time of the drums, or the noisiness measure of a guitar used to control the filtering of vocals. This also allows for complex signal interactions where features from several signals can be used to affect the processing of another signal. As these kinds of signal interactions are relatively uncharted territory, methods to evaluate various cross-coupling of features have not been formalized and as such currently left to empirical testing. The project should investigate AI methods for finding potentially useful mappings and evaluating their fitness.

## Install dependencies (Ubuntu)

* Install csound: `sudo apt-get install csound`
* Install [aubio](http://aubio.org/download): `sudo apt-get install aubio-tools libaubio-dev libaubio-doc`
* Install essentia extractors (optional):
  * `cd ~/ && wget http://essentia.upf.edu/documentation/extractors/essentia-extractors-v2.1_beta2-linux-x86_64.tar.gz`
  * `tar xzf essentia-extractors-v2.1_beta2-linux-x86_64.tar.gz`
  * `echo 'PATH=~/essentia-extractors-v2.1_beta2/:$PATH' >> ~/.bashrc`
  * `source ~/.bashrc`
* Install MultiNEAT:
  * Install boost c++ libraries: `sudo apt-get install libboost-all-dev`
  * `cd ~/ && git clone https://github.com/peter-ch/MultiNEAT.git`
  * `cd MultiNEAT`
  * `sudo python setup.py install`
* Install NodeJS
  * `sudo apt-get install nodejs npm`
* Install Sonic Annotator
  * `cd ~/ && wget https://code.soundsoftware.ac.uk/attachments/download/1876/sonic-annotator_1.4cc1-1_amd64.deb`
  * `sudo dpkg -i sonic-annotator_1.4cc1-1_amd64.deb`
  * If installation fails due to missing dependencies don't worry: Just run `sudo apt-get -f install` and then try to install again.
* Download the libXtract vamp plugin:
  * `cd ~/ && wget https://code.soundsoftware.ac.uk/attachments/download/620/vamp-libxtract-plugins-0.6.6.20121204-amd64-linux.tar.gz`
  * `tar -xf vamp-libxtract-plugins-0.6.6.20121204-amd64-linux.tar.gz`
  * `sudo mkdir -p /usr/local/lib/vamp`
  * `sudo mv vamp-libxtract-plugins-0.6.6.20121204-amd64-linux/vamp-libxtract.* /usr/local/lib/vamp`

## Install dependencies (Windows)

### Install Python 2.7
https://www.python.org/downloads/

### Install Csound
http://csound.github.io/download.html

### Install HyperNEAT and dependencies (numpy, matplotlib)
Building these dependencies from source can be difficult and time-consuming, so let's download wheel binaries instead

* Go to http://www.lfd.uci.edu/~gohlke/pythonlibs/#multineat
    * Download numpy-1.10.4+mkl-cp27-none-win32.whl
    * Download MultiNEAT-0.3-cp27-none-win32.whl
* `pip install numpy-1.10.4+mkl-cp27-none-win32.whl`
* `pip install MultiNEAT-0.3-cp27-none-win32.whl`

### Install Aubio
* Download http://aubio.org/bin/0.4.2/aubio-0.4.2.win32_binary.zip
* Extract and add to the PATH variable

### Install Essentia Extractors (optional)
* Download tar for windows at http://essentia.upf.edu/documentation/extractors/
* Extract and add to the PATH variable

### Install Sonic Annotator and the libXtract vamp plugin

* https://code.soundsoftware.ac.uk/projects/sonic-annotator/files
    * Download and extract sonic-annotator-1.4-win32.zip (or a newer version, if applicable) to for example C:\sonic-annotator and add that directory to the PATH variable
* https://code.soundsoftware.ac.uk/projects/vamp-libxtract-plugins/files
    * Download vamp-libxtract-plugins-0.6.6.20121204-win32.zip and extract vamp-libxtract.cat, vamp-libxtract.dll and vamp-libxtract.n3 to C:\Program Files (x86)\Vamp Plugins ([more info about installing vamp plugins here](http://www.vamp-plugins.org/download.html#install))

### Install NodeJS
https://nodejs.org/en/download/

### Install GNU make for Windows (optional)
http://www.equation.com/servlet/equation.cmd?fa=make

## Setup of this project

* Clone this repository: `git clone https://github.com/iver56/cross-adaptive-audio.git && cd cross-adaptive-audio`
* Get a local settings file: `cp settings.py.example settings.py`
* Create a settings file for your experiment(s): `cp experiment_settings.json.example experiment_settings.json`
* Make sure that all dependencies are installed: `[sudo] pip install -r requirements.txt`
* Install Node.js dependencies: `cd node_server && npm install && cd -`
    * If npm fails to properly install the websocket package, go to https://www.npmjs.com/package/websocket#installation for more information

## Example commands

* `make test` (run all tests)
* `python neuroevolution.py -i drums.wav synth.wav -g 15 -p 20` (run the evolutionary algorithm for 15 generations with a population of 20)
    * This command assumes that drums.wav and synth.wav are present in the input folder. The sounds should be of equal length, and they should be mono, not stereo. And please use sampling rate 44100 and bit depth 16.
* `python list_all_features.py` (list all analyzers and the features they offer)
* `make clean` (remove data written during an experiment)
* `make prepare-ramdisk` (ensure that directories are present in the RAM disk. Copy audio input files and the web-based visualization system)
* `make serve` (start a server for a web client that can interactively visualize the experiment data)
    * Go to localhost:8080 in your favorite browser and you'll see a GUI that looks somewhat like this:
    ![Screenshot of visualization](visualization-screenshot.png)

## Use RAM disk

Experiments can run ~10% faster if you use a RAM disk to reduce I/O overhead. When you have a
RAM disk running, set `BASE_DIR` in settings.py to the path of the RAM disk
(f.ex. `'/mnt/ramdisk'` for Ubuntu or `'R:\\'` for Windows) and run `make prepare-ramdisk`

### RAM disk setup (Ubuntu)

Assuming you have no RAM disk set up already, and you want one with 3 GB of space:
* `sudo mkdir -p /mnt/ramdisk`
* `sudo mount -t tmpfs -o size=3072m tmpfs /mnt/ramdisk`

`sudo nano /etc/fstab` and add the following line:
`tmpfs       /mnt/ramdisk tmpfs   nodev,nosuid,noexec,nodiratime,size=3072M   0 0`

The ramdisk should now be mounted on startup/reboot. You can confirm this by rebooting and running
`df -h /mnt/ramdisk`

### RAM disk setup (Windows)

I haven't been able to get a performance gain by using a RAM disk on a Windows machine with an SSD,
but if you want to try, you can install a program like this:
https://www.softperfect.com/products/ramdisk/

Use at your own risk
