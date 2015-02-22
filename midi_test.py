from midiutil.MidiFile3 import MIDIFile

midi = MIDIFile(1)

track = 0
time = 0

midi.addTrackName(track,time,'sample')
midi.addTempo(track,time,120)

track = 0
channel = 0
pitch = 60
time = 10
duration = 1
volume = 100

# Now add the note.
midi.addNote(track,channel,pitch,time,duration,volume)

# And write it to disk.
binfile = open("output.mid", 'wb')
midi.writeFile(binfile)
binfile.close()