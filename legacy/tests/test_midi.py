import mido

mid=mido.MidiFile()
trk=mido.MidiTrack()
mid.tracks.append(trk)
trk.append(mido.Message('note_on',note=60,velocity=64,time=0))
trk.append(mido.Message('note_off',note=60,velocity=64,time=480))
mid.save('test.mid')

scale = '1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm'

mid2 = mido.MidiFile('test.mid')
current_time = 0.0
for msg in mid2:
    current_time += msg.time
    if getattr(msg, 'type', '') in ('note_on', 'note_off'):
        map_idx = msg.note - 36
        if 0 <= map_idx < len(scale):
            char = scale[map_idx]
            if msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                print(f"{current_time:.4f} ~{char}")
            else:
                print(f"{current_time:.4f} {char}")
