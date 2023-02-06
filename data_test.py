# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 23:23:04 2022

@author: Ryusei
"""

# 標準ライブラリimport
import tkinter as tk
from tkinter import filedialog
import sys
import pandas as pd
import glob
import os
import tqdm
import shutil as st
import cv2
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use("Agg") #バックエンドを指定
import matplotlib.pyplot as plt
import traceback

from mosqito.functions.shared.load import load
from mosqito.functions.loudness_zwicker.comp_loudness import comp_loudness
from mosqito.functions.oct3filter.comp_third_spectrum import comp_third_spec
from mosqito.functions.loudness_zwicker.loudness_zwicker_shared import calc_main_loudness_ea
from mosqito.functions.loudness_zwicker.loudness_zwicker_shared import calc_main_loudness
from mosqito.functions.loudness_zwicker.loudness_zwicker_nonlinear_decay import calc_nl_loudness
from mosqito.functions.loudness_zwicker.loudness_zwicker_shared import calc_slopes
from mosqito.functions.loudness_zwicker.loudness_zwicker_temporal_weighting import loudness_zwicker_temporal_weighting
from mosqito.functions.loudness_zwicker.sone_to_phon import sone_to_phon
from mosqito.functions.sharpness.sharpness_aures import comp_sharpness_aures
from mosqito.functions.sharpness.sharpness_din import comp_sharpness_din

# 自作モジュールimport
import SoundAnalyzer_GUI as sg
import SoundAnalyzer_Module as sm
import CutWav as cw
import FiltWav as fw
import time_converter as tc


root = tk.Tk()
root.withdraw()
filetype = [("WAV files", "*.wav")]
filepath_wav = filedialog.askopenfilename(filetypes=filetype, multiple=False)


is_stationary = False #非定常信号
signal, fs = load(is_stationary, filepath_wav, calib=1)

# ---------- 1/3octaveバンド処理 ----------- #
third_octave = comp_third_spec(is_stationary, signal, fs) # ←5e-4secごとに出力される（細かすぎるため、計算時間省略のためにデシメーション処理するのが好ましい）
third_octave_Flat = third_octave["values"]
time_axis = third_octave["time"]
freq_band28 = third_octave["freqs"]
#25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500 計28バンド

# ---------- A特性補正処理及びOverall算出 ----------- #
third_octave_A = sm.A_filter_3octave(third_octave_Flat)
OA_A = sm.calc_overall(third_octave_A)

