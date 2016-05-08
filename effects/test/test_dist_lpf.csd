;    Copyright 2015 Oeyvind Brandtsegg
;
;    Parts of this file originates from the Signal Interaction Toolkit
;
;    The Signal Interaction Toolkit is free software: you can redistribute it and/or modify
;    it under the terms of the GNU General Public License version 3
;    as published by the Free Software Foundation.
;
;    The Signal Interaction Toolkit is distributed in the hope that it will be useful,
;    but WITHOUT ANY WARRANTY; without even the implied warranty of
;    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;    GNU General Public License for more details.
;
;    You should have received a copy of the GNU General Public License
;    along with The Signal Interaction Toolkit.
;    If not, see <http://www.gnu.org/licenses/>.

<CsoundSynthesizer>
<CsOptions>
-M0 -odac
</CsOptions>
<CsInstruments>
	sr	= 44100
	ksmps	= 441
	nchnls	= 1
	0dbfs	= 1

	instr 1

kTime 	timek

;****************************************************************
; LPF18 Filter
;****************************************************************
aIn 	rand 1

kDrive ctrl7 1, 2, 1, 12
kFreq ctrl7 1, 3, 20, 10000 ; TODO: skew 0.3
kResonance ctrl7 1, 4, 0.001, 0.95
;kDist ctrl7 1, 5, 0.001, 10 ; TODO: skew 0.5
kDist = 1
;kMix ctrl7 1, 6, 0, 1
kMix = 1
;kPostGain ctrl7 1, 7, 0, 10 ; TODO: skew 0.3
kPostGain = 1

printk2 kDrive

kDrive 	tonek	kDrive, 50
kFreq 	tonek	kFreq, 50
kResonance 	tonek	kResonance, 50
kDist 	tonek	kDist, 50
kAutoLevel 	=	0.9
kMix 	tonek	kMix, 50
kPostGain 	tonek	kPostGain, 50

; stage 1, distortion
kpregain 	=	kDrive ; dist amount
ishape 	=	0.8 ; dist shaping
kpostgain 	=	(0.5 / kpregain) * (kpregain * 0.5) ; auto set output gain corresponding to input drive
ishape1 	=	ishape * 1.6
ishape2 	=	ishape
adist 	distort1	aIn, kpregain, kpostgain, ishape1, ishape2

; stage 2, lpf18 filter
	denorm	adist
afilt 	lpf18	adist, kFreq, kResonance, kDist
kleveladjust 	=	1 / (sqrt(kDrive) + (kDist * 2)) ; attempt automatic level adjustment according to distortion drive
afilt 	=	(afilt * (1 - kAutoLevel)) + (afilt * kleveladjust * kAutoLevel) ; and select balance between autogained and straight dist signal

aOut 	=	((afilt * kMix) + (aIn * (1 - kMix))) * kPostGain

	out	aOut

	endin
</CsInstruments>
<CsScore>
i1	0	80
e
</CsScore>
</CsoundSynthesizer>
