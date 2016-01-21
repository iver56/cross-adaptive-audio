<CsoundSynthesizer>
    <CsOptions>
        -i input/synth_remind_me.wav
        --nosound
    </CsOptions>
    <CsInstruments>
        sr = 44100
        kr = 441 ; ksmps = 100
        nchnls = 1
        0dbfs = 1

        pyinit

        instr 1

        pyruni {{
import os, sys
#sys.path.append(os.getcwd())
from logger import Logger
my_logger = Logger(krate=441, filename='synth_remind_me.wav', features=['rms'])
        }}

        ;kTime times

        aIn in

        kRms rms aIn
        pyassign "my_logger.buffer", kRms
        pyrun "my_logger.log('rms')"

        endin
    </CsInstruments>
    <CsScore>
        i 1 0 5
        e
    </CsScore>
</CsoundSynthesizer>