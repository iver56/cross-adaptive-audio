<CsoundSynthesizer>

<CsOptions>
-i input/synth_remind_me.wav
-odac
</CsOptions>

<CsInstruments>
sr     = 44100
kr     = 4410
nchnls = 1

instr 1
	iFreq = 300
	iDur  = p3
	iMix  = p4

	a1 in

	aMod oscils 1, iFreq, 0

	a1 = sqrt(1 - iMix) * a1 + sqrt(iMix) * a1 * aMod

	out a1
endin
</CsInstruments>

<CsScore>
;    iDur iMix
i1 0 3    0
i1 3 3    1
e
</CsScore>

</CsoundSynthesizer>