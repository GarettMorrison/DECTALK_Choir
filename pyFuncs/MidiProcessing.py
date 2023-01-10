import mido

def loadMidiData(midiFileName, printInfo=True):
    fileTitle = midiFileName.split('/')[-1].split('.')[0]

    if printInfo: print(f"{midiFileName}  :  {fileTitle}")

    mid = mido.MidiFile(midiFileName)

    if printInfo: print(f'File mid: {mid.type}')

    notesByChannel = []
    trackNames = []

    active_notes = []
    active_times = []

    for channel, track in enumerate(mid.tracks):
        if printInfo: print('Track {}: {}'.format(channel, track.name))
        # channel = 0
        notesByChannel.append({
            'title':'loremIpsum',
            'tempo':-1,
            'note':[],
            'start':[],
            'end':[],
            })
        ii = 0

        currTime = 0
        for msg in track:
            if msg.type == 'track_name':
                if printInfo: print(f'   name:{msg}      {ii}')
                ii = 0
                trackNames.append(msg.name)
                notesByChannel[channel]['title'] = msg.name
                # channel += 1
                continue
            # print(f'   {msg}')
            
            if msg.type == 'set_tempo':
                if printInfo: print(f'   tempo:{msg}      {ii}')
                notesByChannel[channel]['tempo'] = msg.tempo
                continue

            if msg.type not in ['note_on', 'note_off']:
                if printInfo: print(f'   {msg}      {ii}')
                ii = 0
                continue
            
            
            ii += 1
            # channel = msg.channel
            
            # while(len(notesByChannel) <= channel):  # Add new channels

            # print(f'{len(notesByChannel)} | {channel}')
            # print(notesByChannel[channel])

            # print(msg)

            currTime += msg.time

            if msg.type == 'note_on': 
                active_notes.append( msg.note  )
                active_times.append( currTime )
            elif msg.note in active_notes:
                noteInd = active_notes.index(msg.note)

                notesByChannel[channel]['note'].append( msg.note )
                notesByChannel[channel]['start'].append( active_times[noteInd] )
                notesByChannel[channel]['end'].append( currTime )

                del active_notes[noteInd]
                del active_times[noteInd]
                # notesByChannel[channel]['note'].append( 255 )
    
    return(notesByChannel)