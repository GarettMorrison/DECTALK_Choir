import cmudict

# DECTALK_Arpabet_Phonemes = ["_", "@", "&", "^", "|", "a", "A", "b", "B", "c", "C", "d", "D", "D", "E", "e", "f", "g", "G", "h", "I", "i", "J", "j", "K", "k", "L", "l", "l", "m", "M", "N", "n", "o", "O", "P", "p", "q", "Q", "r", "R", "R", "s", "S", "t", "T", "U", "u", "v", "W", "w", "x", "Y", "y", "z", "Z", "_", "ae", "dx", "ah", "ix", "aa", "ay", "b", "ir", "ao", "ch", "d", "dh", "dz", "eh", "ey", "f", "g", "nx", "hx", "ih", "iy", "jh", "ur", "er", "k", "el", "ll", "lx", "m", "or", "en", "n", "ow", "oy", "ar", "p", "eat", "tx", "r", "rr", "rx", "s", "sh", "t", "th", "uh", "uw", "v", "aw", "w", "ax", "yu", "yx", "z", "zh", ]

DECTALK_Arpabet_Conversions = {
    'hh': 'hx'
}


def lyricsToPhonemes(lyricsFileName, printInfo=True, convertLowercase=True, DECTALK_check=False):
    outLyrics = []
    readLyrics = open(lyricsFileName, 'r')
    for fooLine in readLyrics.readlines():
        splt = fooLine[:-1].lower().split(' ')

        for fooWord in splt:
            if len(fooWord) == 0: continue
            if fooWord[0] == '*': # * indicates that the next word hase multiple notes per syllable
                outLyrics.append(fooWord)
            else:
                outPhonemes = cmudict.dict()[fooWord][-1]
                
                for ii in range(len(outPhonemes)):
                    if convertLowercase: outPhonemes[ii] = outPhonemes[ii].lower()

                    if DECTALK_check:
                        if outPhonemes[ii] in DECTALK_Arpabet_Conversions:
                            print(f"DECTALK Arpabet conversion {outPhonemes[ii]} -> {DECTALK_Arpabet_Conversions[outPhonemes[ii]]}")
                            outPhonemes[ii] = DECTALK_Arpabet_Conversions[outPhonemes[ii]]

                        
                outLyrics.append(outPhonemes)
            # print('\n')
            if printInfo: print(f"{fooWord} -> {outLyrics[-1]}")
        
        if printInfo: print('')
        outLyrics.append(['\n'])
    
    return(outLyrics)