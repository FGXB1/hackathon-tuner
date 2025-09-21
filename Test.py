# # 1. Get audio input (file or microphone)
# # 2. Pitch detection
# # 3. Compare with defined pitches (EADGBE) -- FFT

# import numpy as np
# import matplotlib.pyplot as plt
# import soundfile as sf 
# import sounddevice as sd
# from scipy.signal import find_peaks
# from scipy import fft
# import math
# from scipy.io.wavfile import write
# import wave

# # Pitch detection 
# concert_pitch = 440
# notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
# def detect_pitch(fundamental_frequency):
#     semitone_freq = int(np.round(np.log2(fundamental_frequency/concert_pitch)*12)) 
#     close_note = notes[semitone_freq%12] + str(abs(4+(semitone_freq+9) // 12))
#     close_pitch = concert_pitch*2**(semitone_freq/12)
#     return close_note, close_pitch

# # Audio inputs
# def audio_import(audio_file):
#     data, sample_rate = sf.read(audio_file)       

#     if len(data.shape) > 1:                #Convert stereo to monotone if needed
#          data = data.mean(axis = 1)
    
#     return data, sample_rate

# # Find peaks in audio frequency
# def find_fundamental(data, sample_rate): 
#     fft_data = np.fft.rfft(data)  #Coverts audio file to frequency spectrum
#     magnitude = np.abs(fft_data)  

#     freqs = np.fft.rfftfreq(len(data), 1/sample_rate) 

#     peak_indices, properties = find_peaks(magnitude, height = np.max(magnitude)*.1)

#     peak_frequencies = freqs[peak_indices]
#     peak_magnitudes = magnitude[peak_indices]

#     frequency_peaks = list(peak_frequencies)


#     for i in range(len(peak_frequencies)):
#         frequency_peaks[i] = int(peak_frequencies[i])

#     print(peak_frequencies)
    
#     if len(frequency_peaks)>0:
#         fundamental_frequency_idx = peak_indices[0]
#         fundamental_frequency = freqs[fundamental_frequency_idx]


#     #fig, ax = plt.subplots()
#     #ax.plot(freqs, magnitude)
#     #plt.show()

#     return fundamental_frequency

# # Audio recording
# def audio_record():
#     sample_rate = 44100
#     duration = 3
#     print("Recording audio")
#     recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
#     sd.wait()
#     print("Recording finished")
#     write("anything.wav", sample_rate, recording)

# def desired_pitch(desired, close_note):
#     if desired == close_note:
#         print("In Tune")
#         return True
#     elif desired[1] < close_note[1]:
#         print("Tune Lower")
#     elif desired[1] > close_note[1]: 
#         print("Tune Higher")
#     else:
#         if desired[0]< close_note[0]:
#             print("Tune Lower")
#         elif desired[0]> close_note[0]:
#             print("Tune Higher")
#     return False
            



# def main():
#     # if __name__ == '__main__':
    
    
#     print("audio_record()")
#     audio_record()
#     print("audio_import()")
#     data, sample_rate = audio_import('anything.wav')
#     print("find_peaks()")
#     fundamental_frequency = find_fundamental(data, sample_rate)
#     print("detect_pitch()")
#     close_note, close_pitch = detect_pitch(fundamental_frequency)

#     print(f"Close Note: {close_note}")
#     print(f"Close Pitch: {close_pitch}")
#     in_tune = desired_pitch(desired, close_note)

# in_tune = False
# print("Hello")
# desired = input("Enter desired note (E2-E4): ") 
# while in_tune == False:
#     main()