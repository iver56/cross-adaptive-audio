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

### Install MultiNEAT and numpy
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

## Setup of this project

* Clone this repository: `git clone https://github.com/iver56/cross-adaptive-audio.git && cd cross-adaptive-audio`
* Get a local settings file: `cp settings.py.example settings.py`
* Create a settings file for your experiment(s): `cp experiment_settings.json.example experiment_settings.json`
* Make sure that all dependencies are installed: `[sudo] pip install -r requirements.txt`
* Install Node.js dependencies: `cd node_server && npm install && cd -`
    * If npm fails to properly install the websocket package, go to https://www.npmjs.com/package/websocket#installation for more information

## Usage

First, run `nosetests` to check if things are running smoothly.

### Running an experiment

Input audio files that you use in experiments should reside in the input folder. When you run an experiment with two input files, the two audio clips should be of equal length. Furthermore, the format should be:
* Number of channels: 1 (mono)
* Sampling rate: 44100 Hz
* Bit depth: 16

There are some example files in the test_audio folder. For example, copy drums.wav and noise.wav from the test_audio folder to the input folder.

Our goal in the following example experiment is to make noise.wav sound like drums.wav by running noise.wav through the "dist_lpf" audio effect. The audio effect has a parameters that are controlled by the output of a neural network. The experiment is all about evolving one or more neural networks that behave such that the processed version of noise.wav sounds like drums.wav

Run the command `python neuroevolution.py -i drums.wav noise.wav -g 10 -p 20`

This will run the evolutionary algorithm for 10 generations with a population of 20. While this is running, you might want to open another command line instance and run `python serve.py`. This will start a server for a web client that interactively visualizes the results of the experiment as they become available. Websockets are used to keep the web client synchronized with whatever neuroevolution.py has finished doing. Just visit http://localhost:8080 in your favorite browser. The web client looks somewhat like this:

![Screenshot of visualization](visualization-screenshot.png)

To get information about all the parameters that neuroevolution.py understands, run `python neuroevolution.py --help`

The _most important_ parameters:
```
  -i INPUT_FILES [INPUT_FILES ...], --input INPUT_FILES [INPUT_FILES ...]
                        The filename of the target sound and the filename of
                        the input sound, respectively
  -g NUM_GENERATIONS, --num-generations NUM_GENERATIONS
  -p POPULATION_SIZE, --population_size POPULATION_SIZE
  --fitness {default,mo,hybrid}
                        Multi-Objective (mo) fitness optimizes for a diverse
                        population that consists of various non-dominated
                        trade-offs between similarity in different features.
                        Hybrid fitness is the sum of default and mo, and gives
                        you the best of both worlds
  --neural-input-mode {a,ab,b,s}
                        What to use as neural input. Mode a: target sound.
                        Mode ab: target sound and input sound. Mode b: input
                        sound. Mode s: static input, i.e. only bias.
  --effect EFFECT_NAME  The name of the sound effect to use. See the effects
                        folder for options.
```

But wait, there's more! In experiment_settings.json you can specify which audio features to use for a) similarity calculations and b) neural input. Here's one possible configuration, as in experiment_settings.json.example:
```json
{
  "parameter_lpf_cutoff": 50,
  "similarity_channels": [
    {
      "name": "mfcc_amp",
      "weight": 1.0
    },
    {
      "name": "mfcc_1",
      "weight": 0.2
    }
  ],
  "neural_input_channels": [
    "mfcc_amp",
    "mfcc_amp__derivative",
    "mfcc_1"
  ]
}
```
In this example we are using mfcc_amp and mfcc_1 for similarity calculations, and mfcc_1 is given less weight than mfcc_amp. In other words, mfcc_1 errors matter less than mfcc_amp errors. Neural input is mfcc_amp and the derivative (gradient) of mfcc_amp, which is written as "mfcc_amp__derivative" in the config file. You can add the derivative of any feature by writing "{feature_name}__derivative", (replace {feature_name} with the name of the feature)

To see all the available audio features you can add in experiment_settings.json, run `python list_all_features.py`

When you are done with an experiment, run `python clean.py`. This will delete all files written during the experiment, so you're ready for a new experiment.

## Use RAM disk

Experiments can run ~10% faster if you use a RAM disk to reduce I/O overhead. When you have a
RAM disk running, set `BASE_DIR` in settings.py to the path of the RAM disk
(f.ex. `'/mnt/ramdisk'` for Ubuntu or `'R:\\'` for Windows) and run `python prepare_ramdisk.py`.
The latter command will ensure that directories are present in the RAM disk and copy audio input
files and the web-based visualization system. If you want to experiment with new audio input files
after you ran `python prepare_ramdisk.py`, you can put the new audio files directly in the input folder
on the RAM disk.

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

## Known issues
* libXtract may produce [wrong results on Windows](https://github.com/jamiebullock/LibXtract/issues/65). Use a different analyzer or use Linux.
