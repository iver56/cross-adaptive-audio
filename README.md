# Fitness of transformations in cross-adaptive audio effects

The project will investigate methods of evaluating the musical applicability of cross-adaptive audio effects. The field of adaptive audio effects has been researched during the last 10-15 years, where analysis of various features of the audio signal is used to adaptively control parameters of audio processing of the same signal. Cross-adaptivity has been used similarly in automatic mixing algorithms. The relatively new field of signal interaction relates to the use of these techniques where features of one signal affect the processing of another in a live performance setting. As an example, the pitch tracking data of vocals used to control the reverberation time of the drums, or the noisiness measure of a guitar used to control the filtering of vocals. This also allows for complex signal interactions where features from several signals can be used to affect the processing of another signal. As these kinds of signal interactions are relatively uncharted territory, methods to evaluate various cross-coupling of features have not been formalized and as such currently left to empirical testing. The project should investigate AI methods for finding potentially useful mappings and evaluating their fitness.

## Setup (Ubuntu)

* `cp settings.py.example settings.py`
* Initialize virtual environment: `virtualenv -p /usr/bin/python3 venv3`
* Activate virtual environment : `source venv3/bin/activate`
* `make`
* Install csound: `sudo apt-get install csound`
* Install [aubio](http://aubio.org/download): `apt-get install aubio-tools libaubio-dev libaubio-doc`
* Install essentia extractors:
  * `wget http://essentia.upf.edu/documentation/extractors/essentia-extractors-v2.1_beta2-linux-x86_64.tar.gz`
  * `tar xzf essentia-extractors-v2.1_beta2-linux-x86_64.tar.gz`
  * `echo 'PATH=/data/essentia-extractors-v2.1_beta2/:$PATH' >> ~/.bashrc`
  * `source ~/.bashrc`

## Example commands

* `python create_project.py --name test1`
* `python analyze.py -i drums_remind_me.wav`
* `python visualize.py -i drums_remind_me.wav`
* `python cross_adapt.py -s synth_remind_me.wav -d drums_remind_me.wav`
