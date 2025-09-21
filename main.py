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


record = False

dark = ui.dark_mode()
dark.enable()
close_note = "A2"
global i, desired
i = 0

record_button = ui.button('Record', on_click=lambda: toggle_record()).style('margin: auto; width: 50%;')

with ui.card().classes('relative w-64 h-32 bg-blue-200'):
    
    note_icon = ui.icon('music_note', size='100px').style('margin: auto; width: 50%;').classes('absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-yellow-400 p-2')



ui.add_head_html('''
    <style>
        @keyframes slideLeft {
            100% { transform: translateX(-80%); }
        } 

        @keyframes slideRight {
            100% { transform: translateX(80%); }
        }
        
        @keyframes slideMiddle {
            100% { transform: translateX(0%); }
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
        
        .slide-across-left {
            animation: slideAcrossLeft 2s;
            animation-fill-mode: forwards;
        }
                 
        .slide-across-right {
            animation: slideAcrossRight 2s;
            animation-fill-mode: forwards;
        }
                 
    </style>
''')

def main():
    
    with ui.row().style('margin: auto; margin-top: 10px; width: 50%; justify-content: center; align-items: center;'):
        # left_select.value = ["E2", "A2", "D3"]
        left_select = ui.radio(["E2", "A2", "D3"]).bind_value(globals(), 'desired')
        note_label = ui.label(close_note).style('margin: auto; margin-top: 10px; text-align: center; font-size: 100px;')
        # right_select.value = ["G3", "B3", "E4"]
        right_select = ui.radio(["G3", "B3", "E4"]).bind_value(globals(), 'desired')
    ui.button('Submit', on_click=lambda: pitch_indentification(note_icon)).style('margin: auto; width: 50%;')

def toggle_record():
    global record
    i=0
    record = not record
    ui.label(record)
    record_button.set_text('Stop' if record else 'Record')
    if record_button.clicked:
        i = i+1
    if i%2==1:
        main()
    else:
        return
    
        

ui.run()


# Pitch detection 
concert_pitch = 440
notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
def detect_pitch(fundamental_frequency):
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


    #fig, ax = plt.subplots()
    #ax.plot(freqs, magnitude)
    #plt.show()

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
        # if note_icon.classes.contains("slide-right"):
        #     note_icon.classes(replace="slide-across-left")
        # else:
        note_icon.classes(replace='slide-middle')
        note_icon.classes(replace="slide-left")
    elif new_dir == "right":
        # if note_icon.classes.contains("slide-left"):
        #     note_icon.classes(replace="slide-across-right")
        # else:
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
        set_animation(note_icon, "middle")
        return True
    
    if dnumber < cnumber:
        ui.notify("Tune Down")
        set_animation(note_icon, "right")
    elif dnumber > cnumber: 
        ui.notify("Tune Up")
        set_animation(note_icon, "left")
    else:
        if dict[dchar] < dict[cchar]:
            ui.notify("Tune Down")
            set_animation(note_icon, "right")
        else:
            ui.notify("Tune Up")
            set_animation(note_icon, "left")
    return False

    
    # if len(desired) == 2:
    #     dchar = desired[0]
    #     dnumber = desired[1]
    # elif len(desired) == 3: 
    #     dchar = desired[0]
    #     dnumber = desired[2]
    # if len(close_note) == 2:
    #     cchar = close_note[0]
    #     cnumber = close_note[1]
    # elif len(close_note) == 3:
    #     cchar = close_note[0]
    #     cnumber = close_note[2]
    
    # if desired == close_note:
    #     ui.notify("In Tune")
    #     note_icon.classes(replace ='')
    #     note_icon.classes(add='slide-middle')
    #     return True
    # elif dnumber < cnumber:
    #     ui.notify("Tune Lower")
    #     note_icon.classes(replace = 'slide-middle')
    #     note_icon.classes(add='slide-right')
    # elif dnumber > cnumber: 
    #     ui.notify("Tune Higher")
    #     note_icon.classes(replace='')
    #     note_icon.classes(add='slide-left')
    # else:
    #     if dchar < cchar:
    #         ui.notify("Tune Lower")
    #         note_icon.classes(replace ='slide-middle')
    #         note_icon.classes(add='slide-right')
    #     elif dchar > cchar:
    #         ui.notify("Tune Higher")
    #         note_icon.classes(replace = 'slide-middle')
    #         note_icon.classes(add='slide-left')
    #     else:
    #         if len(desired) > len(close_note):
    #             ui.notify("Tune Higher")
    #             note_icon.classes(replace = 'slide-middle')
    #             note_icon.classes(add='slide-left')
    #         elif len(desired) < len(close_note):
    #             ui.notify("Tune Lower")
    #             note_icon.classes(replace ='slide-middle')
    #             note_icon.classes(add='slide-right')
    # return False



    
async def pitch_indentification(music_note):
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
        close_note, close_pitch = detect_pitch(fundamental_frequency)

        
        # ui.notify(f"Close Pitch: {close_pitch}")
        in_tune = desired_pitch(desired, close_note, music_note)
        if in_tune:
            ui.notify("In Tune", color='positive')
        await asyncio.sleep(0.1)
# main()