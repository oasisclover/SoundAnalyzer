# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 17:15:33 2022

@author: Ryusei
"""

import numpy as np
from scipy.io.wavfile import write
from scipy.io.wavfile import read

def CutFreq(filepath_input, filepath_output, freq_range):
    """
    Parameters
    ----------
    filepath_input : string
        file path of input wav files
    filepath_output : string
        file path of output wav files
    freq_range : list, size=2
        the range of frequency that you want to cut
        ex) if you want to ccut between 100Hz and 1000Hz, freq_range = [100, 1000]

    Returns
    -------
    **create wav files that is cut between freqency you specify

    """
    
    # サンプリング数定義
    N = 48000
    
    # wavファイル読み込み
    rate, data = read(filepath_input)
    
    # 縦軸:dataを高速フーリエ変換する
    fft_data = np.fft.fft(data)
    
    # 横軸:周波数の取得
    freqList = np.fft.fftfreq(data.shape[0], d=1/rate)
    
    # 正規化 +　交流成分2倍
    fft_data = fft_data/(N/2) #サンプル数/2
    fft_data[0] = fft_data[0]/2
    
    # 配列fft_dataをコピー
    fft_data2 = fft_data.copy()
    
    #指定された周波数帯域以外は0値化
    fft_data2[(freqList < freq_range[0])] = 0 #highpass
    fft_data2[(freqList > freq_range[1])] = 0 #lowpass
    
    # 高速逆フーリエ変換
    data2 = np.fft.ifft(fft_data2)
    
    # 振幅を元のスケールに戻す
    data2 = np.real(data2*N)
    
    # wav出力のためにfloat型をint16に変換
    data2 = data2.astype(np.int16)
    
    # wavデータ書き出し
    write(filepath_output, rate, data2)
    return



if __name__ == "__main__":
    
    import os
    import tkinter as tk
    import tkinter.filedialog
    
    # =============================================================================
    #     入力値
    # =============================================================================
    freq_range = [100, 1000] #切り取る周波数範囲
    
    
    folder_output = os.join(os.getcwd(), "output")
    root = tk.Tk()
    root.withdraw()
    filepath_wav_input_list = tkinter.filedialog.askopenfilename(
        title = "指定した周波数範囲で切り取りたい音源データ（*.wav）を選択してください",
        filetypes = [("WAV files", "*.wav")],
        multiple = True)
    
    if len(filepath_wav_input_list) != 0:
        for filepath_wav_input in filepath_wav_input_list:
            CutFreq(filepath_wav_input, folder_output, freq_range)
    else:
        print("FreqCut module is canceled")