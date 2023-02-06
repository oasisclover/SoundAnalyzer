# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 09:41:43 2022

@author: Ryusei
"""

import pickle

def Create_DataSet(filepath,
                   filename,
                   t_start,
                   t_end,
                   amp_calib,
                   A_analyze,
                   Loudness_analyze,
                   FFT_analyze,
                   movie_post,
                   freq_range,
                   range_Hz,
                   yrange_FFT_FLAT,
                   yrange_FFT_A,
                   yrange_OA,
                   yrange_SN,
                   zrange_specFLAT,
                   zrange_specA,
                   zrange_specCORE):

    DataSet = {"filepath": filepath,
               "filename": filename,
               "t_start": t_start,
               "t_end": t_end,
               "amp_calib" : amp_calib,
               "A_analyze" : A_analyze,
               "Loudness_analyze" : Loudness_analyze,
               "FFT_analyze": FFT_analyze,               
               "movie_post": movie_post,
               "freq_range": freq_range,
               "range_Hz": range_Hz,
               "yrange_FFT_FLAT": yrange_FFT_FLAT,
               "yrange_FFT_A": yrange_FFT_A,
               "yrange_OA": yrange_OA,
               "yrange_SN": yrange_SN,
               "zrange_specFLAT": zrange_specFLAT,
               "zrange_specA": zrange_specA,
               "zrange_specCORE": zrange_specCORE}
    
    return DataSet


if __name__ == "__main__":
    
    import os
    import tkinter as tk
    from tkinter import filedialog
    
    filepath_txt = os.path.join("components", "Default.pickle")
    with open(filepath_txt, "rb") as f:
        def_name = pickle.load(f)
    filepath_def_time = os.path.join("parameter", "time", def_name["time_parameter"])
    filepath_def_analyze = os.path.join("parameter", "analyze", def_name["analyze_parameter"])
    filepath_def_graph = os.path.join("parameter", "graph", def_name["graph_parameter"])
    with open(filepath_def_analyze, "rb") as tf:
        def_para_analyze = pickle.load(tf)
    with open(filepath_def_graph, "rb") as tf:
        def_para_graph = pickle.load(tf)
    with open(filepath_def_time, "rb") as tf:
        def_para_time = pickle.load(tf)
        
    t_start = def_para_time["t_start"]
    t_end = def_para_time["t_end"]
    
    amp_calib = def_para_analyze["amp_calib"]
    A_analyze = def_para_analyze["A_analyze"]
    Loudness_analyze = def_para_analyze["Loudness_analyze"]
    FFT_analyze = def_para_analyze["FFT_analyze"]
    movie_post = def_para_analyze["movie_post"]
    freq_range = def_para_analyze["freq_range"]
    
    range_Hz = def_para_graph["range_Hz"]
    yrange_FFT_FLAT = def_para_graph["yrange_FFT(FLAT)"]
    yrange_FFT_A = def_para_graph["yrange_FFT(A)"]
    yrange_OA = def_para_graph["yrange_OA"]
    yrange_SN = def_para_graph["yrange_SN"]
    zrange_specFLAT = def_para_graph["zrange_spec(FLAT)"]
    zrange_specA = def_para_graph["zrange_spec(A)"]
    zrange_specCORE = def_para_graph["zrange_spec(CORE)"]
    
    root = tk.Tk()
    root.withdraw()
    filepath_wav_list = filedialog.askopenfilename(
                        title = "test",
                        filetypes = [("WAV files", "*.wav")],
                        multiple = True)
    job_list = []
    for job_number in range(0, len(filepath_wav_list), 1):
        filepath_wav = filepath_wav_list[job_number]
        filename_wav = os.path.basename(filepath_wav)
        job_list.append(Create_DataSet(filepath_wav, 
                                       filename_wav, 
                                       t_start, 
                                       t_end,
                                       amp_calib,
                                       A_analyze,
                                       Loudness_analyze,
                                       FFT_analyze,
                                       movie_post,
                                       freq_range, 
                                       range_Hz, 
                                       yrange_FFT_FLAT, 
                                       yrange_FFT_A, 
                                       yrange_OA, 
                                       yrange_SN, 
                                       zrange_specFLAT, 
                                       zrange_specA, 
                                       zrange_specCORE))
    
    with open("test_jobDataSet.txt", "w") as f:
        for key in job_list[0]:
            f.write(f"{key} : {job_list[0][key]}\n")