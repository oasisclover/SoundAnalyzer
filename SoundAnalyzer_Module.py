# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 10:46:06 2022

@author: Ryusei
"""

import numpy as np
import os

def A_filter_3octave(third_octave_FLAT):
                         #各バンドの中心周波数[Hz]
    A = np.array([-44.7, #25
                  -39.4, #31.5
                  -34.6, #40
                  -30.2, #50
                  -26.2, #63
                  -22.5, #80
                  -19.1, #100
                  -16.1, #125
                  -13.4, #160
                  -10.9, #200
                   -8.6, #250
                   -6.6, #315
                   -4.8, #400
                   -3.2, #500
                   -1.9, #630
                   -0.8, #800
                      0, #1000
                    0.6, #1250
                    1.0, #1600
                    1.2, #2000
                    1.3, #2500
                    1.2, #3150
                    1.0, #4000
                    0.5, #5000
                   -0.1, #6300
                   -1.1, #8000
                   -2.5, #10000
                   -4.3])#12500
    third_octave_A = np.array([[third_octave_FLAT[row, col] + A[row] for col in range(third_octave_FLAT.shape[1])] for row in range(third_octave_FLAT.shape[0])])
    
    return third_octave_A



def calc_overall(third_octave):
    
    n_samples = third_octave.shape[1]
    n_band = third_octave.shape[0]
    overall = np.zeros(n_samples)
    for col in range(0, n_samples, 1):
        for row in range(0, n_band, 1):
            overall[col] += 10**(third_octave[row, col]/10)
        overall[col] = 10*np.log10(overall[col])
    
    return overall



def A_filter_fft(f):
    
    if f[0] == 0:
        f[0] = 1e-6
    else:
        pass
    ra = (np.power(12194, 2) * np.power(f, 4)) / \
         ((np.power(f, 2) + np.power(20.6, 2)) * \
          np.sqrt((np.power(f, 2) + np.power(107.7, 2)) * \
                  (np.power(f, 2) + np.power(737.9, 2))) * \
          (np.power(f, 2) + np.power(12194, 2)))
    A_curve = 20 * np.log10(ra) + 2.00
    
    return A_curve



#オーバーラップ関数
def ov(data, samplerate, Fs, overlap):
    """
    https://watlab-blog.com/2019/04/17/python-overlap/
    """
    
    Ts = len(data) / samplerate
    Fc = Fs / samplerate
    x_ol = Fs * (1-(overlap/100))
    N_ave = int((Ts - (Fc * (overlap/100))) / (Fc * (1-(overlap/100))))
    array = []
    for i in range(N_ave):
        ps = int(x_ol * i)
        array.append(data[ps:ps+Fs:1])
        
    return array, N_ave



def Pa2dB(Pa):
    
    dB = 20*np.log10(Pa/20e-6)
    
    return dB



def connect_mp4_wav(mp4path, wavpath, outmp4path):
    
    os.system("ffmpeg -i {0} -i {1} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {2}".format(mp4path, wavpath, outmp4path))
    
    return


if __name__ == "__main__":
    mp4path = os.path.join(os.getcwd(), "mp4", "movie.mp4")
    wavpath = os.path.join(os.getcwd(), "wav", "sound1.wav")
    outmp4path = os.path.join(os.getcwd(), "mp4", "movie_sound.mp4")
    connect_mp4_wav(mp4path, wavpath, outmp4path)