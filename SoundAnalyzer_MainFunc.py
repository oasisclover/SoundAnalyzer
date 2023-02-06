# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 02:04:30 2022

@author: Ryusei
"""

version = "0.7.0"
print(f"SoundAnalyzer (Version {version}) 起動中...")

# 標準ライブラリimport
import tkinter as tk
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
from mosqito.functions.loudness_zwicker.sone_to_phon import sone_to_phon
from mosqito.functions.sharpness.sharpness_aures import comp_sharpness_aures
from mosqito.functions.sharpness.sharpness_din import comp_sharpness_din

# 自作モジュールimport
import SoundAnalyzer_GUI as sg
import SoundAnalyzer_Module as sm
import CutWav as cw
import FiltWav as fw
import time_converter as tc
from opencv import imread
from opencv import imwrite



class Main(sg.GUI):
    
    def __init__(self):
        root = tk.Tk()
        super().__init__(version, master=root)
        root.mainloop()
        return
    
    
    
    # =============================================================================
    #     メイン計算処理＆プロット関数
    # =============================================================================
    def MainFunc(self):
        
        self.started.wait()
        # リソースフォルダパスの設定
        folder_components = "components"
        folder_frame1     = "frame1"
        folder_frame2     = "frame2"
        folder_mp4        = "mp4"
        folder_png        = "png"
        folder_wav        = "wav"
        
        filepath_bar1    = os.path.join(folder_components, "black_bar1.png")
        filepath_bar2    = os.path.join(folder_components, "black_bar2.png")
        filepath_mp4     = os.path.join(folder_mp4, "movie.mp4")
        filepath_mp4_wav = os.path.join(folder_mp4, "movie_sound.mp4")
        filepath_png     = os.path.join(folder_png, "contour.png")
        filepath_wav1    = os.path.join(folder_wav, "sound1.wav")
        filepath_wav2    = os.path.join(folder_wav, "sound2.wav")
        
        # グラフの設定
        plt.rcParams["font.family"] = "serif"           # 使用するフォント
        plt.rcParams["font.serif"]  = "Times New Roman" # 使用するフォント
        plt.rcParams["font.size"]   = 24                # 基本となるフォントの大きさ
        plt.rcParams["axes.labelsize"] = 24             # 軸ラベルのフォントサイズ
        plt.rcParams["legend.fontsize"] = 16            # 凡例のフォントの大きさ
        plt.rcParams["legend.handlelength"] = 1         # 凡例のイラスト線の長さ
        plt.rcParams["axes.grid"] = True                # グリッドを表示するかどうか
        plt.rcParams["xtick.labelsize"] = 18            # X軸目盛のフォントサイズ
        plt.rcParams["ytick.labelsize"] = 24            # Y軸目盛のフォントサイズ
        self.cm = plt.cm.get_cmap("jet")                # コンター図の色の種類を定義
        
        
        for job_number, self.record in enumerate(self.tree.get_children()):
            
            # リソースフォルダ内のファイルを全消去
            files_del = glob.glob(folder_frame1+"\\*.png")
            for file_del in files_del:
                os.remove(file_del)
            
            files_del = glob.glob(folder_frame2+"\\*.png")
            for file_del in files_del:
                os.remove(file_del)
            
            files_del = glob.glob(folder_mp4+"\\*.mp4")
            for file_del in files_del:
                os.remove(file_del)
            
            files_del = glob.glob(folder_png+"\\*.png")
            for file_del in files_del:
                os.remove(file_del)
            
            files_del = glob.glob(folder_wav+"\\*.wav")
            for file_del in files_del:
                os.remove(file_del)
            
            
            # =============================================================================
            #         メイン計算処理
            # =============================================================================
            try:
                job = self.job_list[job_number]
                
                
                if job["A_analyze"] == "on" or job["Loudness_analyze"] == "on" or job["FFT_analyze"] == "on" or job["movie_post"] == "on":
                    
                    # =============================================================================
                    ####                 解析前準備
                    # =============================================================================
                    if self.started.is_set():
                        self.tree.set(self.record, 2, "解析準備中...")
                        
                        # ========= 出力フォルダの作成 ========= #
                        filename_wav = os.path.basename(job["filepath"])
                        basename_wav = os.path.splitext(filename_wav)[0]
                        t_start = job["t_start"]
                        t_end = job["t_end"]
                        time_label = f"{t_start.hour}h{t_start.minute}m{t_start.second}s~{t_end.hour}h{t_end.minute}m{t_end.second}s"
                        if job["freq_range"] == "ALL":
                            folder_output_new = os.path.join(self.folder_output, f"{basename_wav} {time_label}")
                        else:
                            freq_label = f"{job['freq_range'][0]}Hz~{job['freq_range'][1]}Hz"
                            folder_output_new = os.path.join(self.folder_output, f"{basename_wav} {time_label} {freq_label}")
                        for i in range(1, 1000, 1):
                            if not os.path.exists(folder_output_new):
                                os.mkdir(folder_output_new)
                                break
                            else:
                                if job["freq_range"] == "ALL":
                                    folder_output_new = os.path.join(self.folder_output, f"{basename_wav} {time_label} ({i})")
                                else:
                                    folder_output_new = os.path.join(self.folder_output, f"{basename_wav} {time_label} {freq_label} ({i})")
                                continue
                        self.btn_result["state"] = "able"
                        
                        
                        # ========= 解析時の設定パラメータをtxtファイルに出力 ========= #
                        filepath_data_info = os.path.join(folder_output_new, "DataInfo.txt")
                        with open(filepath_data_info, "w", encoding="utf-8") as f:
                            f.write(f"SoundAnalyzer version == {version}\n")
                            for key in job:
                                f.write(f"{key} : {job[key]}\n")
                        
                        
                        # ========= 指定時間範囲でwavデータ切り取り ========= #
                        cw.CutWav(job["filepath"], filepath_wav1, t_start, t_end)
                        
                        
                        # ========= 指定周波数範囲でwavデータをフィルタリング ========= #
                        if job["freq_range"] != "ALL":
                            fw.CutFreq(filepath_wav1, filepath_wav2, job["freq_range"])
                            filepath_wav = filepath_wav2
                        else:
                            filepath_wav = filepath_wav1
                        
                        
                        # ========= t_range変換 ========= #
                        self.t_start_sec, self.t_end_sec, t_tick, dec = tc.calc_t_tick(job["t_start"], job["t_end"])
                        self.timeticks = np.arange(0, self.t_end_sec-self.t_start_sec+t_tick, t_tick)
                        self.timeticks2 = np.arange(self.t_start_sec, self.t_end_sec+t_tick, t_tick)
                        self.timelabels = [tc.convert_time(timetick)[1] for timetick in self.timeticks2]
                        
                        # ========= csv出力用dataframe準備 ========== #
                        df = pd.DataFrame()
                        
                    else:
                        self.display_stop()
                        
                    
                    # =============================================================================
                    ####                 wavデータ読込
                    # =============================================================================                    
                    if self.started.is_set():
                        self.tree.set(self.record, 2, "wavデータ読込中...")
                        
                        # ========= 時刻歴振幅波形読込 ========= #
                        if job["amp_calib"] == "*1":
                            calib = 1 # 振幅補正値
                        elif job["amp_calib"] == "*√2":
                            calib = 2**0.5
                        is_stationary = False #非定常信号
                        signal, fs = load(is_stationary, filepath_wav, calib=calib)
                        # fs:サンプリング周波数[Hz] ※fs=48000固定で出てくるはず
                        try:
                            channels = signal.shape[1]
                            print(f"channels : {channels} \nUnable to analyze multi-channels-Audio")
                            sys.exit()
                        except IndexError:
                            print("channels : 1")
                        
                    else:
                        self.display_stop()
                
                
                
                if job["FFT_analyze"] == "on":
                    
                    # =============================================================================
                    ####                 FFT解析
                    # =============================================================================
                    # https://watlab-blog.com/2019/04/17/python-overlap/                    
                    if self.started.is_set():
                        self.tree.set(self.record, 2, "FFT解析中...")
                        
                        self.time_signal = np.arange(0, len(signal))/fs
                        Fs = 19200 #　フレームサイズ[点数](=時間窓長)
                        #　※時間窓長Fsが長い程周波数分解能は上がるが、その分だけ時間変化に鈍くなる、定常信号解析の場合はFsは長くていいが、非定常信号解析の場合は一般的にはFsを短くするほうが良い
                        overlap = 50 #[%]
                        signal_ol, N_ave = sm.ov(signal, fs, Fs, overlap)
                        han = np.hamming(Fs) # ハミング窓関数作成
                        acf = 1/(sum(han)/Fs) # Amplitude Correction Factorを計算
                        # オーバーラップ波形に対しハミング窓をかける
                        fft_array = np.array([np.abs(np.fft.fft(signal_ol[k]*han/(Fs/2))) for k in range(N_ave)])# ※(Fs/2)で割ってるのは正規化のため
                        fft_mean = np.mean(fft_array, axis=0)
                        fft_mean = fft_mean*acf # 補正係数を乗算
                        self.freqList = np.fft.fftfreq(signal_ol[0].shape[0], d=1/fs) # (データ点数,　サンプリング周期)
                        fft_mean_dB = sm.Pa2dB(fft_mean)
                        A_curve = sm.A_filter_fft(self.freqList)
                        fft_mean_dB_A = fft_mean_dB + A_curve
                        
                    else:
                        self.display_stop()
                    
                    
                    
                    # =============================================================================
                    ####           プロット Wave signal
                    # =============================================================================
                    if self.started.is_set():
                        self.tree.set(self.record, 2, "FFTプロット中(1/4)...")
                        
                        fig = plt.figure(figsize=(12, 5))
                        fig.patch.set_alpha(0) #背景色の透明度を設定
                        ax = plt.axes([0.1, 0.25, 0.8, 0.68]) #axes([左, 下, 幅, 高さ])
                        ax.plot(self.time_signal, signal, lw=1, color="blue")
                        ax.set_xlim(0, self.t_end_sec-self.t_start_sec)
                        ax.set_xticks(self.timeticks)
                        ax.set_xticklabels(self.timelabels, rotation=90)
                        ax.set_xlabel("Time")
                        ax.set_ylim(-2, 2)
                        ax.set_yticks(np.arange(-2, 2+0.5, 0.5))
                        ax.set_ylabel("Amplitude [Pa]")
                        ax.set_title(f"{basename_wav} Wave signal", font="MS Gothic", fontsize=16)
                        ax.text(1.12, -0.3, f"v{version}", va='top', ha='right', transform=ax.transAxes, fontsize=16)
                        plt.savefig(os.path.join(folder_output_new, "Wav signal.png"))
                        plt.close()
                        
                    else:
                        self.display_stop()
                    
                    
                    
                    # =============================================================================
                    ####           プロット FFT signal (FLAT) [Pa]
                    # =============================================================================
                    if self.started.is_set():
                        self.tree.set(self.record, 2, "FFTプロット中(2/4)...")
                        
                        xrange = job["range_Hz"]
                        xticks = [10, 20, 30, 40, 50, 60, 70, 80, 90,
                                  100, 200, 300, 400, 500, 600, 700, 800, 900,
                                  1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 
                                  10000, 11000, 12000, 13000]
                        xticks = list(filter(lambda i: i>=xrange[0] and i<=xrange[1], xticks))
                        fig = plt.figure(figsize=(12, 5))
                        fig.patch.set_alpha(0) #背景色の透明度を設定
                        ax = plt.axes([0.1, 0.25, 0.8, 0.68]) #axes([左, 下, 幅, 高さ])
                        ax.plot(self.freqList, fft_mean, lw=1, color="blue")
                        ax.set_xscale("log")
                        ax.set_xlim(xrange[0], xrange[1])
                        ax.set_xticks(xticks)
                        ax.set_xlabel("Frequency [Hz]")
                        ax.set_ylim(0, 2)
                        ax.set_yticks(np.arange(0, 2+0.5, 0.5))
                        ax.set_ylabel("Amplitude [Pa]")
                        ax.set_title(f"{basename_wav} FFT(FLAT) signal", font="MS Gothic", fontsize=16)
                        ax.text(1.12, -0.3, f"v{version}", va='top', ha='right', transform=ax.transAxes, fontsize=16)
                        plt.savefig(os.path.join(folder_output_new, "FFT(FLAT) signal [Pa].png"))
                        plt.close()
                        
                    else:
                        self.display_stop()
                    
                    
                    
                    # =============================================================================
                    ####           プロット FFT signal (FLAT) [dB]
                    # =============================================================================
                    if self.started.is_set():
                        self.tree.set(self.record, 2, "FFTプロット中(3/4)...")
                        
                        xrange = job["xrange_FFT"]
                        yrange = job["yrange_FFT_FLAT"]
                        fig = plt.figure(figsize=(12, 5))
                        fig.patch.set_alpha(0) #背景色の透明度を設定
                        ax = plt.axes([0.1, 0.25, 0.8, 0.68]) #axes([左, 下, 幅, 高さ])
                        ax.plot(self.freqList, fft_mean_dB, lw=1, color="blue")
                        ax.set_xscale("log")
                        ax.set_xlim(xrange[0], xrange[1])
                        ax.set_xticks(xticks)
                        ax.set_xlabel("Frequency [Hz]")
                        ax.set_ylim(yrange[0], yrange[1])
                        ax.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                        ax.set_ylabel("Amplitude [dB]")
                        ax.set_title(f"{basename_wav} FFT(FLAT) signal", font="MS Gothic", fontsize=16)
                        ax.text(1.12, -0.3, f"v{version}", va='top', ha='right', transform=ax.transAxes, fontsize=16)
                        plt.savefig(os.path.join(folder_output_new, "FFT(FLAT) signal [dB].png"))
                        plt.close()
                        
                    else:
                        self.display_stop()
                    
                    
                    
                    # =============================================================================
                    ####           プロット FFT signal (A) [dB]
                    # =============================================================================
                    if self.started.is_set():
                        self.tree.set(self.record, 2, "FFTプロット中(4/4)...")
                        
                        xrange = job["xrange_FFT"]
                        yrange = job["yrange_FFT_A"]
                        fig = plt.figure(figsize=(12, 5))
                        fig.patch.set_alpha(0) #背景色の透明度を設定
                        ax = plt.axes([0.1, 0.25, 0.8, 0.68]) #axes([左, 下, 幅, 高さ])
                        ax.plot(self.freqList, fft_mean_dB_A, lw=1, color="blue")
                        ax.set_xscale("log")
                        ax.set_xlim(xrange[0], xrange[1])
                        ax.set_xticks(xticks)
                        ax.set_xlabel("Frequency [Hz]")
                        ax.set_ylim(yrange[0], yrange[1])
                        ax.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                        ax.set_ylabel("Amplitude [dB]")
                        ax.set_title(f"{basename_wav} FFT(A) signal", font="MS Gothic", fontsize=16)
                        ax.text(1.12, -0.3, f"v{version}", va='top', ha='right', transform=ax.transAxes, fontsize=16)
                        plt.savefig(os.path.join(folder_output_new, "FFT(A) signal [dB].png"))
                        plt.close()
                        
                    else:
                        self.display_stop()
                
                
                
                if job["A_analyze"] == "on" or job["movie_post"] == "on":
                    
                    # =============================================================================
                    ####                 1/3octave解析
                    # =============================================================================
                    if self.started.is_set():
                        self.tree.set(self.record, 2, "A特性解析中...")
                        
                        # ---------- 1/3octaveバンド処理 ----------- #
                        third_octave = comp_third_spec(is_stationary, signal, fs) # ←5e-4secごとに出力される（細かすぎるため、計算時間省略のためにデシメーション処理するのが好ましい）
                        third_octave_Flat = third_octave["values"]
                        time_axis = third_octave["time"]
                        self.time_axis = time_axis
                        self.freq_band28 = third_octave["freqs"]
                        #25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500 計28バンド
                        
                        # ---------- A特性補正処理及びOverall算出 ----------- #
                        third_octave_A = sm.A_filter_3octave(third_octave_Flat)
                        self.OA_A = sm.calc_overall(third_octave_A)
                        
                        # ---------- 計算時間省略のためにデシメーション処理 ----------- #
                        third_octave_Flat_dec = third_octave_Flat[:, ::dec]
                        third_octave_A_dec = third_octave_A[:, ::dec]
                        self.time_axis_dec = time_axis[::dec]
                        
                        # ---------- プロット用のため0以下の値をすべて0値化 ----------- #
                        self.third_octave_Flat = np.where(third_octave_Flat_dec<0, 0, third_octave_Flat_dec)
                        self.third_octave_A = np.where(third_octave_A_dec<0, 0, third_octave_A_dec)
                        
                        # ---------- dataframeに格納 ----------- #
                        df["Time [sec]"] = np.append(self.time_axis_dec, ["max", "min", "average"])
                        df["Overall(A) [dB]"] = np.append(self.OA_A[::dec], [max(self.OA_A), min(self.OA_A), np.mean(self.OA_A)])
                        
                        #コンター図作成準備
                        X1, Y1 = np.meshgrid(self.time_axis_dec, np.array(self.freq_band28))
                    else:
                        self.display_stop()
                    
                
                
                if job["Loudness_analyze"] == "on" or job["movie_post"] == "on":
                    
                    # ========= ラウドネス、シャープネス算出 ========= #
                    if self.started.is_set():
                        self.tree.set(self.record, 2, "ラウドネス解析中...")
                        
                        loudness_obj = comp_loudness(is_stationary, signal, fs)
                        loudness = loudness_obj["values"]
                        spec_loudness = loudness_obj["specific values"]
                        self.bark_axis = loudness_obj["freqs"]
                        
                        # ---------- ラウドネスレベルに変換[sone→phon(≒dB)]&プロット時間短縮のためデシメーション処理 ----------- #
                        self.loudness_level = np.array([])
                        for col in range(len(self.time_axis_dec)):
                            self.loudness_level = np.append(self.loudness_level, sone_to_phon(loudness[col*dec]))
                        
                        self.spec_loudness_level = np.zeros((240, len(self.time_axis_dec)))
                        for row in range(spec_loudness.shape[0]):
                            for col in range(len(self.time_axis_dec)):
                                self.spec_loudness_level[row, col] = sone_to_phon(spec_loudness[row, col*dec])
                        
                        self.sharpness_din = comp_sharpness_din(loudness[::dec], spec_loudness[:, ::dec], is_stationary)
                        self.sharpness_aures = comp_sharpness_aures(loudness[::dec], spec_loudness[:, ::dec], is_stationary)
                        
                        #コンター図作成準備
                        X2, Y2 = np.meshgrid(self.time_axis_dec, np.array(self.bark_axis))
                        
                        # ---------- dataframeに格納 ----------- #
                        if job["A_analyze"] != "on":
                            df["Time [sec]"] = np.append(self.time_axis_dec, ["max", "min", "average"])
                        df["Loness Level [phon]"] = np.append(self.loudness_level, [max(self.loudness_level), min(self.loudness_level), np.mean(self.loudness_level)])
                        df["Sharpness(Aures) [acum]"] = np.append(self.sharpness_aures, [max(self.sharpness_aures), min(self.sharpness_aures), np.mean(self.sharpness_aures)])
                        df["Sharpness(Din) [acum]"] = np.append(self.sharpness_din, [max(self.sharpness_din), min(self.sharpness_din), np.mean(self.sharpness_din)])
                    else:
                        self.display_stop()
                    
                    
                    
                # =============================================================================
                ####                     算出値csv出力
                # =============================================================================
                if self.started.is_set():
                    self.tree.set(self.record, 2, "csvデータ出力中...")
                    # ---------- 各値保存 ----------- #
                    df.to_csv(os.path.join(folder_output_new, "data.csv"), index=False)
                    
                    # ---------- 1/3octave(A)のデータをcsv出力 ----------- #
                    if job["A_analyze"] == "on":
                        dec_csv = 2000 #←1sec間隔でデータを出力するためのデシメーション（服部さん要望により固定）
                        time_axis_csv = time_axis[::dec_csv]
                        third_octave_A_csv = third_octave_A[:, ::dec_csv]
                        df2 = pd.DataFrame({"Frequency[Hz] : Time[sec]" : self.freq_band28})
                        df3 = pd.DataFrame(third_octave_A_csv, columns=np.round(time_axis_csv, 2))
                        df4 = df2.join(df3)
                        df4.to_csv(os.path.join(folder_output_new, "3rd_octave(A).csv"), index=False)
                    
                else:
                    self.display_stop()
                
                
                
                if job["A_analyze"] == "on":
                    
                    # =============================================================================
                    ####                     プロット OA(A)&Loudness
                    # =============================================================================
                    if  self.started.is_set():
                        self.tree.set(self.record, 2, "解析結果プロット中(1/7)...")
                        
                        yrange = job["yrange_OA"]
                        fig = plt.figure(figsize=(12, 5))
                        fig.patch.set_alpha(0) #背景色の透明度を設定
                        ax = plt.axes([0.1, 0.25, 0.8, 0.68]) #axes([左, 下, 幅, 高さ])
                        OA_A_mean = np.array(pd.DataFrame(self.OA_A).rolling(10).mean())
                        ax.plot(time_axis, OA_A_mean, lw=1, color="blue", label="OA(A)")
                        ax.set_xlim(0, self.t_end_sec-self.t_start_sec)
                        ax.set_xticks(self.timeticks)
                        ax.set_xticklabels(self.timelabels, rotation=90)
                        ax.set_xlabel("Time")
                        ax.set_ylim(yrange[0], yrange[1])
                        ax.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                        ax.set_ylabel('OA(A) [dB]')
                        if job["Loudness_analyze"] == "on":
                            ax2 = ax.twinx()
                            ax2.plot(self.time_axis_dec, self.loudness_level, lw=1, color="red", label="Loudness")
                            ax2.set_ylim(yrange[0], yrange[1])
                            ax2.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                            ax2.set_ylabel("Loudness Level [phon]")
                            h1, l1 = ax.get_legend_handles_labels()
                            h2, l2 = ax2.get_legend_handles_labels()
                            ax.legend(h1+h2, l1+l2, loc="upper right")
                            ax.set_title(f"{basename_wav} Overall(A)&Loudness", fontname="MS Gothic", fontsize=16)
                            ax.text(1.12, -0.3, f"v{version}", va='top', ha='right', transform=ax.transAxes, fontsize=16)
                            savepath = os.path.join(folder_output_new, "Overall(A)&Loudness.png")
                        else:
                            ax.set_title(f"{basename_wav} Overall(A)", fontname="MS Gothic", fontsize=16)
                            ax.text(1.12, -0.3, f"v{version}", va='top', ha='right', transform=ax.transAxes, fontsize=16)
                            savepath = os.path.join(folder_output_new, "Overall(A).png")
                        plt.savefig(savepath)
                        plt.close()
                        
                    else:
                        self.display_stop()
                    
                    
                    
                    # =============================================================================
                    ####                     プロット spectrogram (FLAT)
                    # =============================================================================
                    if  self.started.is_set():
                        self.tree.set(self.record, 2, "解析結果プロット中(2/7)...")
                        
                        yrange = job["range_Hz"]
                        yticks = [10, 100, 1000, 10000]
                        yticks = list(filter(lambda i: i>=yrange[0] and i<=yrange[1], yticks))
                        yticklabels = [i*1e-3 for i in yticks]
                        yticklabels = [int(i) if i >= 1 else i for i in yticklabels]
                        zrange = job["zrange_specFLAT"]
                        fig = plt.figure(figsize=(12, 5))
                        fig.patch.set_alpha(0) #背景色の透明度を設定
                        ax = plt.axes([0.1, 0.25, 0.95, 0.68]) #axes([左, 下, 幅, 高さ])
                        contour = ax.contourf(X1, Y1, self.third_octave_Flat, cmap=self.cm, levels=np.arange(zrange[0], zrange[1]+zrange[2]/10, zrange[2]/10))
                        cbar = plt.colorbar(contour, ticks=[np.arange(zrange[0], zrange[1]+zrange[2], zrange[2])], orientation="vertical", pad=0.01)
                        cbar.set_label("SPL [dB]")
                        ax.set_xlim(0, self.t_end_sec-self.t_start_sec)
                        ax.set_xticks(self.timeticks)
                        ax.set_xticklabels(self.timelabels, rotation=90)
                        ax.set_xlabel("Time")
                        ax.set_yscale("log")
                        ax.set_ylim(yrange[0], yrange[1])
                        ax.set_yticks(yticks)
                        ax.set_yticklabels(yticklabels)
                        ax.set_ylabel("Frequency [kHz]")
                        ax.set_title(f"{basename_wav} Spectrogram(FLAT)", fontname="MS Gothic", fontsize=16)
                        ax.text(1.12, -0.3, f"v{version}", va='top', ha='right', transform=ax.transAxes, fontsize=16)
                        savepath = os.path.join(folder_output_new, "Spectrogram(FLAT).png")
                        plt.savefig(savepath)
                        plt.close()
                        
                    else:
                        self.display_stop()
                    
                    
                    
                    # =============================================================================
                    ####                     プロット spectrogram (A)
                    # =============================================================================
                    if  self.started.is_set():
                        self.tree.set(self.record, 2, "解析結果プロット中(3/7)...")
                        
                        zrange = job["zrange_specA"]
                        fig = plt.figure(figsize=(12, 5))
                        fig.patch.set_alpha(0) #背景色の透明度を設定
                        ax = plt.axes([0.1, 0.25, 0.95, 0.68]) #axes([左, 下, 幅, 高さ])
                        contour = ax.contourf(X1, Y1, self.third_octave_A, cmap=self.cm, levels=np.arange(zrange[0], zrange[1]+zrange[2]/10, zrange[2]/10))
                        cbar = plt.colorbar(contour, ticks=[np.arange(zrange[0], zrange[1]+zrange[2], zrange[2])], orientation="vertical", pad=0.01)
                        cbar.set_label("SPL [dB]")
                        ax.set_xlim(0, self.t_end_sec-self.t_start_sec)
                        ax.set_xticks(self.timeticks)
                        ax.set_xticklabels(self.timelabels, rotation=90)
                        ax.set_xlabel("Time")
                        ax.set_yscale("log")
                        ax.set_ylim(yrange[0], yrange[1])
                        ax.set_yticks(yticks)
                        ax.set_yticklabels(yticklabels)
                        ax.set_ylabel("Frequency [kHz]")
                        ax.set_title(f"{basename_wav} Spectrogram(A)", fontname="MS Gothic", fontsize=16)
                        ax.text(1.12, -0.3, f"v{version}", va='top', ha='right', transform=ax.transAxes, fontsize=16)
                        savepath = os.path.join(folder_output_new, "Spectrogram(A).png")
                        plt.savefig(savepath)
                        plt.close()
                        
                    else:
                        self.display_stop()
                    
                    
                    
                if job["Loudness_analyze"] == "on":
                    
                    if job["A_analyze"] != "on":
                        # =============================================================================
                        ####                     プロット Loudness
                        # =============================================================================
                        if  self.started.is_set():
                            self.tree.set(self.record, 2, "解析結果プロット中(4/7)...")
                            
                            yrange = job["yrange_OA"]
                            fig = plt.figure(figsize=(12, 5))
                            fig.patch.set_alpha(0) #背景色の透明度を設定
                            ax = plt.axes([0.1, 0.25, 0.8, 0.68]) #axes([左, 下, 幅, 高さ])
                            ax.plot(self.time_axis_dec, self.loudness_level, lw=1, color="red", label="Loudness")
                            ax.set_xlim(0, self.t_end_sec-self.t_start_sec)
                            ax.set_xticks(self.timeticks)
                            ax.set_xticklabels(self.timelabels, rotation=90)
                            ax.set_xlabel("Time")
                            ax.set_ylim(yrange[0], yrange[1])
                            ax.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                            ax.set_ylabel("Loudness Level [phon]")
                            ax.set_title(f"{basename_wav} Loudness", fontname="MS Gothic", fontsize=16)
                            ax.text(1.12, -0.3, f"v{version}", va='top', ha='right', transform=ax.transAxes, fontsize=16)
                            savepath = os.path.join(folder_output_new, "Loudness.png")
                            plt.savefig(savepath)
                            plt.close()
                            
                        else:
                            self.display_stop()
                        
                    # =============================================================================
                    ####                     プロット spectrogram (Specific Loudness)
                    # =============================================================================
                    if  self.started.is_set():
                        self.tree.set(self.record, 2, "解析結果プロット中(5/7)...")
                        
                        zrange = job["zrange_specCORE"]
                        fig = plt.figure(figsize=(12, 5))
                        fig.patch.set_alpha(0) #背景色の透明度を設定
                        ax = plt.axes([0.1, 0.25, 0.95, 0.68]) #axes([左, 下, 幅, 高さ])
                        contour = ax.contourf(X2, Y2, self.spec_loudness_level, cmap=self.cm, levels=np.arange(zrange[0], zrange[1]+zrange[2]/10, zrange[2]/10))
                        cbar = plt.colorbar(contour, ticks=[np.arange(zrange[0], zrange[1]+zrange[2], zrange[2])], orientation="vertical", pad=0.01)
                        cbar.set_label("Specific Loudness [phon]")
                        ax.set_xlim(0, self.t_end_sec-self.t_start_sec)
                        ax.set_xticks(self.timeticks)
                        ax.set_xticklabels(self.timelabels, rotation=90)
                        ax.set_xlabel("Time")
                        ax.set_ylim(0, 24)
                        ax.set_yticks([0, 5, 10, 15, 20, 24])
                        ax.set_ylabel("Bark scale [-]")
                        ax.set_title(f"{basename_wav} Spectrogram(SpecificLoudness)", fontname="MS Gothic", fontsize=16)
                        ax.text(1.12, -0.3, f"v{version}", va='top', ha='right', transform=ax.transAxes, fontsize=16)
                        savepath = os.path.join(folder_output_new, "Spectrogram(SpecificLoudness).png")
                        plt.savefig(savepath)
                        plt.close()
                        
                    else:
                        self.display_stop()
                                        
                    
                    
                    # =============================================================================
                    ####                     プロット Sharpness
                    # =============================================================================
                    if  self.started.is_set():
                        self.tree.set(self.record, 2, "解析結果プロット中(6/7)...")
                        
                        yrange = job["yrange_SN"]
                        fig = plt.figure(figsize=(12, 5))
                        fig.patch.set_alpha(0) #背景色の透明度を設定
                        ax = plt.axes([0.1, 0.25, 0.8, 0.68]) #axes([左, 下, 幅, 高さ])
                        ax.plot(self.time_axis_dec, self.sharpness_din, lw=1, color="blue", label="Din45629")
                        ax.plot(self.time_axis_dec, self.sharpness_aures, lw=1, color="red", label="Aures")
                        ax.legend(loc="upper right").get_frame().set_alpha(0.5)
                        ax.set_xlim(0, self.t_end_sec-self.t_start_sec)
                        ax.set_xticks(self.timeticks)
                        ax.set_xticklabels(self.timelabels, rotation=90)
                        ax.set_xlabel("Time")
                        ax.set_ylim(yrange[0], yrange[1])
                        ax.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                        ax.set_ylabel("Sharpness [acum]")
                        ax.set_title(f"{basename_wav} Sharpness", fontname="MS Gothic", fontsize=16)
                        ax.text(1.12, -0.3, f"v{version}", va='top', ha='right', transform=ax.transAxes, fontsize=16)
                        savepath = os.path.join(folder_output_new, "Sharpness.png")
                        plt.savefig(savepath)
                        plt.close()
                        
                    else:
                        self.display_stop()
                    
                    
                    
                if job["A_analyze"] == "on" or job["Loudness_analyze"] == "on":
                    
                    # =============================================================================
                    ####                     プロット AllFigure
                    # =============================================================================
                    if self.started.is_set():
                        self.tree.set(self.record, 2, "解析結果プロット中(7/7)...")
                        
                        fig = plt.figure(figsize=(25, 15))
                        fig.patch.set_alpha(0) #背景色の透明度を設定
                        fig.suptitle(basename_wav, fontsize=25, fontname="MS Gothic")
                        fig.text(2.48, -0.3, f"v{version}", va='top', ha='right', transform=ax.transAxes, fontsize=16)
                        L1 = [0.04, 0.67, 0.412, 0.23] #axes([左, 下, 幅, 高さ])
                        L2 = [0.04, 0.38, 0.490, 0.23] #axes([左, 下, 幅, 高さ])
                        L3 = [0.04, 0.10, 0.490, 0.23] #axes([左, 下, 幅, 高さ])
                        R1 = [0.54, 0.67, 0.412, 0.23] #axes([左, 下, 幅, 高さ])
                        R2 = [0.54, 0.38, 0.490, 0.23] #axes([左, 下, 幅, 高さ])
                        R3 = [0.54, 0.10, 0.490, 0.23] #axes([左, 下, 幅, 高さ])
                        
                        if job["A_analyze"] == "on":
                            yrange = job["yrange_OA"]
                            axL1 = plt.axes(L1)
                            axL1.plot(time_axis, OA_A_mean, lw=1, color="blue", label="OA(A)")
                            axL1.set_xlim(0, self.t_end_sec-self.t_start_sec)
                            axL1.set_xticks(self.timeticks)
                            axL1.set_xticklabels([])
                            axL1.set_ylim(yrange[0], yrange[1])
                            axL1.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                            if job["Loudness_analyze"] == "on":
                                ax2 = axL1.twinx()
                                ax2.plot(self.time_axis_dec, self.loudness_level, lw=1, color="red", label="Loudness")
                                ax2.set_ylim(yrange[0], yrange[1])
                                ax2.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                                ax2.set_ylabel("Loudness Level [phon]")
                                h1, l1 = axL1.get_legend_handles_labels()
                                h2, l2 = ax2.get_legend_handles_labels()
                                axL1.legend(h1+h2, l1+l2, loc="upper right")
                                axL1.set_title("Overall(A) & Loudness")
                            else:
                                axL1.set_title("Overall(A)")
                        
                        elif job["A_analyze"] != "on" and job["Loudness_analyze"] == "on":
                            yrange = job["yrange_OA"]
                            axL1 = plt.axes(L1)
                            axL1.plot(self.time_axis_dec, self.loudness_level, lw=1, color="red", label="Loudness")
                            axL1.set_xlim(0, self.t_end_sec-self.t_start_sec)
                            axL1.set_xticks(self.timeticks)
                            axL1.set_xticklabels(self.timelabels, rotation=90)
                            axL1.set_ylim(yrange[0], yrange[1])
                            axL1.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                            axL1.set_ylabel("Loudness Level [phon]")
                            axL1.set_title("Loudness")
                        
                        if job["A_analyze"] == "on":
                            yrange = job["range_Hz"]
                            yticks = [10, 100, 1000, 10000]
                            yticks = list(filter(lambda i: i>=yrange[0] and i<=yrange[1], yticks))
                            yticklabels = [i*1e-3 for i in yticks]
                            yticklabels = [int(i) if i >= 1 else i for i in yticklabels]
                            zrange = job["zrange_specFLAT"]
                            axL2 = plt.axes(L2)
                            contour = axL2.contourf(X1, Y1, self.third_octave_Flat, cmap=self.cm, levels=np.arange(zrange[0], zrange[1]+zrange[2]/10, zrange[2]/10))
                            cbar = plt.colorbar(contour, ticks=[np.arange(zrange[0], zrange[1]+zrange[2], zrange[2])], orientation="vertical", pad=0.01)
                            cbar.set_label("SPL [dB]")
                            axL2.set_xlim(0, self.t_end_sec-self.t_start_sec)
                            axL2.set_xticks(self.timeticks)
                            axL2.set_xticklabels([])
                            axL2.set_yscale("log")
                            axL2.set_ylim(yrange[0], yrange[1])
                            axL2.set_yticks(yticks)
                            axL2.set_yticklabels(yticklabels)
                            axL2.set_ylabel("Frequency [kHz]")
                            axL2.set_title("Spectrogram(FLAT)")
                            
                            zrange = job["zrange_specA"]
                            axL3 = plt.axes(L3)
                            contour = axL3.contourf(X1, Y1, self.third_octave_A, cmap=self.cm, levels=np.arange(zrange[0], zrange[1]+zrange[2]/10, zrange[2]/10))
                            cbar = plt.colorbar(contour, ticks=[np.arange(zrange[0], zrange[1]+zrange[2], zrange[2])], orientation="vertical", pad=0.01)
                            cbar.set_label("SPL [dB]")
                            axL3.set_xlim(0, self.t_end_sec-self.t_start_sec)
                            axL3.set_xticks(self.timeticks)
                            axL3.set_xticklabels(self.timelabels, rotation=90)
                            axL3.set_xlabel("Time")
                            axL3.set_yscale("log")
                            axL3.set_ylim(yrange[0], yrange[1])
                            axL3.set_yticks(yticks)
                            axL3.set_yticklabels(yticklabels)
                            axL3.set_ylabel("Frequency [kHz]")
                            axL3.set_title("Spectrogram(A)")
                        
                        if job["Loudness_analyze"] == "on":
                            yrange = job["yrange_SN"]
                            axR1 = plt.axes(R1)
                            axR1.plot(self.time_axis_dec, self.sharpness_din, lw=1, color="blue", label="Din45629")
                            axR1.plot(self.time_axis_dec, self.sharpness_aures, lw=1, color="red", label="Aures")
                            axR1.legend(loc="upper right").get_frame().set_alpha(0.5)
                            axR1.set_xlim(0, self.t_end_sec-self.t_start_sec)
                            axR1.set_xticks(self.timeticks)
                            axR1.set_xticklabels([])
                            axR1.set_ylim(yrange[0], yrange[1])
                            axR1.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                            axR1.set_ylabel("Sharpness [acum]")
                            axR1.set_title("Sharpness")
                            
                            zrange = job["zrange_specCORE"]
                            axR2 = plt.axes(R2)
                            contour = axR2.contourf(X2, Y2, self.spec_loudness_level, cmap=self.cm, levels=np.arange(zrange[0], zrange[1]+zrange[2]/10, zrange[2]/10))
                            cbar = plt.colorbar(contour, ticks=[np.arange(zrange[0], zrange[1]+zrange[2], zrange[2])], orientation="vertical", pad=0.01)
                            cbar.set_label("Core Loudness [phon]")
                            axR2.set_xlim(0, self.t_end_sec-self.t_start_sec)
                            axR2.set_xticks(self.timeticks)
                            axR2.set_xticklabels(self.timelabels, rotation=90)
                            axR2.set_xlabel("Time")
                            axR2.set_ylim(0, 24)
                            axR2.set_yticks([0, 5, 10, 15, 20, 24])
                            axR2.set_ylabel("Bark scale [-]")
                            axR2.set_title("Spectrogram(SpecificLoudness)")
                        
                        savepath = os.path.join(folder_output_new, "AllFigures.png")
                        plt.savefig(savepath)
                        plt.close()
                        
                    else:
                        self.display_stop()
                
                
                
                if job["movie_post"] == "on":
                    # =============================================================================
                    ####                     音源付き動画作成
                    # =============================================================================
                    if self.started.is_set():
                        self.tree.set(self.record, 2, "音源付き動画作成中...")
                        
                        # ================== contour.png作成 ================== #
                        fig = plt.figure(figsize=(25, 17))
                        fig.patch.set_alpha(0) #背景色の透明度を設定
                        fig.suptitle(basename_wav, fontsize=25, fontname="MS Gothic")
                        fig.text(66, -18.5, f"v{version}", va='bottom', ha='right', fontsize=16)
                        L1 = [0.04, 0.67, 0.412, 0.23] #axes([左, 下, 幅, 高さ])
                        L2 = [0.04, 0.37, 0.490, 0.23] #axes([左, 下, 幅, 高さ])
                        L3 = [0.04, 0.08, 0.490, 0.23] #axes([左, 下, 幅, 高さ])
                        R1 = [0.54, 0.71, 0.412, 0.19] #axes([左, 下, 幅, 高さ])
                        R2 = [0.54, 0.38, 0.490, 0.23] #axes([左, 下, 幅, 高さ])
                        R3 = [0.54, 0.10, 0.490, 0.23] #axes([左, 下, 幅, 高さ])
                        
                        yrange = job["yrange_OA"]
                        axL1 = plt.axes(L1)
                        OA_A_mean = np.array(pd.DataFrame(self.OA_A).rolling(10).mean())
                        axL1.plot(time_axis, OA_A_mean, lw=1, color="blue", label="OA(A)")
                        axL1.set_xlim(0, self.t_end_sec-self.t_start_sec)
                        axL1.set_xticks(self.timeticks)
                        axL1.set_xticklabels([])
                        axL1.set_ylim(yrange[0], yrange[1])
                        axL1.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                        ax2 = axL1.twinx()
                        ax2.plot(self.time_axis_dec, self.loudness_level, lw=1, color="red", label="Loudness")
                        ax2.set_ylim(yrange[0], yrange[1])
                        ax2.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                        ax2.set_ylabel("Loudness Level [phon]")
                        h1, l1 = axL1.get_legend_handles_labels()
                        h2, l2 = ax2.get_legend_handles_labels()
                        axL1.legend(h1+h2, l1+l2, loc="upper right")
                        axL1.set_title("Overall(A) & Loudness")
                        
                        yrange = job["range_Hz"]
                        yticks = [10, 100, 1000, 10000]
                        yticks = list(filter(lambda i: i>=yrange[0] and i<=yrange[1], yticks))
                        yticklabels = [i*1e-3 for i in yticks]
                        yticklabels = [int(i) if i >= 1 else i for i in yticklabels]
                        zrange = job["zrange_specA"]
                        axL2 = plt.axes(L2)
                        contour = axL2.contourf(X1, Y1, self.third_octave_A, cmap=self.cm, levels=np.arange(zrange[0], zrange[1]+zrange[2]/10, zrange[2]/10))
                        cbar = plt.colorbar(contour, ticks=[np.arange(zrange[0], zrange[1]+zrange[2], zrange[2])], orientation="vertical", pad=0.01)
                        cbar.set_label("SPL [dB]")
                        axL2.set_xlim(0, self.t_end_sec-self.t_start_sec)
                        axL2.set_xticks(self.timeticks)
                        axL2.set_xticklabels([], rotation=90)
                        axL2.set_yscale("log")
                        axL2.set_ylim(yrange[0], yrange[1])
                        axL2.set_yticks(yticks)
                        axL2.set_yticklabels(yticklabels)
                        axL2.set_ylabel("Frequency [kHz]")
                        axL2.set_title("Spectrogram(A)")
                        
                        zrange = job["zrange_specCORE"]
                        axL3 = plt.axes(L3)
                        contour = axL3.contourf(X2, Y2, self.spec_loudness_level, cmap=self.cm, levels=np.arange(zrange[0], zrange[1]+zrange[2]/10, zrange[2]/10))
                        cbar = plt.colorbar(contour, ticks=[np.arange(zrange[0], zrange[1]+zrange[2], zrange[2])], orientation="vertical", pad=0.01)
                        cbar.set_label("Core Loudness [phon]")
                        axL3.set_xlim(0, self.t_end_sec-self.t_start_sec)
                        axL3.set_xticks(self.timeticks)
                        axL3.set_xticklabels(self.timelabels, rotation=90)
                        axL3.set_xlabel("Time")
                        axL3.set_ylim(0, 24)
                        axL3.set_yticks([0, 5, 10, 15, 20, 24])
                        axL3.set_ylabel("Bark scale [-]")
                        axL3.set_title("Spectrogram(SpecificLoudness)")
                        
                        yrange = job["yrange_SN"]
                        axR1 = plt.axes(R1)
                        axR1.plot(self.time_axis_dec, self.sharpness_din, lw=1, color="blue", label="Din45629")
                        axR1.plot(self.time_axis_dec, self.sharpness_aures, lw=1, color="red", label="Aures")
                        axR1.legend(loc="upper right")
                        axR1.set_xlim(0, self.t_end_sec-self.t_start_sec)
                        axR1.set_xticks(self.timeticks)
                        axR1.set_xticklabels(self.timelabels, rotation=90)
                        axR1.set_xlabel("Time")
                        axR1.set_ylim(yrange[0], yrange[1])
                        axR1.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                        axR1.set_ylabel("Sharpness [acum]")
                        axR1.set_title("Sharpness")
                        
                        plt.savefig(filepath_png)
                        plt.close()
                        
                        
                    else:
                        self.display_stop()
                    
                    
                    # ================== frame作成前準備 ================== #
                    fps = 10 #動画にするときのfpsのデフォルト設定（これによってFFT間隔が決まるため、偶数でなければならない！）
                    dec_fps = int((1/fps)/5e-4)
                    time_axis_fps = time_axis[::dec_fps]
                    self.time_axis_fps = time_axis[::dec_fps]
                    self.signal = signal
                    third_octave_A_fps = third_octave_A[:, ::dec_fps]
                    #for文表記
                    spec_loudness_level_fps = np.zeros((240, len(self.time_axis_fps)))
                    for row in range(spec_loudness.shape[0]):
                        for col in range(len(self.time_axis_fps)):
                            spec_loudness_level_fps[row, col] = sone_to_phon(spec_loudness[row, col*dec_fps])
                    
                    # ================== FFT解析 ================== #
                    Fs = 9600 #フレームサイズ[点数](=時間窓長)
                    overlap = 50 #オーバーラップ率[%]
                    signal_ol, N_ave = sm.ov(signal, fs, Fs, overlap)
                    han = np.hamming(Fs) #ハニング窓関数作成
                    acf = 1/(sum(han)/Fs) #Amplitude Correction Factorを計算
                    fft_array = np.array([np.abs(np.fft.fft(signal_ol[k]*han/(Fs/2))) for k in range(N_ave)])
                    freqList = np.fft.fftfreq(signal_ol[0].shape[0], d=1/fs) #(データ点数、サンプリング周期)
                    fft_array_dB = np.array([sm.Pa2dB(fft_array[i, :]) for i in range(N_ave)])
                    A_curve = sm.A_filter_fft(freqList)
                    fft_array_dB_A = np.array([fft_array_dB[i, :]+A_curve for i in range(N_ave)])
                    
                    # ================== frame1, frame2作成 ================== #
                    for frame_number, frame_time in enumerate(tqdm.tqdm(time_axis_fps[:-2], desc="動画作成プロセス", position=0, leave=False)):
                        if self.started.is_set():
                            
                            # ---------- 現在時刻ラベルの作成 ----------- #
                            time_current = frame_time + self.t_start_sec
                            time_current_label = str(tc.convert_time_micro(time_current))[:10]
                            if len(time_current_label) == 7:
                                time_current_label = time_current_label+".00"
                            
                            # ---------- 0.1秒間ごとのFFT(A)グラフ作成 ----------- #
                            xrange = job["range_Hz"]
                            xticks = [10, 20, 30, 40, 50, 60, 70, 80, 90,
                                      100, 200, 300, 400, 500, 600, 700, 800, 900,
                                      1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 
                                      10000, 11000, 12000, 13000]
                            xticks = list(filter(lambda i: i>=xrange[0] and i<=xrange[1], xticks))
                            yrange = job["yrange_FFT_A"]
                            
                            fig = plt.figure(figsize=(12, 10))
                            fig.patch.set_alpha(0) #背景色の透明度を設定
                            
                            ax1 = plt.axes([0.1, 0.55, 0.85, 0.35]) #axes([左, 下, 幅, 高さ])
                            ax1.plot(freqList, fft_array_dB_A[frame_number, :], lw=1, color="blue", label="FFT(A)")
                            ax1.plot(self.freq_band28, third_octave_A_fps[:, frame_number], lw=1, color="red", label="1/3octave(A)")
                            ax1.legend(loc="lower left").get_frame().set_alpha(0.5)
                            ax1.set_xscale("log")
                            ax1.set_xlim(xrange[0], xrange[1])
                            ax1.set_xticks(xticks)
                            ax1.set_xlabel("Frequency [Hz]")
                            ax1.set_ylim(yrange[0], yrange[1])
                            ax1.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                            ax1.set_ylabel("Amplitude [dB]")
                            ax1.set_title(f"FFT(A) & 1/3octave(A) Spectrum {round(frame_time, 1)}sec")
                            
                            # ---------- 0.1秒間ごとのラウドネススロープグラフ作成 ----------- #
                            yrange = job["zrange_specCORE"]
                            ax2 = plt.axes([0.1, 0.07, 0.85, 0.35]) #axes([左, 下, 幅, 高さ])
                            ax2.plot(spec_loudness_level_fps[:, frame_number], lw=1, color="blue", label="FFT(A)")
                            ax2.set_xlim(0, 240)
                            ax2.set_xticks(np.arange(0, 250, 10))
                            ax2.set_xticklabels(np.arange(0, 25, 1))
                            ax2.set_xlabel("Bark scale [-]")
                            ax2.set_ylim(yrange[0], yrange[1])
                            ax2.set_yticks(np.arange(yrange[0], yrange[1]+yrange[2], yrange[2]))
                            ax2.set_ylabel("Specific Loudness [phon]")
                            ax2.set_title(f"Specific Loudness Spectrum {round(frame_time, 1)}sec")
                            
                            # ---------- frame1としてpng出力 ----------- #
                            filename_frame1 = '%05d.png'%(int(frame_number))
                            filepath_frame1 = os.path.join(folder_frame1, filename_frame1)
                            plt.savefig(filepath_frame1)
                            plt.close()
                            
                            # ---------- frame1をcontour.pngに張り付けてframe2として出力 ----------- #
                            blank1 = np.zeros((233, 4, 3)) #(高さ, 幅, 3固定)
                            imwrite(filepath_bar1, blank1)
                            blank2 = np.zeros((282, 4, 3)) #(高さ, 幅, 3固定)
                            imwrite(filepath_bar2, blank2)
                            img_bar1 = Image.open(filepath_bar1)
                            img_bar2 = Image.open(filepath_bar2)
                            img_contour = Image.open(filepath_png)
                            img_frame1 = Image.open(filepath_frame1)
                            img_frame1.resize((777, 640))
                            
                            back_img = img_contour.copy()
                            x1 = 72 #黒線1出発座標
                            x2 = 970 #黒線2出発座標
                            l = 783 #黒線の出発座標から停止座標までの長さ
                            back_img.paste(img_bar2, (x1+round(l/len(time_axis_fps))*frame_number, 123)) #貼り付けるframe1.pngの左上のx座標, y座標
                            back_img.paste(img_bar1, (x2+round(l/len(time_axis_fps))*frame_number, 123)) #貼り付けるframe1.pngの左上のx座標, y座標
                            back_img.paste(img_bar2, (x1+round(l/len(time_axis_fps))*frame_number, 490)) #貼り付けるframe1.pngの左上のx座標, y座標
                            back_img.paste(img_bar2, (x1+round(l/len(time_axis_fps))*frame_number, 845)) #貼り付けるframe1.pngの左上のx座標, y座標
                            back_img.paste(img_frame1, (890, 438)) #貼り付けるframe1.pngの左上のx座標, y座標
                            
                            filename_frame2 = "%05d.png"%(int(frame_number))
                            filepath_frame2 = os.path.join(folder_frame2, filename_frame2)
                            back_img.save(filepath_frame2)
                            
                        else:
                            self.display_stop()
                    
                    # ---------- 生成されたframe2をレンダリング処理してmp4出力 ----------- #
                    codec = cv2.VideoWriter_fourcc(*'mp4v')
                    video = cv2.VideoWriter(filepath_mp4, codec, fps, (1800, 1224))
                    frames = glob.glob(folder_frame2+"\\*.png")
                    for frame in tqdm.tqdm(frames, desc="レンダリングプロセス", position=0, leave=False):
                        img = imread(frame)
                        video.write(img)
                    video.release() #動画ファイル作成時にはこの解放処理がないと作成した動画ファイルが開けない
                    
                    # ---------- mp4動画とwav音源を結合して音源付きmp4動画として出力 ----------- #
                    sm.connect_mp4_wav(filepath_mp4, filepath_wav, filepath_mp4_wav)
                    
                    # ---------- 生成されたmovie_sound.mp4をリネームして出力フォルダに保存 ----------- #
                    filepath_output = os.path.join(folder_output_new, "SoundMovie.mp4")
                    st.copy2(filepath_mp4_wav, filepath_output)
                    
                
                if self.started.is_set():
                    self.tree.set(self.record, 2, "完了")
                
                else:
                    self.display_stop()
                
                
                
            except:
                print("予期せぬエラーが発生しました。次のタスクにスキップします")
                traceback.print_exc()
                self.tree.set(self.record, 2, "エラー")
        
        
        # 処理終了時の処理
        self.display_finish()





# =============================================================================
#               メインファイル実行時処理
# =============================================================================
if __name__ == "__main__":
    app = Main()
    job_list = app.job_list
    #time_axis_fps = app.time_axis_fps
    #signal = app.signal
    #time_axis = app.time_axis