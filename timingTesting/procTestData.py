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

import pickle as pkl
dataDump = open(f"timingTesting/tmp/dataBuffer.pkl", 'rb')
consolidatedData = pkl.load(dataDump)
dataDump.close()

# Convert to numpy arrays
voiceComm_indexNP = np.array([consolidatedData[ii][0] for ii in range(len(consolidatedData))])
syllable_indexNP = np.array([consolidatedData[ii][1] for ii in range(len(consolidatedData))])
noteDur_indexNP = np.array([consolidatedData[ii][2] for ii in range(len(consolidatedData))])
restDur_indexNP = np.array([consolidatedData[ii][3] for ii in range(len(consolidatedData))])

startTimesNP = np.array([consolidatedData[ii][4] for ii in range(len(consolidatedData))], dtype=np.double) / sampleRate
stopTimesNP = np.array([consolidatedData[ii][5] for ii in range(len(consolidatedData))], dtype=np.double) / sampleRate


noteDurNP = np.array(noteDur_TestSet, dtype=np.double)[noteDur_indexNP] / 1000
restDurNP = np.array(restDur_TestSet, dtype=np.double)[restDur_indexNP] / 1000

# print(f"voiceComm_indexNP:{voiceComm_indexNP}")
# print(f"syllable_indexNP:{syllable_indexNP}")
# print(f"noteDur_indexNP:{noteDur_indexNP}")
# print(f"restDur_indexNP:{restDur_indexNP}")

# print(f"startTimesNP:{startTimesNP}")
# print(f"stopTimesNP:{stopTimesNP}")

NUM_COLORS = len(syllable_TestSet)
print(f"NUM_COLORS:{NUM_COLORS}")
cm = plt.get_cmap('gist_rainbow')
colorSet = np.array( [cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS)] )

# Get 2d array of notes played
noteValues = np.zeros_like(startTimesNP)
for ii in range(len(note_TestSet)):
    noteValues[:, ii] = note_TestSet[ii]
    
noteValues = np.tile(note_TestSet, (len(startTimesNP), 1))

# Expected space between each note
expectedSpacing = noteDurNP+restDurNP
expectedSpacing_2D = np.tile(expectedSpacing, (len(note_TestSet), 1)).transpose()

noteSpacingError = startTimesNP[:, 1:] -startTimesNP[:, :-1] -expectedSpacing_2D[:, :-1]

noteDurationError = stopTimesNP -startTimesNP -np.tile(noteDurNP, (len(note_TestSet), 1)).transpose()


ax = plt.figure().add_subplot(projection='3d')

# ax.scatter(noteDurNP, restDurNP, meanNoteSpacing , c=colorSet[syllable_indexNP])



# ax.scatter(noteDurNP, restDurNP, meanNoteDuration-noteDurNP, c=colorSet[syllable_indexNP])
# ax.set_xlabel('Note Duration')
# ax.set_ylabel('Rest Duration')
# ax.set_zlabel('Note Spacing Error')


print(f"noteValues:{noteValues.shape}")
print(f"noteSpacingError:{noteSpacingError.shape}")
print(f"noteDurationError:{noteDurationError.shape}")
print(f"colorSet[syllable_indexNP]:{colorSet[syllable_indexNP].shape}")

colorSet_2D = np.tile(colorSet[syllable_indexNP], (len(note_TestSet), 1, 1)).transpose(1, 0, 2)

print(f"colorSet_2D:{colorSet_2D.shape}")
print(f"colorSet_2D corrected:{colorSet_2D[:, -1].reshape(-1, 4).shape}")

ax.scatter(noteValues[:, :-1].flatten(), noteSpacingError.flatten(), noteDurationError[:, :-1].flatten(), c=colorSet_2D[:, :-1].reshape(-1, 4))
ax.set_xlabel('Note Value')
ax.set_ylabel('Note Spacing Error')
ax.set_zlabel('Note Duration Error')



from matplotlib.lines import Line2D
lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--') for c in colorSet]
labels = syllable_TestSet
plt.legend(lines, labels)



plt.show()