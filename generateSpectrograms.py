import math as m
import scipy
import numpy as np
from copy import deepcopy

import scipy.io.wavfile as wavfile
from scipy import signal
from matplotlib import pyplot as plt

import cv2
from cv2 import VideoWriter, VideoWriter_fourcc
from PIL import Image, ImageDraw

import sys
import os
import time

import pyFuncs.spectrogramAnimation as specAnimate


videoDimensions = (2560, 1440) # Width and height of video
framesPerSecond = 30 # Output FPS

# Make sure song is specified in command
if len(sys.argv) < 2:
    print('No song specified')
    exit()

songTitle = sys.argv[-1]

# Make sure specified song folder exists
if not songTitle in os.listdir('songs'):
    print(f'Songs folders found are:')
    for foo in os.listdir('songs'):
        print(f"   {foo}")
    print(f'Song {songTitle} not found')
    exit()

# Load settings.yaml from within folder
import yaml
try:
    file = open(f"songs/{songTitle}/settings.yaml", 'r')
    settings_yaml = yaml.safe_load(file)
except:
    print(f"songs/{songTitle}/settings.yaml NOT FOUND")
    exit()

# Folder for output files
os.makedirs(f"outputs/{songTitle}/_animation", exist_ok = True)

wavFileList = os.listdir(f"outputs/{songTitle}/_tracks/")
wavFileList = [foo.split('.')[0] for foo in wavFileList if '.wav' in foo]

trackList = [foo for foo in settings_yaml['Tracks']]

outputParts = []
ii=0
while ii<len(trackList):
    foo = trackList[ii]
    if foo in wavFileList:
        outputParts.append(foo)
        wavFileList.remove(foo)
        trackList.remove(foo)
    else: 
        ii+= 1

print(f"Only .wav:{wavFileList}")
print(f"Only settings:{trackList}")
print(f"outputParts:{outputParts}")

# Add default settings to dictionary if none found
for fooTrack in outputParts:
    trackDict = settings_yaml['Tracks'][fooTrack]
    if 'VID_HSB' not in trackDict: trackDict['VID_HSB'] = [0, 100, 100]
    if 'VID_Position' not in trackDict: trackDict['VID_Position'] = [0.5, 0.25, 0.25]
    if 'VID_Label' not in trackDict: trackDict['VID_Label'] = fooTrack
    if 'VID_LabelTime' not in trackDict: trackDict['VID_LabelTime'] = 0.0
    if 'VID_LabelDur' not in trackDict: trackDict['VID_LabelDur'] = 4.0
    if 'VID_LabelFade' not in trackDict: trackDict['VID_LabelFade'] = 1.0

# 
# for fooTrack in outputParts:
#     print(f"\nAnimating {fooTrack}")
#     wavFileName = f"outputs/{songTitle}/_tracks/{fooTrack}.wav"
#     outputFileName = f"outputs/{songTitle}/_animation/{fooTrack}.mp4"

backColor = [100, 0, 0]
specAnimate.generateAnimation(outputParts, songTitle, settings_yaml, videoDims=videoDimensions, framesPerSecond=30, back_color=backColor)

print("DONE!")
exit()

# # Setup video output
# outputFileName = f"outputs/{songTitle}/_finished/{songTitle}.mp4"
# fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# video = cv2.VideoWriter(outputFileName, fourcc, framesPerSecond, videoDimensions)


# clipSet = []
# for fooTrack in outputParts:
#     vidFileName = f"outputs/{songTitle}/_animation/{fooTrack}.mp4"
#     vid = cv2.VideoCapture(vidFileName)

#     trackSettings = settings_yaml['Tracks'][fooTrack]['VID_Position']
#     xPixelSize = int( videoDimensions[0]*trackSettings[0] )
#     yPixelSize = int( videoDimensions[1]*trackSettings[0] )
    
#     clipSet.append({
#         'vid': vid,
#         'size':(xPixelSize, yPixelSize),
#         'xStart': int(videoDimensions[0]*trackSettings[1]),
#         'yStart': int(videoDimensions[1]*trackSettings[2]),
#     })
#     # print(trackSettings)
#     # print(clipSet[-1])

# print("Compositing videos")
# ii = 0
# while(len(clipSet) > 0):
#     print(f"{ii}\033[F")
#     # print(f"{len(clipSet)}")
#     ii += 1
#     img = None
    
#     jj = 0
#     while jj < len(clipSet):
#         fooClip = clipSet[jj]
#         ret, frame = fooClip['vid'].read()
        
#         if not ret: 
#             clipSet.pop(jj)
#             continue

#         if type(img) != type(frame): img = np.zeros_like(frame)

#         # print(frame.shape)
        
#         imgResized = cv2.resize(frame, (fooClip['size']), interpolation = cv2.INTER_AREA)

#         # print('\n\n\n')
#         # print(f"imgResized.shape:{imgResized.shape}")
#         # print(f"fooClip['yStart']:{fooClip['yStart']}")
#         # print(f"fooClip['yStart']+fooClip['size'][1]:{fooClip['yStart']+fooClip['size'][1]}")
#         # print(f"fooClip['xStart']:{fooClip['xStart']}")
#         # print(f"fooClip['xStart']+fooClip['size'][0]:{fooClip['xStart']+fooClip['size'][0]}")

#         img[fooClip['yStart']:fooClip['yStart']+fooClip['size'][1], fooClip['xStart']:fooClip['xStart']+fooClip['size'][0]] = imgResized
#         jj += 1
        
#     video.write(img)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         cv2.destroyAllWindows()
#         break

# video.release()



# # Use ffmpeg to mix output audio and video to single, synced file
# print(f"Adding audio for final output")
# audioFileName = f"outputs/{songTitle}/_finished/{songTitle}.wav"
# finalFileName = f"outputs/{songTitle}/{songTitle}.mp4"
# import subprocess as sp
# sp.run(f"ffmpeg -y -i {outputFileName} -i {audioFileName} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {finalFileName}", shell=True)
