import cmudict
cmu_dict = cmudict.dict()

# DECTALK_Arpabet_Phonemes = ["_", "@", "&", "^", "|", "a", "A", "b", "B", "c", "C", "d", "D", "D", "E", "e", "f", "g", "G", "h", "I", "i", "J", "j", "K", "k", "L", "l", "l", "m", "M", "N", "n", "o", "O", "P", "p", "q", "Q", "r", "R", "R", "s", "S", "t", "T", "U", "u", "v", "W", "w", "x", "Y", "y", "z", "Z", "_", "ae", "dx", "ah", "ix", "aa", "ay", "b", "ir", "ao", "ch", "d", "dh", "dz", "eh", "ey", "f", "g", "nx", "hx", "ih", "iy", "jh", "ur", "er", "k", "el", "ll", "lx", "m", "or", "en", "n", "ow", "oy", "ar", "p", "eat", "tx", "r", "rr", "rx", "s", "sh", "t", "th", "uh", "uw", "v", "aw", "w", "ax", "yu", "yx", "z", "zh", ]

DECTALK_Arpabet_Conversions = {
    'hh': 'hx',
    'y':'yx',
}


def convertWordToPhonemes(fooWord, convertLowercase=True, DECTALK_check=True):
    outPhonemes = cmu_dict[fooWord] 
    if len(outPhonemes) == 0: return([])
    outPhonemes = outPhonemes[-1]
    
    for ii in range(len(outPhonemes)):
        if convertLowercase: outPhonemes[ii] = outPhonemes[ii].lower()

        if DECTALK_check:
            if outPhonemes[ii] in DECTALK_Arpabet_Conversions:
                print(f"      DECTALK Arpabet conversion {outPhonemes[ii]} -> {DECTALK_Arpabet_Conversions[outPhonemes[ii]]}")
                outPhonemes[ii] = DECTALK_Arpabet_Conversions[outPhonemes[ii]]
    
    return(outPhonemes)


def lyricsToPhonemes(lyricsFileName, printInfo=True, convertLowercase=True, DECTALK_check=True):
    outLyrics = []
    readLyrics = open(lyricsFileName, 'r')
    currentLineIndex = -1
    lyricRepetitions = 1
    for fooLine in readLyrics.readlines(): # Iterate over lines in lyric files
        currentLineIndex += 1
        if fooLine[0] == '#': continue # Skip line if it's a comment
        splt = fooLine[:-1].lower().split(' ') # Split line into words
        
        currentLinePhonemes = []
        for fooWord in splt:    # Iterate over words in line
            if len(fooWord) == 0: continue  # If fooWord has no characters, skip
            
            if fooWord[0] == '!': # !X Indicates to repeat the following line X times
                try: lyricRepetitions = int(fooWord.split('!')[-1])
                except:
                    print(f"Error converting \"{fooWord}\" to repeat lyrics   (line {currentLineIndex})")
                    exit()
                continue

            elif fooWord[0] == '`':   # ` indicates to load syllable directly without modification
                outPhonemes = fooWord

            elif '*' in fooWord:    # * indicates that the word should be played for multiple notes per syllable
                splitWord = fooWord.split('*')
                outPhonemes = convertWordToPhonemes(splitWord[-1])
                
                if len(outPhonemes) == 0:
                    print(f"ERROR: Unable to match \"{fooWord}\" to phonemes in {lyricsFileName}   (line {currentLineIndex})")
                    exit()
                
                try: outPhonemes = [int(splitWord[0])] + outPhonemes
                except:
                    print(f"Error converting \"{fooWord}\" to repeat lyrics   (line {currentLineIndex})")
                    exit()
                

            elif '|' in fooWord:    # X|Y|Z|lyric indicates notes per specific syllables
                splitWord = fooWord.split('|')
                outPhonemes = convertWordToPhonemes(splitWord[-1])


                if len(outPhonemes) == 0:
                    print(f"ERROR: Unable to match \"{fooWord}\" to phonemes in {lyricsFileName}   (line {currentLineIndex})")
                    exit()
                
                try:
                    outPhonemes = [[int(foo) for foo in splitWord[:-1]]] + outPhonemes
                except:
                    print(f"ERROR: Unable to converting \"{fooWord}\" to phonemes in {lyricsFileName}   (line {currentLineIndex})")
                    
            else:   # No special case, convert directly
                outPhonemes = convertWordToPhonemes(fooWord)

                if len(outPhonemes) == 0:
                    print(f"ERROR: Unable to match \"{fooWord}\" to phonemes in {lyricsFileName}   (line {currentLineIndex})")
                    exit()
            
            currentLinePhonemes.append(outPhonemes)
            if printInfo: print(f"{fooWord} -> {currentLinePhonemes[-1]}")
        
        if printInfo: print('')
        currentLinePhonemes.append(['\n'])

        for ii in range(lyricRepetitions):
            outLyrics = outLyrics + currentLinePhonemes
            
        lyricRepetitions = 1
    
    return(outLyrics)


def savePhonemesToFile(phonemes, fileName):
    outFile = open(fileName, 'w')
    
    for foo in phonemes:
        for bar in foo:
            outFile.write(f"{bar} ")
        outFile.write('     ')
    
    outFile.close()



def loadPhonemesFromFile(fileName):
    inFile = open(fileName, 'r')

    phonemes = []
    for readline in inFile.readlines():
        lineSplt = readline.split('      ')[1:]

        if len(lineSplt) == 1:
            phonemes.append(['\n'])
        else:
            for foo in lineSplt[:-1]:
                phonemes.append(foo.split(' '))
    
    inFile.close()