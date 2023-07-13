from pydub import AudioSegment, effects
import pyrubberband as pyrb
import os
import sys
import numpy as np
import scipy as scp
import subprocess as sp
import time
from matplotlib import pyplot as plt

from testParameters import *

print(f"Initialing .wav files")
# Setup tests
testIteration = 0
procSet = []
testSetups = []
for voiceComm_ind in range(len(voiceComm_TestSet)):
	for syllable_ind in range(len(syllable_TestSet)):
		for noteDur_ind in range(len(noteDur_TestSet)):
			for restDur_ind in range(len(restDur_TestSet)):
				voiceComm_foo = voiceComm_TestSet[voiceComm_ind]
				syllable_foo = syllable_TestSet[syllable_ind]
				noteDur_foo = noteDur_TestSet[noteDur_ind]
				restDur_foo = restDur_TestSet[restDur_ind]
				testSetups.append((voiceComm_ind, syllable_ind, noteDur_ind, restDur_ind))


				inputFilename = f"timingTesting/tmp/{testIteration}.txt"
				outputFilename = f"timingTesting/tmp/{testIteration}.wav"

				fooTestTxt = open(inputFilename, 'w')

				fooTestTxt.write('[:phoneme arpabet speak on]')
				fooTestTxt.write(voiceComm_foo)
				fooTestTxt.write('[')

				for fooNote in note_TestSet:
					fooTestTxt.write(f"{syllable_foo}<{noteDur_foo},{fooNote}>")
					if restDur_foo > 0: fooTestTxt.write(f"_<{restDur_foo},0>")

				fooTestTxt.write(']')

				fooTestTxt.close()

				
				DEC_proc = sp.Popen(f".{os.sep}say.exe -w {outputFilename} < {inputFilename}", shell=True) # Finally actual run DECtalk! Opens a bunch of processes to run every file in parallel
				procSet.append(DEC_proc)

				print(f"Running Test {testIteration}")
				testIteration += 1

# Wait for all of the DECtalk programs to exit
ii=0
while len(procSet) > 0:
	if procSet[ii].poll() != None:
		procSet.pop(ii)
	else:
		ii += 1
	
	if ii >= len(procSet):
		ii = 0
		print(f"Waiting on say.exe processes to finish, {len(procSet)} remaing")
		time.sleep(0.5)




consolidatedData = []
for fooIteration in range(testIteration):
	fooAudio = AudioSegment.from_file(f"timingTesting/tmp/{fooIteration}.wav")# Load wav file for each test
	audioArray = np.array(fooAudio.get_array_of_samples()) # Convert to np readable

	# Load independent variables for test
	voiceComm_foo = voiceComm_TestSet[testSetups[fooIteration][0]]
	syllable_foo = syllable_TestSet[testSetups[fooIteration][1]]
	noteDur_foo = noteDur_TestSet[testSetups[fooIteration][2]]
	restDur_foo = restDur_TestSet[testSetups[fooIteration][3]]

	# Get smoothed amplitude values
	smoothSize = 100
	smoothedAmp = scp.ndimage.filters.maximum_filter(abs(audioArray), size=smoothSize)

	# Use edge finding kernel to find edges
	edgeKernelRad = 800
	boostRad = 200
	startKernel = np.full(edgeKernelRad*2, 1.0)
	startKernel[:edgeKernelRad] = -1
	startKernel[edgeKernelRad-boostRad: edgeKernelRad+boostRad] *= 1.5
	startKernel /= np.sum(abs(startKernel))
	audioConvolved = np.convolve(np.abs(smoothedAmp), startKernel)[edgeKernelRad:-edgeKernelRad]
	
	# Find positive and negative peaks
	peakReqDist = int(0.9*sampleRate*(noteDur_foo + restDur_foo)/1000) # Search for peaks within 90% of max range
	startPts = np.array(scp.signal.find_peaks(-1*audioConvolved, distance=peakReqDist)[0])
	stopPts = np.array(scp.signal.find_peaks(audioConvolved, distance=peakReqDist)[0])

	startPts_initLen = len(startPts)
	stopPts_initLen = len(stopPts)
	
	jj = 0
	while jj < len(startPts):
		if jj > 0 and startPts[jj] < stopPts[jj-1]:
			# print(f"del startPts {jj} : {startPts}     {stopPts}")
			startPts = np.delete(startPts, jj)
		elif jj < len(stopPts) and stopPts[jj] < startPts[jj]:
			# print(f"del stopPts {jj} : {startPts}     {stopPts}")
			stopPts = np.delete(stopPts, jj)
		else:
			jj += 1

	if len(startPts) > len(stopPts): startPts = startPts[:len(stopPts)]
	if len(stopPts) > len(startPts): stopPts = stopPts[:len(startPts)]

	testTagStr = f"{voiceComm_foo}   {syllable_foo}   {noteDur_foo}   {restDur_foo}".ljust(20, ' ')

	if len(startPts) != len(note_TestSet):
		print(f"{testTagStr} Failed")
		continue

	print(testTagStr + f"   start:{len(startPts)} (-{startPts_initLen - len(startPts)})" + f"   stop:{len(stopPts)} (-{stopPts_initLen - len(stopPts)})")


	consolidatedData.append(tuple(list(testSetups[fooIteration]) + [startPts, stopPts]))

print(consolidatedData)

import pickle as pkl
dataDump = open(f"timingTesting/tmp/dataBuffer.pkl", 'wb')
pkl.dump(consolidatedData, dataDump)
dataDump.close()