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
  * Install boost c++ libraries: `sudo apt-get install libboost-all-dev`
  * `git clone https://github.com/peter-ch/MultiNEAT.git`
  * `cd MultiNEAT`
  * `sudo python setup.py install`

## Install dependencies (Windows)

### Install Python 2.7
https://www.python.org/downloads/

### Install Csound
http://csound.github.io/download.html

### Install HyperNEAT and dependencies (numpy, matplotlib, opencv with python bindings)
* Go to http://www.lfd.uci.edu/~gohlke/pythonlibs/#multineat
* Download numpy-1.10.4+mkl-cp27-none-win32.whl
* Download matplotlib-1.5.1-cp27-none-win32.whl
* Download MultiNEAT-0.3-cp27-none-win32.whl
* `pip install numpy-1.10.4+mkl-cp27-none-win32.whl`
* `pip install matplotlib-1.5.1-cp27-none-win32.whl`
* `pip install MultiNEAT-0.3-cp27-none-win32.whl`
* Install OpenCV: http://docs.opencv.org/2.4/doc/tutorials/introduction/windows_install/windows_install.html
* Install Python bindings for OpenCV: http://docs.opencv.org/master/d5/de5/tutorial_py_setup_in_windows.html#gsc.tab=0
* Install pygame (optional): `sudo apt-get install python-pygame`

### Install Aubio
* Download http://aubio.org/bin/0.4.2/aubio-0.4.2.win32_binary.zip
* Extract and add to the PATH variable

### Install Essentia Extractors
* Download tar for windows at http://essentia.upf.edu/documentation/extractors/
* Extract and add to the PATH variable

### Install Pygame (optional)
http://www.pygame.org/download.shtml

## Setup

* Clone this repository
* Get a local settings file: `cp settings.py.example settings.py`
* Install dependencies: `[sudo] pip install -r requirements.txt`

## Example commands

* `[sudo] python create_project.py --name test1`
* `[sudo] python analyze.py -i drums_remind_me.wav`
* `[sudo] python visualize.py -i drums_remind_me.wav`
* `[sudo] python cross_adapt.py -s synth_remind_me.wav -d drums_remind_me.wav`
