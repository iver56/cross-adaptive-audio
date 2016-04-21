# Fitness of transformations in cross-adaptive audio effects

The project will investigate methods of evaluating the musical applicability of cross-adaptive audio effects. The field of adaptive audio effects has been researched during the last 10-15 years, where analysis of various features of the audio signal is used to adaptively control parameters of audio processing of the same signal. Cross-adaptivity has been used similarly in automatic mixing algorithms. The relatively new field of signal interaction relates to the use of these techniques where features of one signal affect the processing of another in a live performance setting. As an example, the pitch tracking data of vocals used to control the reverberation time of the drums, or the noisiness measure of a guitar used to control the filtering of vocals. This also allows for complex signal interactions where features from several signals can be used to affect the processing of another signal. As these kinds of signal interactions are relatively uncharted territory, methods to evaluate various cross-coupling of features have not been formalized and as such currently left to empirical testing. The project should investigate AI methods for finding potentially useful mappings and evaluating their fitness.

## Install dependencies (Ubuntu)

* Install matplotlib dependencies: `sudo apt-get install libfreetype6-dev libpng-dev`
* Install csound: `sudo apt-get install csound`
* Install [aubio](http://aubio.org/download): `apt-get install aubio-tools libaubio-dev libaubio-doc`
* Install essentia extractors:
  * `wget http://essentia.upf.edu/documentation/extractors/essentia-extractors-v2.1_beta2-linux-x86_64.tar.gz`
  * `tar xzf essentia-extractors-v2.1_beta2-linux-x86_64.tar.gz`
  * `echo 'PATH=/data/essentia-extractors-v2.1_beta2/:$PATH' >> ~/.bashrc`
  * `source ~/.bashrc`
* Install MultiNEAT:
  * Install boost c++ libraries: `[sudo] apt-get install libboost-all-dev`
  * `git clone https://github.com/peter-ch/MultiNEAT.git`
  * `cd MultiNEAT`
  * `[sudo] python setup.py install`
* Install NodeJS (optional)

## Install dependencies (Windows)

### Install Python 2.7
https://www.python.org/downloads/

### Install Csound
http://csound.github.io/download.html

### Install HyperNEAT and dependencies (numpy, matplotlib)
Building these dependencies from source can be difficult and time-consuming, so let's download wheel binaries instead

* Go to http://www.lfd.uci.edu/~gohlke/pythonlibs/#multineat
    * Download numpy-1.10.4+mkl-cp27-none-win32.whl
    * Download matplotlib-1.5.1-cp27-none-win32.whl
    * Download MultiNEAT-0.3-cp27-none-win32.whl
* `pip install numpy-1.10.4+mkl-cp27-none-win32.whl`
* `pip install matplotlib-1.5.1-cp27-none-win32.whl`
* `pip install MultiNEAT-0.3-cp27-none-win32.whl`

### Install Aubio
* Download http://aubio.org/bin/0.4.2/aubio-0.4.2.win32_binary.zip
* Extract and add to the PATH variable

### Install Essentia Extractors
* Download tar for windows at http://essentia.upf.edu/documentation/extractors/
* Extract and add to the PATH variable

### Install NodeJS (optional)
https://nodejs.org/en/download/

### Install GNU make for Windows (optional)
http://www.equation.com/servlet/equation.cmd?fa=make

## Setup of this project

* Clone this repository
* Get a local settings file: `cp settings.py.example settings.py`
* Create a settings file for your experiment(s): `cp experiment_settings.json.example experiment_settings.json`
* Make sure that all dependencies are installed: `[sudo] pip install -r requirements.txt`
* Navigate to the node_server folder and run `npm install`

## Example commands

* `make test` (run all tests)
* `python create_project.py` (find and analyze a collection of sound files in the input folder)
* `python analyze.py -i drums.wav` (manually analyze drums.wav and put the result in a json file)
* `python visualize.py -i drums.wav` (visualize the analysis of drums.wav)
* `python fitness_evaluator.py -i drums.wav synth.wav` (print a number that represents the similarity between drums.wav and synth.wav)
* `python neuroevolution.py -i drums.wav synth.wav -g 100 -p 30` (run the genetic algorithm for 100 generations with a population of 30)
* `make clean` (remove data written during an experiment, but keep data about input files)
* `make clean-all` (remove all calculated data and ensure that directories are present in the RAM disk)
* `make serve` (start a server for a web client that can interactively visualize the experiment data)
    * Go to localhost:8080 in your favorite browser and you'll see a GUI that looks somewhat like this:
    ![Screenshot of visualization](visualization-screenshot.png)

## RAM disk (Ubuntu)

Experiments can run ~10-30% faster (depending on hardware) if you use a RAM disk to reduce I/O overhead.

* `sudo mkdir -p /mnt/ramdisk`
* `sudo mount -t tmpfs -o size=3072m tmpfs /mnt/ramdisk`

`sudo nano /etc/fstab` and add the following line:
`tmpfs       /mnt/ramdisk tmpfs   nodev,nosuid,noexec,nodiratime,size=3072M   0 0`

The ramdisk should now be mounted on startup/reboot. You can confirm this by rebooting and running
`df -h /mnt/ramdisk`

Finally, set BASE_DIR in settings.py to '/mnt/ramdisk'
