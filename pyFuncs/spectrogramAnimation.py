import math as m
import scipy
import numpy as np
from copy import deepcopy

import scipy.io.wavfile as wavfile
from scipy import signal
from matplotlib import pyplot as plt

import cv2
from cv2 import VideoWriter, VideoWriter_fourcc
from PIL import Image, ImageDraw, ImageFont
import colorsys




def generateAnimation(wavFileName, outputFileName, trackSettingDict, videoDims=(2560, 1440), freqRange=(100, 5000), divisionFactor = 500, framesPerSecond=30, barCount=100, bar_color=[0, 100, 100], back_color=[0, 0, 0]):
    # Convert input colors to HSV
    bar_color = colorsys.hsv_to_rgb(bar_color[0]/360, bar_color[1]/100, bar_color[2]/100)
    bar_color = tuple([int(255*foo) for foo in bar_color] )
    print(f"   bar_color:{bar_color}")

    back_color = colorsys.hsv_to_rgb(back_color[0]/360, back_color[1]/100, back_color[2]/100)
    back_color = tuple([int(255*foo) for foo in back_color] )
    print(f"   back_color:{back_color}")


    
    # Load waveFile to process
    readWav = wavfile.read(wavFileName)
    samplingRate = readWav[0]

    # Run spectrogram on waveFile
    procSpec = signal.spectrogram(readWav[1], samplingRate, window=('hamming'), nperseg=int(readWav[0]/framesPerSecond)) # nperseg gets close to target framesPerSecond

    # Calculate length of wav in seconds
    timeRange = procSpec[1][-1]
    print(f"   timeRange:{timeRange}")

    # Get just spectrogram data
    specData = procSpec[2]
    
    frameCount = int(timeRange*framesPerSecond)
    print(f"   frameCount:{frameCount}")

    # Interpolate spectrogram to match time domain to FPS
    fpsAdjustedSpec = np.zeros((len(specData), frameCount), dtype=np.float32)
    for ii in range(len(specData)):
        fpsAdjustedSpec[ii] = np.interp( np.arange(0, frameCount, 1), np.arange(0, frameCount, frameCount/len(specData[0])), specData[ii] )
    
    # Flip array so axis 0 is time and axis 1 is frequency
    fpsAdjustedSpec = np.transpose(fpsAdjustedSpec)

    # Get min and max index of frequency domain which matches freqRange
    freqDomain = procSpec[0]
    freqMinInd = (np.abs(freqDomain - freqRange[0])).argmin()
    freqMaxInd = (np.abs(freqDomain - freqRange[1])).argmin()

    print(f"   freq range: {freqMinInd}->{freqMaxInd} out of {len(fpsAdjustedSpec[ii])}")

    #  Interpolate spectrogram to match frequency domain barCount
    barAdjustedSpec = np.zeros((len(fpsAdjustedSpec), barCount), dtype=np.float32)
    for ii in range(len(fpsAdjustedSpec)):
        barAdjustedSpec[ii] = np.interp( 
            np.arange(barCount),
            np.arange(freqMinInd, freqMaxInd, (freqMaxInd-freqMinInd)/len(fpsAdjustedSpec[ii])), 
            fpsAdjustedSpec[ii] )

    adjustedSpectrogram = barAdjustedSpec

    specMax = [max(np.sqrt(np.abs(foo))) for foo in adjustedSpectrogram]
    specMax.sort()
    # print(specMax)
    divisionFactor = specMax[m.floor(len(specMax)*0.85  )]
    print(f"   divisionFactor:{divisionFactor}")

    # Setup video output
    edgeMargin = 20
    barGapFrac = 0.5
    vidWidth = videoDims[0]
    vidHeight = videoDims[1]

    # Setup video output
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')    
    video = cv2.VideoWriter(outputFileName, fourcc, framesPerSecond, videoDims)

    # Setup Pillow Image
    # Each frame is written to this image and then saved to video
    imtemp = Image.new("RGB", videoDims, (255, 255, 255))
    draw = ImageDraw.Draw(imtemp)

    # Calculate label size
    labelFont = ImageFont.truetype('pyFuncs/fonts/NexaText-Trial-Light.ttf', 80)
    labelText = trackSettingDict['VID_Label']
    labelWidth, labelHeight = draw.textsize(labelText, font=labelFont)
    labelPosition = ( (vidWidth-labelWidth)/2, 0.7*vidHeight -labelHeight/2)

    # Calculate variables for bar plot
    maxHeight = vidHeight/2
    barWidth = (vidWidth -edgeMargin*2)/barCount
    barHalfGap = barWidth*barGapFrac/2

    currFFT = None
    # for yy in range(int(frameCount/5)):
    for yy in range(frameCount):
        print(f"{yy}\033[F") # Print current iteration to same line
        draw.rectangle((0, 0, vidWidth, vidHeight), fill=back_color) # Reset image

        fooFFt = adjustedSpectrogram[yy] # Load FFT for this time stamp
        fooFFt = np.abs(fooFFt) # Take absolute value
        fooFFt = np.sqrt(fooFFt) # Square root for nicer looking visual range
        # fooFFt = signal.savgol_filter(fooFFt, 10, 3) # Filter to prevent harsh edges
        fooFFt /= divisionFactor # Scale input range to 0.0 -> 1.0

        if type(currFFT) != type(fooFFt): currFFT = deepcopy(fooFFt) # Setup currFFT on first loop

        # Process each bar
        for xx in range(barCount):
            # Smooths data in time domain, preventing sharp drop offs
            currFFT[xx] /= 1.4
            if currFFT[xx] < fooFFt[xx]: currFFT[xx] = fooFFt[xx]
            
            # Load value for bar and clamp
            ptValue = currFFT[xx]
            if ptValue > 1.0: ptValue = 1.0
            if ptValue < 0.001: ptValue = 0.001 

            # Actually draw bar
            draw.ellipse(
                (xx*barWidth +barHalfGap+edgeMargin, maxHeight-maxHeight*ptValue, 
                    (xx+1)*barWidth -barHalfGap+edgeMargin, maxHeight+maxHeight*ptValue), 
                fill=bar_color)
                
        currentTime = yy/framesPerSecond
        if currentTime > trackSettingDict['VID_LabelTime'] and currentTime < trackSettingDict['VID_LabelTime'] +trackSettingDict["VID_LabelDur"] +trackSettingDict['VID_LabelFade']:
            textOpacity = 1.0
            if currentTime > trackSettingDict['VID_LabelTime'] +trackSettingDict["VID_LabelDur"]:
                # print("!!!!!!!!   ", end='')
                textOpacity =  ( 1 - (currentTime -trackSettingDict['VID_LabelTime'] -trackSettingDict["VID_LabelDur"])/trackSettingDict['VID_LabelFade'] )

                # print((currentTime -trackSettingDict['VID_LabelTime'] -trackSettingDict["VID_LabelDur"])/trackSettingDict['VID_LabelFade'])

            draw.text(labelPosition, labelText, (m.floor(bar_color[0] * textOpacity), m.floor(bar_color[1] * textOpacity), m.floor(bar_color[2] * textOpacity)), labelFont)

        video.write(cv2.cvtColor(np.array(imtemp), cv2.COLOR_RGB2BGR)) # Save frame

    video.release() # Output final video