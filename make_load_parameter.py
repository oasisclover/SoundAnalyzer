# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 09:16:37 2022

@author: Ryusei
"""

import pickle
import datetime


def load_pickle():
    
    with open("parameter/analyze/デフォルト(削除厳禁).pickle", 'rb') as tf:
        dict_analyze = pickle.load(tf)
    with open("parameter/time/デフォルト(削除厳禁).pickle", 'rb') as tf:
        dict_time = pickle.load(tf)
    with open("parameter/graph/デフォルト(削除厳禁).pickle", 'rb') as tf:
        dict_graph = pickle.load(tf)
    with open("components/Default.pickle", 'rb') as tf:
        Default = pickle.load(tf)
        
    return dict_analyze, dict_time, dict_graph, Default



def make_time_parameter():
    
    Default = {'t_start': datetime.time(0, 0, 0, 0),
               't_end' : datetime.time(0, 1, 0, 0)}
    with open("parameter/time/デフォルト(削除厳禁).pickle", "wb") as tf:
        pickle.dump(Default, tf)
    
    return Default



def make_analyze_parameter():
    
    Default = {"amp_calib"          : "*1",
               "A_analyze"          : "on",
               "Loudness_analyze"   : "-",
               "FFT_analyze"        : "-",
               "movie_post"         : "-",
               "freq_range"         : "ALL"}
    with open("parameter/analyze/デフォルト(削除厳禁).pickle", "wb") as tf:
        pickle.dump(Default, tf)

    return Default



def make_graph_parameter():
    
    Default = {"range_Hz":          [30, 12000],
               "yrange_FFT(FLAT)":  [-10.0, 40.0, 10.0],
               "yrange_FFT(A)":     [-10.0, 40.0, 10.0],
               "yrange_OA":         [20.0, 60.0, 5.0],
               "yrange_SN":         [0.0, 5.0, 1.0],
               "zrange_spec(FLAT)": [0.0, 50.0, 10.0],
               "zrange_spec(A)":    [0.0, 40.0, 5.0],
               "zrange_spec(CORE)":  [0.0, 35.0, 5.0]}
    with open("parameter/graph/デフォルト(削除厳禁).pickle", "wb") as tf:
        pickle.dump(Default, tf)
    
    return Default



def make_Default_pickle():
    
    Default = {"analyze_parameter": "デフォルト(削除厳禁).pickle",
               "graph_parameter": "デフォルト(削除厳禁).pickle",
               "time_parameter": "デフォルト(削除厳禁).pickle"}
    with open("components/Default.pickle", "wb") as tf:
        pickle.dump(Default, tf)
    
    return Default



if __name__ == "__main__":
    #Default = make_Default_pickle()
    #Default = make_analyze_parameter()
    #Default = make_time_parameter()
    Default = make_graph_parameter()
    dict_analyze, dict_time, dict_graph, Default = load_pickle()