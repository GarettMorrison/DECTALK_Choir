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




def generateAnimation(trackNames, songTitle, settings_yaml, videoDims=(2560, 1440), freqRange=(100, 5000), divisionFactor = 500, framesPerSecond=30, barCount=100, back_color=[0, 0, 0], barGapFrac = 0.5):
    back_color = colorsys.hsv_to_rgb(back_color[0]/360, back_color[1]/100, back_color[2]/100)
    back_color = tuple([int(255*foo) for foo in back_color] )
    print(f"   back_color:{back_color}")
    
    labelFont = ImageFont.truetype('pyFuncs/fonts/NexaText-Trial-Light.ttf', 80)
    
    spectDict = {}
    for fooTrack in trackNames:
        print(f"\n{fooTrack}:")
        fooTrackDict = settings_yaml['Tracks'][fooTrack]
        # Convert input colors to HSV
        bar_color = fooTrackDict['VID_HSB']
        bar_color = colorsys.hsv_to_rgb(bar_color[0]/360, bar_color[1]/100, bar_color[2]/100)
        bar_color = tuple([int(255*foo) for foo in bar_color] )
        print(f"   bar_color:{bar_color}")



        
        # Load waveFile to process
        readWav = wavfile.read(f"outputs/{songTitle}/_tracks/{fooTrack}.wav")
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
        
        for yy in range(frameCount): # Process FFT to improve visuals
            fooFFt = adjustedSpectrogram[yy] # Load FFT for this time stamp
            fooFFt = np.abs(fooFFt) # Take absolute value
            fooFFt = np.sqrt(fooFFt) # Square root for nicer looking visual range
            # fooFFt = signal.savgol_filter(fooFFt, 10, 3) # Filter to prevent harsh edges
            adjustedSpectrogram[yy] = fooFFt

        # Find max at each spectrogram timestamp, sort maximums, and take index near the top to use as max
        specMax = np.max(adjustedSpectrogram, axis=1)
        specMax = specMax[np.where(specMax > 0.0)]
        specMax.sort()
        # print(specMax)
        divisionFactor = specMax[m.floor(len(specMax)*0.9  )] 
        print(f"   divisionFactor:{divisionFactor}")

        adjustedSpectrogram /= divisionFactor
        adjustedSpectrogram[np.where(adjustedSpectrogram > 1.0)] = 1.0

        fooPos = fooTrackDict['VID_Position']
        fooSpacing = videoDims[0]*fooPos[0]/(barCount+1)

        spectDict[fooTrack] = {
            'data':adjustedSpectrogram,
            'color':bar_color,
            'label': fooTrackDict['VID_Label'],
            'position': fooPos,
            'currFFT': deepcopy(adjustedSpectrogram[0]),
            'barDims': (fooSpacing, fooSpacing*barGapFrac, videoDims[1]*fooPos[0]/2, videoDims[0]*(fooPos[1]-fooPos[0]/2), videoDims[1]*fooPos[2]), # Order is spacing, bar width, maxHeight
            
            # # Calculate label size
            # 'labelText': fooTrackDict['VID_Label'],
            # 'labelDims': draw.textsize(labelText, font=labelFont),
            # labelPosition = ( (vidWidth-labelWidth)/2, 0.7*vidHeight -labelHeight/2)
        }

    # Setup video output
    vidWidth = videoDims[0]
    vidHeight = videoDims[1]

    # Setup video output
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')    
    outputFileName = f"outputs/{songTitle}/_finished/animation.mp4"
    video = cv2.VideoWriter(outputFileName, fourcc, framesPerSecond, videoDims)

    # Setup Pillow Image
    # Each frame is written to this image and then saved to video
    imtemp = Image.new("RGB", videoDims, (255, 255, 255))
    draw = ImageDraw.Draw(imtemp)


    # # Calculate variables for bar plot
    # maxHeight = vidHeight/2
    # barWidth = (vidWidth -edgeMargin*2)/barCount
    # barHalfGap = barWidth*barGapFrac/2

    # currFFT = None
    # Iterate over data
    # for yy in range(int(frameCount/10)):
    for yy in range(frameCount):
        print(f"Frame: {yy}\033[F") # Print current iteration to same line
        draw.rectangle((0, 0, vidWidth, vidHeight), fill=back_color) # Reset image

        for fooTrack in spectDict:
            fooDict = spectDict[fooTrack]

            if len(fooDict['data']) <= yy: continue
            currFFT = fooDict['currFFT']
            barSpace, barWidth, maxHeight, xLeftEdge, yCenter = fooDict['barDims']
            fooFFt = fooDict['data'][yy]

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
                    (((xx)*barSpace +xLeftEdge, yCenter-currFFT[xx]*maxHeight, (xx)*barSpace+barWidth +xLeftEdge, yCenter+currFFT[xx]*maxHeight)), 
                    fill=fooDict['color'])
                
                # if(currFFT[xx] > 0.5): print(((xx)*barSpace +xLeftEdge, currFFT[xx]*maxHeight+yCenter, (xx)*barSpace+barWidth +xLeftEdge, -currFFT[xx]*maxHeight+yCenter))
                

                # draw.ellipse(
                #     (xx*barWidth +barHalfGap+edgeMargin, maxHeight-maxHeight*ptValue, 
                #         (xx+1)*barWidth -barHalfGap+edgeMargin, maxHeight+maxHeight*ptValue), 
                #     fill=bar_color)
            
            fooDict['currFFT'] = currFFT

            # if max(currFFT) > 0.9: 
            #     imtemp.show()
                # input('PAUSED')
            
            # print(max(currFFT)*maxHeight)
            # currentTime = yy/framesPerSecond
            # if currentTime > trackSettingDict['VID_LabelTime'] and currentTime < trackSettingDict['VID_LabelTime'] +trackSettingDict["VID_LabelDur"] +trackSettingDict['VID_LabelFade']:
            #     textOpacity = 1.0
            #     if currentTime > trackSettingDict['VID_LabelTime'] +trackSettingDict["VID_LabelDur"]:
            #         # print("!!!!!!!!   ", end='')
            #         textOpacity =  ( 1 - (currentTime -trackSettingDict['VID_LabelTime'] -trackSettingDict["VID_LabelDur"])/trackSettingDict['VID_LabelFade'] )

            #         # print((currentTime -trackSettingDict['VID_LabelTime'] -trackSettingDict["VID_LabelDur"])/trackSettingDict['VID_LabelFade'])

            #     draw.text(labelPosition, labelText, (m.floor(bar_color[0] * textOpacity), m.floor(bar_color[1] * textOpacity), m.floor(bar_color[2] * textOpacity)), labelFont)

        video.write(cv2.cvtColor(np.array(imtemp), cv2.COLOR_RGB2BGR)) # Save frame

    video.release() # Output final video


    # Use ffmpeg to mix output audio and video to single, synced file
    print(f"Adding audio for final output")
    audioFileName = f"outputs/{songTitle}/_finished/{songTitle}.wav"
    finalFileName = f"outputs/{songTitle}/_finished/{songTitle}.mp4"
    import subprocess as sp
    sp.run(f"ffmpeg -y -i {outputFileName} -i {audioFileName} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {finalFileName}", shell=True)
