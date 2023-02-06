# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 11:11:21 2022

@author: Ryusei
"""


import sys
from pydub import AudioSegment
import datetime


def CutWav(filepath_wav_input, filepath_wav_output, t_start, t_end):
    """
    Parameters
    ----------
    filepath_wav_input : string
        the wav file path you want to cut along time
    fileapth_wav_output : string
        the file path of cut wav file
    t_start : datetime.time
        the time of start point in the time range you want to cut
    t_end : datetime.time
        the time of end point in the time range you want to cut
        
    Raises
    -------
    ValueError
        if the data types of time_start and time_end as input argument is not datetime.time, raise ValueError
    
    Returns
    -------
    None.

    """
    # t_start, t_endがdatatime.time型ではなかった場合、エラーを表示
    if type(t_start) != datetime.time or type(t_end) != datetime.time:
        raise ValueError("the data types of t_start and t_end as input argument must be datetime.time")
        sys.exit()
    
    # 時間をsecに変換
    t_start_sec = t_start.hour*3600+t_start.minute*60+t_start.second
    t_end_sec = t_end.hour*3600+t_end.minute*60+t_end.second
    
    # 指定した時間範囲で音源を切り取り
    sound_all = AudioSegment.from_wav(filepath_wav_input)
    sound_part = sound_all[t_start_sec*1000:t_end_sec*1000]
    sound_part.export(filepath_wav_output, format="wav")
    return



if __name__ == "__main__":
    
    import os
    import tkinter as tk
    import tkinter.filedialog
    
    # =============================================================================
    #     入力値
    # =============================================================================
    t_start = datetime.time(0, 0, 0, 0)
    t_end = datetime.time(0, 1, 0, 0)
    title_label = None
    
    
    folder_output = os.path.join(os.getcwd(), "output")
    t_str = f"{t_start.hour}h{t_start.minute}m{t_start.second}s~{t_end.hour}h{t_end.minute}m{t_end.second}s"
    root = tk.Tk()
    root.withdraw()
    filepath_wav_input_list = tkinter.filedialog.askopenfilename(
        title = "指定した時間範囲で切り取りたい音源データ(*.wav)を選択してください",
        filetypes = [("WAV files", "*.wav")],
        multiple = True)
    if len(filepath_wav_input_list) != 0:
        for filepath_wav_input in filepath_wav_input_list:
            basename_wav_input = os.path.splitext(os.path.basename(filepath_wav_input))[0]
            if title_label == None:
                filepath_output = os.path_join(folder_output, f"{basename_wav_input} {t_str}.wav")
            else:
                filepath_output = os.path.join(folder_output, f"{basename_wav_input} {title_label}.wav")
            CutWav(filepath_wav_input, filepath_output, t_start, t_end)
    else:
        print("WavCut module is canceled")