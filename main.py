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
from nicegui import ui


record = False
def toggle_record():
    global record
    global i
    i=0
    record = not record
    print(record)
    record_button.set_text('Stop' if record else 'Record')
    if record_button.clicked:
        i = i+1
    if i%2==1:
        main()
    else:
        return
    
        
record_button = ui.button('Record', on_click=lambda: toggle_record())

ui.run()


# Pitch detection 
concert_pitch = 440
notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
def detect_pitch(fundamental_frequency):
    semitone_freq = int(np.round(np.log2(fundamental_frequency/concert_pitch)*12)) 
    close_note = notes[semitone_freq%12] + str(abs(4+(semitone_freq+9) // 12))
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

    print(peak_frequencies)
    
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
    print("Recording audio")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    print("Recording finished")
    write("anything.wav", sample_rate, recording)

def desired_pitch(desired, close_note):
    if len(desired) == 2:
        dchar = desired[0]
        dnumber = desired[1]
    elif len(desired) == 3: 
        dchar = desired[0]
        dnumber = desired[2]
    if len(close_note) == 2:
        cchar = close_note[0]
        cnumber = close_note[1]
    elif len(close_note) == 3:
        cchar = close_note[0]
        cnumber = close_note[2]
    
    if desired == close_note:
        print("In Tune")
        return True
    elif dnumber < cnumber:
        print("Tune Lower")
    elif dnumber > cnumber: 
        print("Tune Higher")
    else:
        if dchar < cchar:
            print("Tune Lower")
        elif dchar > cchar:
            print("Tune Higher")
        else:
            if len(desired) > len(close_note):
                print("Tune Higher")
            elif len(desired) < len(close_note):
                print("Tune Lower")
    return False


def main():
    desired = input("Enter desired note (E2-E4): ") 
    global in_tune 
    in_tune = False
    
    while in_tune == False:
        print("audio_record()")
        audio_record()
        print("audio_import()")
        data, sample_rate = audio_import('anything.wav')
        print("find_peaks()")
        fundamental_frequency = find_fundamental(data, sample_rate)
        print("detect_pitch()")
        close_note, close_pitch = detect_pitch(fundamental_frequency)

        print(f"Close Note: {close_note}")
        print(f"Close Pitch: {close_pitch}")
        in_tune = desired_pitch(desired, close_note)
# main()