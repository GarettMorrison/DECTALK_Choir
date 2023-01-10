# Convert lyrics and midi to playable demo

# Load Lyrics and convert to phonemes
import pyFuncs.PhonemeProcessing as pp

lyricsFile = "Lyrics.txt"
phonemes = pp.lyricsToPhonemes(lyricsFile, DECTALK_check=True)

# exit()



# Load MIDI data
import pyFuncs.MidiProcessing as pymidi

midiName = "FlyMeToTheMoon"
lyricTrackName = "Vocals"
midiData = pymidi.loadMidiData("MIDI/" + midiName + ".mid", printInfo=False )
noteOffset = -48

# Convert midi data to notes and durations
pitchOffset = 0

notes = []
durations = []
for fooMidi in midiData:
    if fooMidi['title'] != lyricTrackName: continue

    tempo_ms = fooMidi['tempo']/1000

    prevNote = 0
    for ii in range(len(fooMidi['note'])):
        if fooMidi['start'][ii] > prevNote:
            notes.append([-1, (fooMidi['start'][ii] - prevNote) * tempo_ms/128])


        notes.append([fooMidi['note'][ii] + pitchOffset, (fooMidi['end'][ii] - fooMidi['start'][ii]) * tempo_ms/128 ])
        
        
        prevNote = fooMidi['end'][ii]


# print("MIDI NOTES:")
# for ii in range(len(notes)):
#     print(f"{notes[ii][0]} : {notes[ii][1]}")



# Actually write demo output

demoOutTxt = open("demo.txt", 'w')
# demoOutTxt.write("[:phoneme arpabet speak on]\n[")

demoOutTxt.write("[:phone arpa on][:np][\n")



lyricIndex = 0
noteIndex = 0
while lyricIndex < len(phonemes) and noteIndex < len(notes):
    # If lyric is newline
    if phonemes[lyricIndex][0] == '\n':
        print('\n------------------------\n')
        demoOutTxt.write("]\n[")
        lyricIndex += 1
        continue
    
    # If lyric is indicating multiple notes in next word
    if phonemes[lyricIndex][0] == '*':
        notesInWord = int(phonemes[lyricIndex][1:])
        lyricIndex += 1
    else:
        notesInWord = 1
    
    print('\n')
    print(notesInWord)

    # Iterate through symbols in word and process
    symbolIndex = 0
    while notesInWord > 0:
        symbolsToSing = []
        isSymbolVowel = []
        
        while symbolIndex < len(phonemes[lyricIndex]):
            if phonemes[lyricIndex][symbolIndex][-1].isnumeric(): # If last character in syllable is vowel, symbol is a vowel
                symbolsToSing.append(phonemes[lyricIndex][symbolIndex][:-1]) # Drop number at end of vowel
                isSymbolVowel.append(1)

                notesInWord -= 1
                if notesInWord > 0: # If more notes are to be played in word, stop here and output this syllable
                    symbolIndex += 1
                    break
            else:
                symbolsToSing.append(phonemes[lyricIndex][symbolIndex])
                isSymbolVowel.append(0)
            
            symbolIndex += 1

        # Load note information
        noteValue = notes[noteIndex][0]
        noteDuration = notes[noteIndex][1]
        noteIndex += 1

        if noteValue == -1: # If note is rest, write pause
            demoOutTxt.write(f"_<{round(noteDuration)},0>")
            print(f"REST:{noteDuration}")
            noteValue = notes[noteIndex][0]
            noteDuration = notes[noteIndex][1]
            noteIndex += 1

        print(f"NOTE:{noteValue}->{noteValue+noteOffset}   {round(noteDuration,3)}")
        noteValue += noteOffset


        vowelCount = sum(isSymbolVowel)
        consonantCount = len(isSymbolVowel) - sum(isSymbolVowel)
        print(f"vowelCount:{vowelCount}    consonantCount:{consonantCount}")

        if consonantCount == 0 or vowelCount == 0: # If word does not have vowels or consonants catch divide by 0 error
            consonantDuration = round(consonantCount / (consonantCount + vowelCount))
            consonantFraction = consonantDuration
            vowelDuration = round(vowelCount / (consonantCount + vowelCount))
        else:
            consonantFraction = 0.4 - pow(0.4, consonantCount+1)
            consonantDuration = round(noteDuration * consonantFraction / consonantCount)
            vowelDuration = round(noteDuration * (1-consonantFraction) / vowelCount)

            print(f"consonantFraction:{round(consonantFraction, 3)}    consonantDuration:{consonantDuration}    vowelDuration:{vowelDuration}    ")



        for ii in range(len(symbolsToSing)):
            if isSymbolVowel[ii]: symbolString = f"{symbolsToSing[ii]}<{vowelDuration},{noteValue}>"
            else: symbolString = f"{symbolsToSing[ii]}<{consonantDuration},{noteValue}>"

            print(symbolString)

            demoOutTxt.write(symbolString)
        
        print('')

    lyricIndex += 1
    demoOutTxt.write(" ")
    
    
    
demoOutTxt.write("]")


import subprocess
subprocess.run("klattclassic/dectalk classic.exe")