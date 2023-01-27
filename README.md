# DECTALK Choir
Making a retro speech synth sing! Able to work with polyphonic choral music. All written in Python3 and runs on Windows. Also generate spectrogram animation for the voices. 

## Background
Dectalk is a text to speech synthesizer released in 1983. It was famously used by Steven Hawking, and was included in the game Moonbase Alpha to read chat messages aloud. The system allows pronunciation phonemes, even inputting specific pitches and durations. Players of Moonbase Alpha quickly realized that these could be used to sing songs. I think this is absolutely delightful, and really wanted to play with this myself. Rather than copy-paste lines of text into the game, I tracked down a standard version of DECTalk and compiled it line by line. 

### Usage
Each song is saved in a folder under /songs. Before compilation, specify notes (.mid), lyrics (lyrics/*.txt), and settings (settings.yaml). Run choir.py to compile. 
choir.py Usage: python3 choir.py \[options\] \[songFolder\]
Example: 
> python3 choir.py -vis AuldLangSyne

Outputs will be saved to **/outputs** in a matching folder. One folder for each track will be generated, to save partial outputs.  **/\_tracks** contains each individual track's compiled output.  **/\_animation** contains the generated spectrogram animations for each track. Finally, **/\_finished** contains the final compiled audio and video. 

Three example songs are included, and I would recommend duplicating and modifying one of them instead of starting from scratch. 

### MIDI
In the song directory, choir.py will check for a single .mid file. I use LMMS to work with MIDI, but other software *should* be able to export compatible files. For each track in the song, there must be a corresponding MIDI track with a matching name. Each track should be monophonic, only playing one note at a time. Split chords into separate tracks. The only data used are note positions, timings, and velocity. 

### Lyrics
Lyrics should be saved as a .txt file in **/lyrics**. Lyrics are run one line at a time, so desync issues in playback can frequently be fixed by separating words into individual lines. Internally, words are split up into phonemes by **pyFuncs/PhonemeProcessing.py**. If a word can't be converted, try replacing it with a homophone. 
Lines starting with **\#** are comments and will be ignored. 
> # Start Repeat
Words starting with **`** are not split into phonemes, allowing very specific input if you're familiar with how DECtalk works. 
> 
If a word needs to be played across multiple notes, add *X before it to play X notes across it. The code will attempt to match syllables to notes. 
> *2 christmas is here

### Settings
Settings.yaml holds both general settings and per track settings. All settings are optional, and a default will be added by choir.py if none is specified. 

#### General Settings

**noteOffset**: DECtalk uses a different pitch encoding than MIDI, -48 should shift the pitches to match. This can also be tweaked to transpose songs into a playable range, as most voices only work from C2-C5. 

Consonants are played as separate phonemes. How long each consonant is played for can be tweaked with the following. 
**consonantFractionTarget**: The maximum time taken up by consonants across the whole word. 
**consonantMinMs**: Minimum time per consonant (mS)
**consonantMaxMs**: Maximum time per consonant (mS)

#### Per Track Audio Settings
**LYRICS_FILENAME**: Name of file to read lyrics from. Allows different parts to read from same lyrics file for simplicity. 
**VOLUME_ADJUST_DB**: Will adjust volume level of each track in decibels. Positive is louder, negative is quieter, and 0 is the same. I usually make higher tracks louder to be audible. 
**DEC_SETUP**: Add a bit of scripting to the beginning of each text file read by DECtalk to change settings. 
\[:np\] sets the voice to perfect paul, the most popular voice. Other voices include \[:np\] \[:nb\] \[:nh\] \[:nd\] \[:nf\] \[:nu\] \[:nr\] \[:nw\] & \[:nk\]
\[:dv hs 95\] changes the head size to be 95% standard. I usually increase head size for lower voices as I think it sounds better. 
There are a ton of other settings to play with that I haven't taken the time to learn, I've been mostly focused on the synchronization and playback. 



**TODO**

#### Per Track Animation Settings
**VID_HSB**
**VID_Position**
**VID_LabelDur**
**VID_LabelFade**