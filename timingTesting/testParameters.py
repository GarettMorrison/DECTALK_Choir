import numpy as np

sampleRate = 11025

voiceComm_TestSet = ['[:np]', '[:np][:dv hs 90]', '[:np][:dv hs 120]']
syllable_TestSet = ['dah', 'dax', 'hxae', 'duh', 'ae', 'mmaa', 'llao', ]
noteDur_TestSet = np.arange(10, 500, 40)
restDur_TestSet = np.arange(0, 2000, 200)


# voiceComm_TestSet = ['[:np]']
# syllable_TestSet = ['dah', 'dax']
# noteDur_TestSet = np.arange(10, 2000, 800)
# restDur_TestSet = np.arange(0, 1000, 400)

note_TestSet = np.arange(0, 24, 2)
