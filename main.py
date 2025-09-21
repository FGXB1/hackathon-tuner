# 1. Get audio input (file or microphone)
# 2. Pitch detection
# 3. Compare with defined pitches (EADGBE) -- FFT

import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf 
import sounddevice as sd
from scipy.signal import find_peaks
from scipy import fft
import math
from scipy.io.wavfile import write
import wave
import asyncio
from nicegui import tailwind, ui
from pygame import mixer

mixer.init()
tune_up = mixer.Sound("TuneHigher.wav")
tune_down = mixer.Sound("TuneLower.wav")
tune_in = mixer.Sound("InTune.dat.wav")


record = False

CELESTIAL = {
    'dark': '#0A0A12',
    'deep_blue': '#2C355C',
    'mid_blue': '#464C7E',
    'purple': '#8B6C8E',
    'lavender': '#E4CED3',
}

dark = ui.dark_mode()
dark.enable()
ui.query('body').style(f'background-color: #101426;')
close_note = "A2"
global i, desired
i = 0

record_button = ui.button('Record', on_click=lambda: toggle_record(), color=CELESTIAL["purple"]).style(f'''
    margin: auto;
    margin-top: 100px;
    width: 50%;
    border-radius: 12px;
''')

with ui.card().classes('relative w-64 h-5 bg-blue-200').style(\
    f'margin: auto; margin-top: 40px; width: 50%; \
    background: #000000;\
    background: linear-gradient(\
    90deg, rgba(0, 0, 0, 1) 0%, rgba(36, 44, 83, 1) 18%,\
        rgba(147, 115, 156, 1) 35%,\
        rgba(235, 212, 218, 1) 53%, \
        rgba(147, 115, 156, 1) 67%, \
        rgba(36, 44, 83, 1) 82%, \
        rgba(0, 0, 0, 1) 100%);'\
):
    note_icon = ui.icon('music_note', size='100px').style(f'margin: auto; width: 50%; color: #E3D1E8;').classes('absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 p-2')

ui.add_head_html('''
    <style>
        @keyframes slideLeft {
            from { transform: translateY(-50%) }
            to { transform: translateX(-100%) translateY(-50%); }
        } 

        @keyframes slideRight {
            from { transform: translateY(-50%) }
            to { transform: translateX(100%) translateY(-50%); }
        }
        
        @keyframes slideMiddle {
            from { transform: translateY(-50%) }
            to { transform: translateX(0%) translateY(-50%); }
        }

        .slide-left {       
            animation: slideLeft 2s;
            animation-fill-mode: forwards;
        }
                          
        .slide-right {
            animation: slideRight 2s;
            animation-fill-mode: forwards;
        }
        
        .slide-middle {
            animation: slideMiddle 2s;
            animation-fill-mode: forwards;
        }
                 
        input[type="radio"] {
            accent-color: #E4CED3l;    
        }
    </style>
''')

def main():
    
    with ui.row().style(f'margin: auto; margin-top: 10px; width: 50%; justify-content: center; align-items: center;'):
        # select_note.value = ["E2", "A2", "D3"]
        note_label = ui.label(close_note).style(f'margin: auto; text-align: center; font-size: 100px; color: {CELESTIAL["lavender"]};')
        select_note = ui.radio(["E2", "A2", "D3", "G3", "B3", "E4"]).props("inline").bind_value(globals(), 'desired').style(f'accent-color: {CELESTIAL["lavender"]};')
    ui.button('Tune', on_click=lambda: pitch_indentification(note_icon, note_label), color=CELESTIAL["purple"]).style(f'margin: auto; width: 50%; border-radius: 12px;')

def toggle_record():
    global record
    i = 0
    record = not record
    ui.label(record)
    record_button.set_text('Stop' if record else 'Record')
    if record_button.clicked:
        i = i + 1
    if i % 2 == 1:
        main()
    else:
        return
    
ui.run()

# Pitch detection 
concert_pitch = 440
notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
def detect_pitch(fundamental_frequency, note_label):
    semitone_freq = int(np.round(np.log2(fundamental_frequency/concert_pitch)*12)) 
    close_note = notes[semitone_freq%12] + str(abs(4+(semitone_freq+9) // 12))
    note_label.text = close_note
    close_pitch = concert_pitch*2**(semitone_freq/12)
    return close_note, close_pitch

# Audio inputs
def audio_import(audio_file):
    data, sample_rate = sf.read(audio_file)       

    if len(data.shape) > 1:                #Convert stereo to monotone if needed
         data = data.mean(axis = 1)
    
    return data, sample_rate

# Find peaks in audio frequency
def find_fundamental(data, sample_rate): 
    fft_data = np.fft.rfft(data)  #Coverts audio file to frequency spectrum
    magnitude = np.abs(fft_data)  

    freqs = np.fft.rfftfreq(len(data), 1/sample_rate) 

    peak_indices, properties = find_peaks(magnitude, height = np.max(magnitude)*.1)

    peak_frequencies = freqs[peak_indices]
    peak_magnitudes = magnitude[peak_indices]

    frequency_peaks = list(peak_frequencies)


    for i in range(len(peak_frequencies)):
        frequency_peaks[i] = int(peak_frequencies[i])

    # ui.label(peak_frequencies)
    
    if len(frequency_peaks)>0:
        fundamental_frequency_idx = peak_indices[0]
        fundamental_frequency = freqs[fundamental_frequency_idx]

    return fundamental_frequency

# Audio recording
def audio_record():
    sample_rate = 44100
    duration = 3        
    # ui.label("Recording audio")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    # ui.label("Recording finished")
    write("anything.wav", sample_rate, recording)

def set_animation(note_icon, new_dir):
    if new_dir == "middle":
        note_icon.classes(replace="slide-middle")
        return

    if new_dir == "left":
        note_icon.classes(replace='slide-middle')
        note_icon.classes(replace="slide-left")
    elif new_dir == "right":
        note_icon.classes(replace='slide-middle')
        note_icon.classes(replace="slide-right")



def desired_pitch(desired, close_note, note_icon):
    dict = {"C":1, "C#":2, "D":3, "D#":4, "E":5, "F":6, "F#":7, "G":8, "G#":9, "A":10, "A#":11, "B":12}
    
    if len(desired) == 2:
        dchar = desired[0]
        dnumber = int(desired[1])
    elif len(desired) == 3:
        dchar = desired[0:2]
        dnumber = int(desired[2])
    if len(close_note) == 2:
        cchar = close_note[0]
        cnumber = int(close_note[1])
    elif len(close_note) == 3:
        cchar = close_note[0:2]
        cnumber = int(close_note[2])
    if desired == close_note:
        ui.notify("In Tune")
        tune_in.play()
        set_animation(note_icon, "middle")
        return True
    
    if dnumber < cnumber:
        ui.notify("Tune Down")
        tune_down.play()
        set_animation(note_icon, "right")
    elif dnumber > cnumber: 
        ui.notify("Tune Up")
        tune_up.play()
        set_animation(note_icon, "left")
    else:
        if dict[dchar] < dict[cchar]:
            ui.notify("Tune Down")
            tune_down.play()
            set_animation(note_icon, "right")
        else:
            ui.notify("Tune Up")
            tune_up.play()
            set_animation(note_icon, "left")
    return False

async def pitch_indentification(music_note, note_label):
    global in_tune 
    in_tune = False
    while not in_tune:
        # ui.notify("audio_record()")
        audio_record()
        # ui.notify("audio_import()")
        data, sample_rate = audio_import('anything.wav')
        # ui.notify("find_peaks()")
        fundamental_frequency = find_fundamental(data, sample_rate)
        # ui.notify("detect_pitch()")
        close_note, close_pitch = detect_pitch(fundamental_frequency, note_label)
        
        # ui.notify(f"Close Pitch: {close_pitch}")
        in_tune = desired_pitch(desired, close_note, music_note)
        if in_tune:
            ui.notify("In Tune", color='positive')
        await asyncio.sleep(1)
# main()