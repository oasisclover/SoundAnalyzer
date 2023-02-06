# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 22:07:39 2022

@author: Ryusei
"""

# 標準ライブラリimport
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import threading
import subprocess as sp
import pickle
import os
import datetime
import traceback

# 自作モジュールimport
import Create_DataSet as cds


class GUI(tk.Frame):
    
    def __init__(self, version, master=None):
        super().__init__(master)
        # =============================================================================
        #         初期設定
        # =============================================================================
        self.job_list = []
        self.folder_output = "output"
    
        filepath_txt = os.path.join("components", "Default.pickle")
        with open(filepath_txt, "rb") as f:
            self.def_name = pickle.load(f)
        
        # =============================================================================
        #         ウィンドウの作成
        # =============================================================================
        self.master.iconbitmap('components/icon.ico')
        self.master.title(f"SoundAnalyzer (Version {version})")
        self.master.geometry("1200x510")
        self.master.minsize(600, 400)
        
        # =============================================================================
        #         フレーム1作成
        # =============================================================================
        frame1 = tk.Frame(self.master)
        frame1.pack(side="top", padx=10, pady=10, anchor="nw", expand=0, fill=None)
        self.s1 = tk.StringVar()
        self.s1.set("下の追加ボタンを押して、解析したい音データ(*.wav)を追加してください")
        label1 = tk.Label(frame1, textvariable=self.s1, justify=tk.LEFT)
        label1.grid(row=0, column=0)
        
        # =============================================================================
        #         フレーム2作成
        # =============================================================================
        frame2 = tk.Frame(self.master)
        frame2.pack(side="top", padx=10, pady=0, anchor="nw", expand=0, fill=None)
        #追加ボタン作成
        self.btn_add = ttk.Button(frame2, text="追加", command=self.button_add)
        self.btn_add.grid(row=0, column=0)
        self.s2 = tk.StringVar()
        self.s2.set("※軸目盛表記 : [目盛最小値, 目盛最大値, 目盛幅]")
        label = ttk.Label(frame2, textvariable=self.s2)
        label.grid(row=0, column=1, padx=780)
        
        # =============================================================================
        #         フレーム3作成
        # =============================================================================
        frame3 = tk.Frame(self.master)
        frame3.pack(side="top", padx=10, pady=10, anchor="nw", expand=1, fill=tk.BOTH)
        # スクロースバー作成
        self.scrollx_bar = tk.Scrollbar(frame3, orient="horizontal")
        self.scrollx_bar.pack(side=tk.BOTTOM, fill="x")
        self.scrolly_bar = tk.Scrollbar(frame3, orient="vertical")
        self.scrolly_bar.pack(side=tk.RIGHT, fill="y")
        # ツリービュー作成
        self.tree = ttk.Treeview(frame3, xscrollcommand=self.scrollx_bar.set, yscrollcommand=self.scrolly_bar.set)
        # 各列の定義
        self.tree["columns"] = list(range(1, 19, 1))
        self.tree.column(1, width=30, minwidth=30, stretch="no", anchor=tk.W)
        self.tree.column(2, width=140, minwidth=30, stretch="no", anchor=tk.W)
        self.tree.column(3, width=350, minwidth=30, stretch="no", anchor=tk.W)
        self.tree.column(4, width=110, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(5, width=60, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(6, width=65, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(7, width=80, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(8, width=55, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(9, width=55, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(10, width=100, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(11, width=110, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(12, width=110, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(13, width=110, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(14, width=110, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(15, width=110, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(16, width=110, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(17, width=110, minwidth=30, stretch="no", anchor=tk.E)
        self.tree.column(18, width=130, minwidth=30, stretch="no", anchor=tk.E)
        # ヘッダーの定義
        self.tree["show"] = "headings"
        self.tree.heading(1, text="No.", anchor=tk.CENTER)
        self.tree.heading(2, text="状態", anchor=tk.CENTER)
        self.tree.heading(3, text="ファイル名(*.wav)", anchor=tk.CENTER)
        self.tree.heading(4, text="時間範囲", anchor=tk.CENTER)
        self.tree.heading(5, text="振幅補正", anchor=tk.CENTER)
        self.tree.heading(6, text="A特性解析", anchor=tk.CENTER)
        self.tree.heading(7, text="ラウドネス解析", anchor=tk.CENTER)
        self.tree.heading(8, text="FFT解析", anchor=tk.CENTER)
        self.tree.heading(9, text="動画出力", anchor=tk.CENTER)
        self.tree.heading(10, text="解析周波数範囲", anchor=tk.CENTER)
        self.tree.heading(11, text="周波数軸目盛[Hz]", anchor=tk.CENTER)
        self.tree.heading(12, text="FFT(FLAT) Y軸目盛[dB]", anchor=tk.CENTER)
        self.tree.heading(13, text="FFT(A) Y軸目盛[dB]", anchor=tk.CENTER)
        self.tree.heading(14, text="OA(A) Y軸目盛[dB]", anchor=tk.CENTER)
        self.tree.heading(15, text="SN Y軸目盛[acum]", anchor=tk.CENTER)
        self.tree.heading(16, text="Spec(FLAT) Z軸目盛[dB]", anchor=tk.CENTER)
        self.tree.heading(17, text="Spec(A) Z軸目盛[dB]", anchor=tk.CENTER)
        self.tree.heading(18, text="Spec(CORE) Z軸目盛[phon]", anchor=tk.CENTER)
        # ツリー配置
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.scrollx_bar.config(command=self.tree.xview)
        self.scrolly_bar.config(command=self.tree.yview)
        
        # =============================================================================
        #         フレーム4作成
        # =============================================================================
        self.frame4 = tk.Frame(self.master)
        self.frame4.pack(side=tk.LEFT, anchor="sw", expand=0, fill=tk.X)
        # リセットボタンの作成
        self.btn_reset = ttk.Button(self.frame4, text="リセット", command=self.button_reset)
        self.btn_reset.pack(side=tk.LEFT, padx=10, pady=10, anchor="sw")
        # 削除ボタンの作成
        self.btn_remove = ttk.Button(self.frame4, text="削除", command=self.button_remove)
        self.btn_remove.pack(side=tk.LEFT, padx=10, pady=10, anchor="sw")
        # 複製ボタンの作成
        self.btn_duplicate = ttk.Button(self.frame4, text="複製", command=self.button_duplicate)
        self.btn_duplicate.pack(side=tk.LEFT, padx=10, pady=10, anchor="sw")
        # 時間設定ボタンの作成
        self.btn_setting_time = ttk.Button(self.frame4, text="時間設定", command=self.button_setting_time)
        self.btn_setting_time.pack(side=tk.LEFT, padx=10, pady=10, anchor="sw")
        # 解析設定ボタンの作成
        self.btn_setting_analyze = ttk.Button(self.frame4, text="解析設定", command=self.button_setting_analyze)
        self.btn_setting_analyze.pack(side=tk.LEFT, padx=10, pady=10, anchor="sw")
        # グラフ設定ボタンの作成
        self.btn_setting_graph = ttk.Button(self.frame4, text="グラフ設定", command=self.button_setting_graph)
        self.btn_setting_graph.pack(side=tk.LEFT, padx=10, pady=10, anchor="sw")
        
        # =============================================================================
        #         フレーム5作成
        # =============================================================================
        self.frame5 = tk.Frame(self.master)
        self.frame5.pack(side=tk.RIGHT, anchor="se", expand=0, fill=tk.X)
        #　終了ボタンの作成
        self.btn_end = ttk.Button(self.frame5, text="終了", command=self.button_end)
        self.btn_end.pack(side=tk.RIGHT, padx=10, pady=10, anchor="sw")
        #　解析ボタンの作成
        self.btn_analyze = ttk.Button(self.frame5, text="解析", command=self.button_analyze)
        self.btn_analyze.pack(side=tk.RIGHT, padx=10, pady=10, anchor="sw")
        
        return
    
    
    
    # =============================================================================
    #     ファイルの追加ボタンを押したときの処理
    # =============================================================================
    def button_add(self):
        filepath_def_time = os.path.join("parameter", "time", self.def_name["time_parameter"])
        filepath_def_analyze = os.path.join("parameter", "analyze", self.def_name["analyze_parameter"])
        filepath_def_graph = os.path.join("parameter", "graph", self.def_name["graph_parameter"])
        with open(filepath_def_time, "rb") as tf:
            def_para_time = pickle.load(tf)
        with open(filepath_def_analyze, "rb") as tf:
            def_para_analyze = pickle.load(tf)
        with open(filepath_def_graph, "rb") as tf:
            def_para_graph = pickle.load(tf)
        
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
        
        job_amount = len(self.tree.get_children())
        filetype = [("WAV files", "*.wav")]
        filepath_list = filedialog.askopenfilename(filetypes=filetype, multiple=True)
        for job_number in range(len(filepath_list)):
            filepath = filepath_list[job_number]
            filename = os.path.basename(filepath)
            job = cds.Create_DataSet(filepath,
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
                                     zrange_specCORE)
            self.job_list.append(job)
            
            job_ID = self.tree.insert("", "end", values=(job_amount+job_number+1,
                                                         "待機中",
                                                         job["filename"],
                                                         f"{job['t_start']}~{job['t_end']}",
                                                         job["amp_calib"],
                                                         job["A_analyze"],
                                                         job["Loudness_analyze"],
                                                         job["FFT_analyze"],
                                                         job["movie_post"],
                                                         job["freq_range"],
                                                         f"{job['range_Hz'][0]}Hz~{job['range_Hz'][1]}Hz",
                                                         f"{job['yrange_FFT_FLAT']}",
                                                         f"{job['yrange_FFT_A']}",
                                                         f"{job['yrange_OA']}",
                                                         f"{job['yrange_SN']}",
                                                         f"{job['zrange_specFLAT']}",
                                                         f"{job['zrange_specA']}",
                                                         f"{job['zrange_specCORE']}"))
            
            if job["freq_range"] != "ALL":
                self.tree.set(job_ID, 9, f"{job['freq_range'][0]}Hz~{job['freq_range'][1]}Hz")
        
        return
    
    
    
    # =============================================================================
    #     リセットボタンを押したときの処理
    # =============================================================================
    def button_reset(self):
        if len(self.tree.get_children()) != 0:
            # ウィンドウの更新
            self.s1.set("下の追加ボタンを押して、解析したい音データ(*.wav)を追加してください")
            self.btn_add["state"] = "able"
            self.btn_remove["state"] = "able"
            self.btn_duplicate["state"] = "able"
            self.btn_setting_analyze["state"] = "able"
            self.btn_setting_time["state"] = "able"
            self.btn_setting_graph["state"] = "able"
            
            # フレーム5再作成
            self.frame5.destroy()
            self.frame5 = tk.Frame(self.master)
            self.frame5.pack(side=tk.RIGHT, anchor="se", expand=0, fill=tk.X)
            #　終了ボタンの作成
            self.btn_end = ttk.Button(self.frame5, text="終了", command=self.button_end)
            self.btn_end.pack(side=tk.RIGHT, padx=10, pady=10, anchor="sw")
            #　解析ボタンの作成
            self.btn_analyze = ttk.Button(self.frame5, text="解析", command=self.button_analyze)
            self.btn_analyze.pack(side=tk.RIGHT, padx=10, pady=10, anchor="sw")
            
            # ジョブデータのリセット
            self.job_list = []
            # ツリービュー内の表示をオールクリア
            for job_ID in self.tree.get_children():
                self.tree.delete(job_ID)
        else:
            pass
        
        return
    
    
    
    # =============================================================================
    #     削除ボタンを押したときの処理
    # =============================================================================
    def button_remove(self):
        job_del_index_list = []
        for job_ID in self.tree.selection():
            item = self.tree.item(job_ID)
            job_del_index = item["values"][0]-1
            job_del_index_list.append(job_del_index)
        dellist = lambda items, indices: [item for idx, item in enumerate(items) if idx not in indices]
        self.job_list = dellist(self.job_list, job_del_index_list)
        
        # 一旦、ツリー内オールクリア
        for job_ID in self.tree.get_children():
            self.tree.delete(job_ID)
        # 未選択jobのみ再表示
        for job_number in range(len(self.job_list)):
            job = self.job_list[job_number]
            job_ID = self.tree.insert("", "end", values=(job_number+1,
                                                         "待機中",
                                                         job["filename"],
                                                         f"{job['t_start']}~{job['t_end']}",
                                                         job["amp_calib"],
                                                         job["A_analyze"],
                                                         job["Loudness_analyze"],
                                                         job["FFT_analyze"],
                                                         job["movie_post"],
                                                         job["freq_range"],
                                                         f"{job['range_Hz'][0]}Hz~{job['range_Hz'][1]}Hz",
                                                         f"{job['yrange_FFT_FLAT']}",
                                                         f"{job['yrange_FFT_A']}",
                                                         f"{job['yrange_OA']}",
                                                         f"{job['yrange_SN']}",
                                                         f"{job['zrange_specFLAT']}",
                                                         f"{job['zrange_specA']}",
                                                         f"{job['zrange_specCORE']}"))
            
            if job["freq_range"] != "ALL":
                self.tree.set(job_ID, 9, f"{job['freq_range'][0]}Hz~{job['freq_range'][1]}Hz")
        
        return
    
    
    
    # =============================================================================
    #     複製ボタンを押したときの処理
    # =============================================================================
    def button_duplicate(self):
        item_list = [self.tree.item(self.tree.selection()[i])["values"] for i in range(len(self.tree.selection()))]
        job_number_list = [item_list[i][0] for i in range(len(item_list))]
        
        for i in range(len(self.tree.selection())):
            job_dup = self.job_list[job_number_list[i]-1].copy()
            self.job_list.append(job_dup)
            job_amount = len(self.tree.get_children())
            job_dup_ID = self.tree.insert("", "end", values=(job_amount+1,
                                                             "待機中",
                                                             job_dup["filename"],
                                                             f"{job_dup['t_start']}~{job_dup['t_end']}",
                                                             job_dup["amp_calib"],
                                                             job_dup["A_analyze"],
                                                             job_dup["Loudness_analyze"],
                                                             job_dup["FFT_analyze"],
                                                             job_dup["movie_post"],
                                                             job_dup["freq_range"],
                                                             f"{job_dup['range_Hz'][0]}Hz~{job_dup['range_Hz'][1]}Hz",
                                                             f"{job_dup['yrange_FFT_FLAT']}",
                                                             f"{job_dup['yrange_FFT_A']}",
                                                             f"{job_dup['yrange_OA']}",
                                                             f"{job_dup['yrange_SN']}",
                                                             f"{job_dup['zrange_specFLAT']}",
                                                             f"{job_dup['zrange_specA']}",
                                                             f"{job_dup['zrange_specCORE']}"))
            
            if job_dup["freq_range"] != "ALL":
                self.tree.set(job_dup_ID, 9, f"{job_dup['freq_range'][0]}Hz~{job_dup['freq_range'][1]}Hz")
        
        return
    
    
    
    # =============================================================================
    #     時間設定ボタンを押したときの処理
    # =============================================================================
    def button_setting_time(self):
        self.setting_mode = "time"
        try:
            self.job_selected_ID = self.tree.selection()
            self.item_list = []
            self.job_number_selected_list = []
            for i in range(len(self.job_selected_ID)):
                self.item_list.append(self.tree.item(self.job_selected_ID[i]))
                self.job_number_selected_list.append(self.item_list[i]["values"][0])
            
            t_start = self.job_list[self.job_number_selected_list[0]-1]["t_start"]
            t_end = self.job_list[self.job_number_selected_list[0]-1]["t_end"]
            
            # =============================================================================
            #             設定ウィンドウ作成
            # =============================================================================
            self.root_setting = tk.Toplevel(self.master)
            self.root_setting.grab_set()
            self.root_setting.title("時間設定")
            self.root_setting.resizable(width=False, height=False)
            
            # =============================================================================
            #             フレームサブ0の作成
            # =============================================================================
            frame_sub0 = tk.LabelFrame(self.root_setting, text="パラメータ参照・保存")
            frame_sub0.pack(padx=10, pady=5, ipadx=5, ipady=2, side=tk.TOP, anchor="sw")
            # 既存のデフォルトパラメータを表示
            self.setting_s0 = tk.StringVar()
            self.setting_s0.set('wav追加時パラメータ　：　"{}"'.format(os.path.splitext(self.def_name["time_parameter"])[0]))
            tk.Label(frame_sub0, textvariable=self.setting_s0).pack(side=tk.TOP, anchor="w", padx=2, pady=2)
            # デフォルト変更ボタンの作成
            self.btn_def = ttk.Button(frame_sub0, text="wav追加時パラメータ変更", command=self.button_setting_change)
            self.btn_def.pack(side=tk.TOP, anchor="nw", padx=2, pady=2)
            # 参照ボタンの作成
            self.btn_load = ttk.Button(frame_sub0, text="参照", command=self.button_setting_load)
            self.btn_load.pack(side=tk.LEFT, anchor="nw", padx=2, pady=2)
            # 保存ボタンの作成
            self.btn_save = ttk.Button(frame_sub0, text="保存", command=self.button_setting_save)
            self.btn_save.pack(side=tk.LEFT, anchor="nw", padx=2, pady=2)
            
            # =============================================================================
            #             フレームサブ2の作成
            # =============================================================================
            frame_sub2 = tk.LabelFrame(self.root_setting, text="解析の設定")
            frame_sub2.pack(padx=10, pady=5, ipadx=5, ipady=5, side=tk.TOP, anchor="sw")
            
            self.setting_s21 = tk.StringVar()
            self.setting_s21.set("開始時間 　")
            self.setting_s22 = tk.StringVar()
            self.setting_s22.set(" :")
            self.setting_s23 = tk.StringVar()
            self.setting_s23.set("終了時間 　")            
            
            label = tk.Label(frame_sub2, textvariable=self.setting_s21)
            label.grid(row=0, column=0, padx=0, pady=2)
            self.ebox21 = tk.Entry(frame_sub2, width=2, relief=tk.SOLID)
            self.ebox21.insert(0, t_start.hour)
            self.ebox21.grid(row=0, column=1, padx=0, pady=2)
            label = tk.Label(frame_sub2, textvariable=self.setting_s22)
            label.grid(row=0, column=2, padx=0, pady=2)
            self.ebox22 = tk.Entry(frame_sub2, width=2, relief=tk.SOLID)
            self.ebox22.insert(0, t_start.minute)
            self.ebox22.grid(row=0, column=3, padx=0, pady=2)
            label = tk.Label(frame_sub2, textvariable=self.setting_s22)
            label.grid(row=0, column=4, padx=0, pady=2)
            self.ebox23 = tk.Entry(frame_sub2, width=2, relief=tk.SOLID)
            self.ebox23.insert(0, t_start.second)
            self.ebox23.grid(row=0, column=5, padx=0, pady=2)
            
            label = tk.Label(frame_sub2, textvariable=self.setting_s23)
            label.grid(row=1, column=0, padx=0, pady=2)
            self.ebox24 = tk.Entry(frame_sub2, width=2, relief=tk.SOLID)
            self.ebox24.insert(0, t_end.hour)
            self.ebox24.grid(row=1, column=1, padx=0, pady=2)
            label = tk.Label(frame_sub2, textvariable=self.setting_s22)
            label.grid(row=1, column=2, padx=0, pady=2)
            self.ebox25 = tk.Entry(frame_sub2, width=2, relief=tk.SOLID)
            self.ebox25.insert(0, t_end.minute)
            self.ebox25.grid(row=1, column=3, padx=0, pady=2)
            label = tk.Label(frame_sub2, textvariable=self.setting_s22)
            label.grid(row=1, column=4, padx=0, pady=2)
            self.ebox26 = tk.Entry(frame_sub2, width=2, relief=tk.SOLID)
            self.ebox26.insert(0, t_end.second)
            self.ebox26.grid(row=1, column=5, padx=0, pady=2)
            
            # =============================================================================
            #             フレームサブ5作成
            # =============================================================================
            frame_sub5 = tk.Frame(self.root_setting)
            frame_sub5.pack(padx=10, pady=5, side=tk.TOP, anchor="se")
            
            # OKボタンの作成
            self.btn_okey = ttk.Button(frame_sub5, text="OK", command=self.button_setting_okey)
            self.btn_okey.grid(row=0, column=0)
            # キャンセルボタンの作成
            self.btn_cancel = ttk.Button(frame_sub5, text="キャンセル", command=self.button_setting_cancel)
            self.btn_cancel.grid(row=0, column=1)
            
        # 何も選択していない状態で設定ボタンをクリックした場合
        except IndexError:
            pass
        return
    
    
    
    # =============================================================================
    #     解析設定ボタンを押したときの処理
    # =============================================================================
    def button_setting_analyze(self):
        
        # =============================================================================
        #         周波数範囲エントリーボックスのバインド処理
        # =============================================================================
        def change_state(event):
            if self.v41.get() == "ALL":
                self.ebox41.delete(0, tk.END)
                self.ebox42.delete(0, tk.END)
                self.ebox41.insert(0, "--")
                self.ebox42.insert(0, "--")
                self.ebox41.config(state="disabled")
                self.ebox42.config(state="disabled")
            else:
                self.ebox41.config(state="normal")
                self.ebox42.config(state="normal")
                self.ebox41.delete(0, tk.END)
                self.ebox42.delete(0, tk.END)
                self.ebox41.insert(0, 1000)
                self.ebox42.insert(0, 10000)
            return
        
        
        self.setting_mode = "analyze"
        try:
            self.job_selected_ID = self.tree.selection()
            self.item_list = []
            self.job_number_selected_list = []
            for i in range(len(self.job_selected_ID)):
                self.item_list.append(self.tree.item(self.job_selected_ID[i]))
                self.job_number_selected_list.append(self.item_list[i]["values"][0])
            
            amp_calib = self.job_list[self.job_number_selected_list[0]-1]["amp_calib"]
            A_analyze = self.job_list[self.job_number_selected_list[0]-1]["A_analyze"]
            Loudness_analyze = self.job_list[self.job_number_selected_list[0]-1]["Loudness_analyze"]
            FFT_analyze = self.job_list[self.job_number_selected_list[0]-1]["FFT_analyze"]
            movie_post = self.job_list[self.job_number_selected_list[0]-1]["movie_post"]
            freq_range = self.job_list[self.job_number_selected_list[0]-1]["freq_range"]
            
            # =============================================================================
            #             設定ウィンドウ作成
            # =============================================================================
            self.root_setting = tk.Toplevel(self.master)
            self.root_setting.grab_set()
            self.root_setting.title("解析設定")
            self.root_setting.resizable(width=False, height=False)
            
            # =============================================================================
            #             フレームサブ0の作成
            # =============================================================================
            frame_sub0 = tk.LabelFrame(self.root_setting, text="パラメータ参照・保存")
            frame_sub0.pack(padx=10, pady=5, ipadx=5, ipady=2, side=tk.TOP, anchor="sw")
            # 既存のデフォルトパラメータを表示
            self.setting_s0 = tk.StringVar()
            self.setting_s0.set('wav追加時パラメータ　：　"{}"'.format(os.path.splitext(self.def_name["analyze_parameter"])[0]))
            tk.Label(frame_sub0, textvariable=self.setting_s0).pack(side=tk.TOP, anchor="w", padx=2, pady=2)
            # デフォルト変更ボタンの作成
            self.btn_def = ttk.Button(frame_sub0, text="wav追加時パラメータ変更", command=self.button_setting_change)
            self.btn_def.pack(side=tk.TOP, anchor="nw", padx=2, pady=2)
            # 参照ボタンの作成
            self.btn_load = ttk.Button(frame_sub0, text="参照", command=self.button_setting_load)
            self.btn_load.pack(side=tk.LEFT, anchor="nw", padx=2, pady=2)
            # 保存ボタンの作成
            self.btn_save = ttk.Button(frame_sub0, text="保存", command=self.button_setting_save)
            self.btn_save.pack(side=tk.LEFT, anchor="nw", padx=2, pady=2)
            
            # =============================================================================
            #             フレームサブ1の作成
            # =============================================================================
            frame_sub1 = tk.LabelFrame(self.root_setting, text="解析の設定")
            frame_sub1.pack(padx=10, pady=5, ipadx=5, ipady=5, side=tk.TOP, anchor="sw")
            
            self.setting_s10 = tk.StringVar()
            self.setting_s10.set("振幅補正　:")
            label = tk.Label(frame_sub1, textvariable=self.setting_s10)
            label.grid(row=0, column=0, padx=2, pady=2)
            self.v10 = tk.StringVar()
            self.v10.set(amp_calib)
            cbox10 = ttk.Combobox(frame_sub1, height=2, width=5, state="readonly", values=("*1", "*√2"), textvariable=self.v10)
            cbox10.grid(row=0, column=1, padx=1, pady=2)
            
            frame_chk = tk.Frame(frame_sub1)
            frame_chk.grid(row=1, column=0, padx=2, pady=2)
            self.chk11 = tk.BooleanVar()
            if A_analyze == "on":
                self.chk11.set(True)
            else:
                self.chk11.set(False)
            chkbox11 = tk.Checkbutton(frame_chk, text='A特性解析', var=self.chk11)
            chkbox11.pack(side=tk.TOP, anchor="sw", padx=2, pady=0)
            
            self.chk12 = tk.BooleanVar()
            if Loudness_analyze == "on":
                self.chk12.set(True)
            else:
                self.chk12.set(False)
            chkbox12 = tk.Checkbutton(frame_chk, text='ラウドネス解析', var=self.chk12)
            chkbox12.pack(side=tk.TOP, anchor="sw", padx=2, pady=0)
            
            self.chk13 = tk.BooleanVar()
            if FFT_analyze == "on":
                self.chk13.set(True)
            else:
                self.chk13.set(False)
            chkbox13 = tk.Checkbutton(frame_chk, text='FFT解析', var=self.chk13)
            chkbox13.pack(side=tk.TOP, anchor="sw", padx=2, pady=0)
            
            self.chk14 = tk.BooleanVar()
            if movie_post == "on":
                self.chk14.set(True)
            else:
                self.chk14.set(False)
            chkbox14 = tk.Checkbutton(frame_chk, text='動画出力', var=self.chk14)
            chkbox14.pack(side=tk.TOP, anchor="sw", padx=2, pady=0)
            
            # =============================================================================
            #             フレームサブ4作成
            # =============================================================================
            frame_sub4 = tk.LabelFrame(self.root_setting, text="周波数範囲の設定")
            frame_sub4.pack(padx=10, pady= 5, ipadx=5, ipady=5, side=tk.TOP, anchor="sw")
            
            self.v41 = tk.StringVar()
            if freq_range == "ALL":
                self.v41.set(freq_range)
            else:
                self.v41.set("カスタム")
            cbox41 = ttk.Combobox(frame_sub4, height=2, width=7, state="readonly", values=("ALL", "カスタム"), textvariable=self.v41)
            cbox41.bind("<<ComboboxSelected>>", change_state)
            cbox41.grid(row=0, column=1, columnspan=2, padx=2, pady=2)
            self.ebox41 = tk.Entry(frame_sub4, width=7, relief=tk.SOLID)
            self.ebox42 = tk.Entry(frame_sub4, width=7, relief=tk.SOLID)
            if freq_range == "ALL":
                self.ebox41.insert(0, "--")
                self.ebox42.insert(0, "--")
                self.ebox41.config(state="disabled")
                self.ebox42.config(state="disabled")
            else:
                self.ebox41.insert(0, freq_range[0])
                self.ebox42.insert(0, freq_range[1])
            self.ebox41.grid(row=1, column=0, padx=2, pady=2)
            self.ebox42.grid(row=1, column=2, padx=2, pady=2)
            self.setting_s41 = tk.StringVar()
            self.setting_s42 = tk.StringVar()
            self.setting_s43 = tk.StringVar()
            self.setting_s41.set("選択")
            self.setting_s42.set("Hz ~")
            self.setting_s43.set("Hz")
            label = tk.Label(frame_sub4, textvariable=self.setting_s41)
            label.grid(row=0, column=0, pady=2)
            label = tk.Label(frame_sub4, textvariable=self.setting_s42)
            label.grid(row=1, column=1, pady=2)
            label = tk.Label(frame_sub4, textvariable=self.setting_s43)
            label.grid(row=1, column=3, pady=2)
            
            # =============================================================================
            #             フレームサブ5作成
            # =============================================================================
            frame_sub5 = tk.Frame(self.root_setting)
            frame_sub5.pack(padx=10, pady=5, side=tk.TOP, anchor="se")
            
            # OKボタンの作成
            self.btn_okey = ttk.Button(frame_sub5, text="OK", command=self.button_setting_okey)
            self.btn_okey.grid(row=0, column=0)
            # キャンセルボタンの作成
            self.btn_cancel = ttk.Button(frame_sub5, text="キャンセル", command=self.button_setting_cancel)
            self.btn_cancel.grid(row=0, column=1)
            
        # 何も選択していない状態で設定ボタンをクリックした場合
        except IndexError:
            pass
        return
    
    
    
    # =============================================================================
    #     グラフ設定ボタンを押したときの処理
    # =============================================================================
    def button_setting_graph(self):
        self.setting_mode = "graph"
        try:
            self.job_selected_ID = self.tree.selection()
            self.item_list = []
            self.job_number_selected_list = []
            for i in range(len(self.job_selected_ID)):
                self.item_list.append(self.tree.item(self.job_selected_ID[i]))
                self.job_number_selected_list.append(self.item_list[i]["values"][0])
            
            range_Hz = self.job_list[self.job_number_selected_list[0]-1]["range_Hz"]
            yrange_FFT_FLAT = self.job_list[self.job_number_selected_list[0]-1]["yrange_FFT_FLAT"]
            yrange_FFT_A = self.job_list[self.job_number_selected_list[0]-1]["yrange_FFT_A"]
            yrange_OA = self.job_list[self.job_number_selected_list[0]-1]["yrange_OA"]
            yrange_SN = self.job_list[self.job_number_selected_list[0]-1]["yrange_SN"]
            zrange_specFLAT = self.job_list[self.job_number_selected_list[0]-1]["zrange_specFLAT"]
            zrange_specA = self.job_list[self.job_number_selected_list[0]-1]["zrange_specA"]
            zrange_specCORE = self.job_list[self.job_number_selected_list[0]-1]["zrange_specCORE"]
            
            # =============================================================================
            #             設定ウィンドウ作成
            # =============================================================================
            self.root_setting = tk.Toplevel(self.master)
            self.root_setting.grab_set()
            self.root_setting.title("グラフ設定")
            self.root_setting.resizable(width=False, height=False)
            
            # =============================================================================
            #             フレームサブ0の作成
            # =============================================================================
            frame_sub0 = tk.LabelFrame(self.root_setting, text="パラメータ参照・保存")
            frame_sub0.pack(padx=10, pady=5, ipadx=5, ipady=2, side=tk.TOP, anchor="sw")
            # 既存のデフォルトパラメータを表示
            self.setting_s0 = tk.StringVar()
            self.setting_s0.set('wav追加時パラメータ　：　"{}"'.format(os.path.splitext(self.def_name["graph_parameter"])[0]))
            tk.Label(frame_sub0, textvariable=self.setting_s0).pack(side=tk.TOP, anchor="w", padx=2, pady=2)
            # デフォルト変更ボタンの作成
            self.btn_def = ttk.Button(frame_sub0, text="wav追加時パラメータ変更", command=self.button_setting_change)
            self.btn_def.pack(side=tk.TOP, anchor="nw", padx=2, pady=2)
            # 参照ボタンの作成
            self.btn_load = ttk.Button(frame_sub0, text="参照", command=self.button_setting_load)
            self.btn_load.pack(side=tk.LEFT, anchor="nw", padx=2, pady=2)
            # 保存ボタンの作成
            self.btn_save = ttk.Button(frame_sub0, text="保存", command=self.button_setting_save)
            self.btn_save.pack(side=tk.LEFT, anchor="nw", padx=2, pady=2)
            
            # =============================================================================
            #             フレームサブ3の作成
            # =============================================================================
            frame_sub3 = tk.LabelFrame(self.root_setting, text="グラフ軸目盛の設定")
            frame_sub3.pack(padx=10, pady=5, ipadx=5, ipady=5, side=tk.TOP, anchor="sw")
            
            self.setting_s30 = tk.StringVar()
            self.setting_s31 = tk.StringVar()
            self.setting_s32 = tk.StringVar()
            self.setting_s33 = tk.StringVar()
            self.setting_s34 = tk.StringVar()
            self.setting_s35 = tk.StringVar()
            self.setting_s36 = tk.StringVar()
            self.setting_sA = tk.StringVar()
            self.setting_sB = tk.StringVar()
            self.setting_sC = tk.StringVar()
            self.setting_sD = tk.StringVar()
            self.setting_sE = tk.StringVar()
            self.setting_sF = tk.StringVar()
            self.setting_sG = tk.StringVar()
            self.setting_sH = tk.StringVar()
            self.setting_s30.set("※軸目盛表記")         
            self.setting_s31.set(":  [")         
            self.setting_s32.set("目盛最小値")         
            self.setting_s33.set("目盛最大値")         
            self.setting_s34.set("目盛幅")         
            self.setting_s35.set(", ")         
            self.setting_s36.set("]")         
            self.setting_sA.set("FFT X軸[Hz]")         
            self.setting_sB.set("FFT(FLAT) Y軸[dB]")         
            self.setting_sC.set("FFT(A) Y軸[dB]")         
            self.setting_sD.set("Overall Y軸[dB]")         
            self.setting_sE.set("Sharpness Y軸[acum]")         
            self.setting_sF.set("spec(FLAT) Z軸[dB]")         
            self.setting_sG.set("spec(A) Z軸[dB]")         
            self.setting_sH.set("spec(CORE) Z軸[phon]")
            
            label = tk.Label(frame_sub3, textvariable=self.setting_s30)
            label.grid(row=0, column=0, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s31)
            label.grid(row=0, column=1, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s32)
            label.grid(row=0, column=2, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=0, column=3, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s33)
            label.grid(row=0, column=4, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=0, column=5, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s34)
            label.grid(row=0, column=6, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s36)
            label.grid(row=0, column=7, padx=0, pady=2)
            
            label = tk.Label(frame_sub3, textvariable=self.setting_sA)
            label.grid(row=1, column=0, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s31)
            label.grid(row=1, column=1, padx=0, pady=2)
            self.A1 = tk.StringVar()
            self.A1.set(range_Hz[0])
            clist = (10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
                     2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000)
            cboxA1 = ttk.Combobox(frame_sub3, height=10, width=5, state="readonly", values=clist, textvariable=self.A1)
            cboxA1.grid(row=1, column=2, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=1, column=3, padx=0, pady=2)
            self.A2 = tk.StringVar()
            self.A2.set(range_Hz[1])
            cboxA2 = ttk.Combobox(frame_sub3, height=10, width=5, state="readonly", values=clist, textvariable=self.A2)
            cboxA2.grid(row=1, column=4, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s36)
            label.grid(row=1, column=5, padx=0, pady=2)
            
            label = tk.Label(frame_sub3, textvariable=self.setting_sB)
            label.grid(row=2, column=0, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s31)
            label.grid(row=2, column=1, padx=0, pady=2)
            self.eboxB1 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxB1.insert(0, yrange_FFT_FLAT[0])
            self.eboxB1.grid(row=2, column=2, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=2, column=3, padx=0, pady=2)
            self.eboxB2 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxB2.insert(0, yrange_FFT_FLAT[1])
            self.eboxB2.grid(row=2, column=4, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=2, column=5, padx=0, pady=2)
            self.eboxB3 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxB3.insert(0, yrange_FFT_FLAT[2])
            self.eboxB3.grid(row=2, column=6, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s36)
            label.grid(row=2, column=7, padx=0, pady=2)
            
            label = tk.Label(frame_sub3, textvariable=self.setting_sC)
            label.grid(row=3, column=0, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s31)
            label.grid(row=3, column=1, padx=0, pady=2)
            self.eboxC1 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxC1.insert(0, yrange_FFT_A[0])
            self.eboxC1.grid(row=3, column=2, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=3, column=3, padx=0, pady=2)
            self.eboxC2 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxC2.insert(0, yrange_FFT_A[1])
            self.eboxC2.grid(row=3, column=4, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=3, column=5, padx=0, pady=2)
            self.eboxC3 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxC3.insert(0, yrange_FFT_A[2])
            self.eboxC3.grid(row=3, column=6, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s36)
            label.grid(row=3, column=7, padx=0, pady=2)
            
            label = tk.Label(frame_sub3, textvariable=self.setting_sD)
            label.grid(row=4, column=0, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s31)
            label.grid(row=4, column=1, padx=0, pady=2)
            self.eboxD1 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxD1.insert(0, yrange_OA[0])
            self.eboxD1.grid(row=4, column=2, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=4, column=3, padx=0, pady=2)
            self.eboxD2 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxD2.insert(0, yrange_OA[1])
            self.eboxD2.grid(row=4, column=4, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=4, column=5, padx=0, pady=2)
            self.eboxD3 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxD3.insert(0, yrange_OA[2])
            self.eboxD3.grid(row=4, column=6, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s36)
            label.grid(row=4, column=7, padx=0, pady=2)
            
            label = tk.Label(frame_sub3, textvariable=self.setting_sE)
            label.grid(row=5, column=0, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s31)
            label.grid(row=5, column=1, padx=0, pady=2)
            self.eboxE1 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxE1.insert(0, yrange_SN[0])
            self.eboxE1.grid(row=5, column=2, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=5, column=3, padx=0, pady=2)
            self.eboxE2 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxE2.insert(0, yrange_SN[1])
            self.eboxE2.grid(row=5, column=4, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=5, column=5, padx=0, pady=2)
            self.eboxE3 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxE3.insert(0, yrange_SN[2])
            self.eboxE3.grid(row=5, column=6, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s36)
            label.grid(row=5, column=7, padx=0, pady=2)
            
            label = tk.Label(frame_sub3, textvariable=self.setting_sF)
            label.grid(row=6, column=0, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s31)
            label.grid(row=6, column=1, padx=0, pady=2)
            self.eboxF1 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxF1.insert(0, zrange_specFLAT[0])
            self.eboxF1.grid(row=6, column=2, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=6, column=3, padx=0, pady=2)
            self.eboxF2 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxF2.insert(0, zrange_specFLAT[1])
            self.eboxF2.grid(row=6, column=4, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=6, column=5, padx=0, pady=2)
            self.eboxF3 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxF3.insert(0, zrange_specFLAT[2])
            self.eboxF3.grid(row=6, column=6, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s36)
            label.grid(row=6, column=7, padx=0, pady=2)
            
            label = tk.Label(frame_sub3, textvariable=self.setting_sG)
            label.grid(row=7, column=0, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s31)
            label.grid(row=7, column=1, padx=0, pady=2)
            self.eboxG1 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxG1.insert(0, zrange_specA[0])
            self.eboxG1.grid(row=7, column=2, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=7, column=3, padx=0, pady=2)
            self.eboxG2 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxG2.insert(0, zrange_specA[1])
            self.eboxG2.grid(row=7, column=4, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=7, column=5, padx=0, pady=2)
            self.eboxG3 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxG3.insert(0, zrange_specA[2])
            self.eboxG3.grid(row=7, column=6, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s36)
            label.grid(row=7, column=7, padx=0, pady=2)
            
            label = tk.Label(frame_sub3, textvariable=self.setting_sH)
            label.grid(row=8, column=0, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s31)
            label.grid(row=8, column=1, padx=0, pady=2)
            self.eboxH1 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxH1.insert(0, zrange_specCORE[0])
            self.eboxH1.grid(row=8, column=2, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=8, column=3, padx=0, pady=2)
            self.eboxH2 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxH2.insert(0, zrange_specCORE[1])
            self.eboxH2.grid(row=8, column=4, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s35)
            label.grid(row=8, column=5, padx=0, pady=2)
            self.eboxH3 = tk.Entry(frame_sub3, width=5, relief=tk.SOLID)
            self.eboxH3.insert(0, zrange_specCORE[2])
            self.eboxH3.grid(row=8, column=6, padx=0, pady=2)
            label = tk.Label(frame_sub3, textvariable=self.setting_s36)
            label.grid(row=8, column=7, padx=0, pady=2)
            
            # =============================================================================
            #             フレームサブ5作成
            # =============================================================================
            frame_sub5 = tk.Frame(self.root_setting)
            frame_sub5.pack(padx=10, pady=5, side=tk.TOP, anchor="se")
            
            # OKボタンの作成
            self.btn_okey = ttk.Button(frame_sub5, text="OK", command=self.button_setting_okey)
            self.btn_okey.grid(row=0, column=0)
            # キャンセルボタンの作成
            self.btn_cancel = ttk.Button(frame_sub5, text="キャンセル", command=self.button_setting_cancel)
            self.btn_cancel.grid(row=0, column=1)
            
        # 何も選択していない状態で設定ボタンをクリックした場合
        except IndexError:
            pass
        return
    
    
    
    # =============================================================================
    #     デフォルト変更ボタンを押したときの処理
    # =============================================================================
    def button_setting_change(self):
        filetype = [("pickle files", "*.pickle")]
        idir = os.path.join("parameter", self.setting_mode)
        filepath_def = filedialog.askopenfilename(filetypes=filetype, 
                                                  title="wav追加時にデフォルトにしたいパラメータデータを選択してください",
                                                  multiple=False,
                                                  initialdir=idir)
        if filepath_def == "": #キャンセル時
            return
        filename_def = os.path.basename(filepath_def)
        filepath_txt = os.path.join("components", "Default.pickle")
        self.def_name[self.setting_mode+"_parameter"] = filename_def
        with open(filepath_txt, "wb") as f:
            pickle.dump(self.def_name, f)
        self.setting_s0.set('wav追加時パラメータ : "{}"'.format(os.path.splitext(self.def_name[self.setting_mode+"_parameter"])[0]))
        return
    
    
    
    # =============================================================================
    #     参照ボタンを押したときの処理
    # =============================================================================
    def button_setting_load(self):
        filetype = [("pickle files", "*.pickle")]
        idir = os.path.join("parameter", self.setting_mode)
        filepath_para = filedialog.askopenfilename(filetypes=filetype, 
                                                   title="参照したいパラメータデータを選択してください",
                                                   multiple=False,
                                                   initialdir=idir)
        if filepath_para == "": #キャンセル時
            return
        with open(filepath_para, "rb") as tf:
            parameter = pickle.load(tf)
        
        if self.setting_mode == "time":
            try:
                self.ebox21.delete(0, tk.END)
                self.ebox22.delete(0, tk.END)
                self.ebox23.delete(0, tk.END)
                self.ebox24.delete(0, tk.END)
                self.ebox25.delete(0, tk.END)
                self.ebox26.delete(0, tk.END)
                self.ebox21.insert(0, parameter["t_start"].hour)
                self.ebox22.insert(0, parameter["t_start"].minute)
                self.ebox23.insert(0, parameter["t_start"].second)
                self.ebox24.insert(0, parameter["t_end"].hour)
                self.ebox25.insert(0, parameter["t_end"].minute)
                self.ebox26.insert(0, parameter["t_end"].second)
            except:
                messagebox.showerror("エラー", "無効なパラメータデータです。", detail="以前のバージョンのパラメータセットデータは参照できません。")
                traceback.print_exc()
        
        elif self.setting_mode == "analyze":
            try:
                self.v10.set(parameter["amp_calib"])
                if parameter["A_analyze"] == "on":
                    self.chk11.set(True)
                else:
                    self.chk11.set(False)
                if parameter["Loudness_analyze"] == "on":
                    self.chk12.set(True)
                else:
                    self.chk12.set(False)
                if parameter["FFT_analyze"] == "on":
                    self.chk13.set(True)
                else:
                    self.chk13.set(False)
                if parameter["movie_post"] == "on":
                    self.chk14.set(True)
                else:
                    self.chk14.set(False)
                if parameter["freq_range"] == "ALL":
                    self.v41.set("ALL")
                    self.ebox41.delete(0, tk.END)
                    self.ebox42.delete(0, tk.END)
                    self.ebox41.insert(0, "--")
                    self.ebox42.insert(0, "--")
                    self.ebox41.config(state="disabled")
                    self.ebox42.config(state="disabled")
                else:
                    self.v41.set("カスタム")
                    self.ebox41.config(state="normal")
                    self.ebox42.config(state="normal")
                    self.ebox41.delete(0, tk.END)
                    self.ebox42.delete(0, tk.END)
                    self.ebox41.insert(0, parameter["freq_range"][0])
                    self.ebox42.insert(0, parameter["freq_range"][1])
            
            except:
                messagebox.showerror("エラー", "無効なパラメータデータです。", detail="以前のバージョンのパラメータセットデータは参照できません。")
                traceback.print_exc()
        
        elif self.setting_mode == "graph":
            try:
                self.A1.set(parameter["range_Hz"][0])
                self.A2.set(parameter["range_Hz"][1])
                self.eboxB1.delete(0, tk.END)
                self.eboxB2.delete(0, tk.END)
                self.eboxB3.delete(0, tk.END)
                self.eboxC1.delete(0, tk.END)
                self.eboxC2.delete(0, tk.END)
                self.eboxC3.delete(0, tk.END)
                self.eboxD1.delete(0, tk.END)
                self.eboxD2.delete(0, tk.END)
                self.eboxD3.delete(0, tk.END)
                self.eboxE1.delete(0, tk.END)
                self.eboxE2.delete(0, tk.END)
                self.eboxE3.delete(0, tk.END)
                self.eboxF1.delete(0, tk.END)
                self.eboxF2.delete(0, tk.END)
                self.eboxF3.delete(0, tk.END)
                self.eboxG1.delete(0, tk.END)
                self.eboxG2.delete(0, tk.END)
                self.eboxG3.delete(0, tk.END)
                self.eboxH1.delete(0, tk.END)
                self.eboxH2.delete(0, tk.END)
                self.eboxH3.delete(0, tk.END)
                self.eboxB1.insert(0, parameter["yrange_FFT(FLAT)"][0])
                self.eboxB2.insert(0, parameter["yrange_FFT(FLAT)"][1])
                self.eboxB3.insert(0, parameter["yrange_FFT(FLAT)"][2])
                self.eboxC1.insert(0, parameter["yrange_FFT(A)"][0])
                self.eboxC2.insert(0, parameter["yrange_FFT(A)"][1])
                self.eboxC3.insert(0, parameter["yrange_FFT(A)"][2])
                self.eboxD1.insert(0, parameter["yrange_OA"][0])
                self.eboxD2.insert(0, parameter["yrange_OA"][1])
                self.eboxD3.insert(0, parameter["yrange_OA"][2])
                self.eboxE1.insert(0, parameter["yrange_SN"][0])
                self.eboxE2.insert(0, parameter["yrange_SN"][1])
                self.eboxE3.insert(0, parameter["yrange_SN"][2])
                self.eboxF1.insert(0, parameter["zrange_spec(FLAT)"][0])
                self.eboxF2.insert(0, parameter["zrange_spec(FLAT)"][1])
                self.eboxF3.insert(0, parameter["zrange_spec(FLAT)"][2])
                self.eboxG1.insert(0, parameter["zrange_spec(A)"][0])
                self.eboxG2.insert(0, parameter["zrange_spec(A)"][1])
                self.eboxG3.insert(0, parameter["zrange_spec(A)"][2])
                self.eboxH1.insert(0, parameter["zrange_spec(CORE)"][0])
                self.eboxH2.insert(0, parameter["zrange_spec(CORE)"][1])
                self.eboxH3.insert(0, parameter["zrange_spec(CORE)"][2])
                
            except:
                messagebox.showerror("エラー", "無効なパラメータデータです。", detail="以前のバージョンのパラメータセットデータは参照できません。")
                traceback.print_exc()
                    
        return
    
    
    
    # =============================================================================
    #     保存ボタンを押したときの処理
    # =============================================================================
    def button_setting_save(self):
        filetype = [("pickle files", "*.pickle")]
        idir = os.path.join("parameter", self.setting_mode)
        filepath_para = filedialog.asksaveasfilename(filetypes=filetype, 
                                                     title="保存するファイル名を指定してください",
                                                     initialdir=idir)
        if filepath_para == "": #キャンセル時
            return
        elif os.path.splitext(filepath_para)[-1] != ".pickle":
            filepath_para = filepath_para + ".pickle"
        
        
        if self.setting_mode == "time":
            try:
                parameter = {"t_start" : datetime.time(int(self.ebox21.get()), int(self.ebox22.get()), int(self.ebox23.get()), 0),
                             "t_end"   : datetime.time(int(self.ebox24.get()), int(self.ebox25.get()), int(self.ebox26.get()), 0)}
            except:
                messagebox.showerror("エラー", "入力値が不適切です。", detail="訂正して下さい。")
                traceback.print_exc()
                return    
            
        elif self.setting_mode == "analyze":
            try:
                parameter = {"amp_calib" : self.v10.get()}
                if self.chk11.get():
                    parameter["A_analyze"] = "on"
                else:
                    parameter["A_analyze"] = "-"
                if self.chk12.get():
                    parameter["Loudness_analyze"] = "on"
                else:
                    parameter["Loudness_analyze"] = "-"
                if self.chk13.get():
                    parameter["FFT_analyze"] = "on"
                else:
                    parameter["FFT_analyze"] = "-"
                if self.chk14.get():
                    parameter["movie_post"] = "on"
                else:
                    parameter["movie_post"] = "-"
                if self.v41.get() == "ALL":
                    parameter["freq_range"] = "ALL"
                else:
                    parameter["freq_range"] = [int(self.ebox41.get()), int(self.ebox42.get())]
            except:
                messagebox.showerror("エラー", "入力値が不適切です。", detail="訂正して下さい。")
                traceback.print_exc()
                return
        
        elif self.setting_mode == "graph":
            try:
                parameter = {"range_Hz"        : [int(self.A1.get()), int(self.A2.get())],
                             "yrange_FFT(FLAT)"  : [float(self.eboxB1.get()), float(self.eboxB2.get()), float(self.eboxB3.get())],
                             "yrange_FFT(A)"     : [float(self.eboxC1.get()), float(self.eboxC2.get()), float(self.eboxC3.get())],
                             "yrange_OA"         : [float(self.eboxD1.get()), float(self.eboxD2.get()), float(self.eboxD3.get())],
                             "yrange_SN"         : [float(self.eboxE1.get()), float(self.eboxE2.get()), float(self.eboxE3.get())],
                             "zrange_spec(FLAT)" : [float(self.eboxF1.get()), float(self.eboxF2.get()), float(self.eboxF3.get())],
                             "zrange_spec(A)"    : [float(self.eboxG1.get()), float(self.eboxG2.get()), float(self.eboxG3.get())],
                             "zrange_spec(CORE)" : [float(self.eboxH1.get()), float(self.eboxH2.get()), float(self.eboxH3.get())]}
            except:
                messagebox.showerror("エラー", "入力値が不適切です。", detail="訂正して下さい。")
                traceback.print_exc()
                return
        
        with open(filepath_para, "wb") as tf:
            pickle.dump(parameter, tf)
        
        return
    
    
    
    # =============================================================================
    #     OKボタンを押したときの処理
    # =============================================================================
    def button_setting_okey(self):
        
        if self.setting_mode == "time":
            try:
                t_start_edit = datetime.time(int(self.ebox21.get()), int(self.ebox22.get()), int(self.ebox23.get()), 0)
                t_end_edit = datetime.time(int(self.ebox24.get()), int(self.ebox25.get()), int(self.ebox26.get()), 0)
            except:
                messagebox.showerror("エラー", "時間範囲項目に文字列が入力されています。", detail="時間範囲項目には整数を入力してください。")
                return
            for i, job_number in enumerate(self.job_number_selected_list):
                self.job_list[job_number-1]["t_start"] = t_start_edit
                self.job_list[job_number-1]["t_end"] = t_end_edit
                self.tree.set(self.job_selected_ID[i], 4, f"{t_start_edit}~{t_end_edit}")
        
        
        elif self.setting_mode == "analyze":
            try:
                amp_calib_edit = self.v10.get()
                if self.chk11.get():
                    A_analyze_edit = "on"
                else:
                    A_analyze_edit = "-"
                if self.chk12.get():
                    Loudness_analyze_edit = "on"
                else:
                    Loudness_analyze_edit = "-"
                if self.chk13.get():
                    FFT_analyze_edit = "on"
                else:
                    FFT_analyze_edit = "-"
                if self.chk14.get():
                    movie_post_edit = "on"
                else:
                    movie_post_edit = "-"
                freq_range_edit = self.v41.get()
                if freq_range_edit != "ALL":
                    if int(self.ebox41.get()) < int(self.ebox42.get()):
                        freq_range_edit = [int(self.ebox41.get()), int(self.ebox42.get())]
                    else:
                        messagebox.showerror("エラー", "周波数範囲項目にご入力があります。", detail="最大値と最小値が逆転していないか確認してください。")
                        return
            except:
                messagebox.showerror("エラー", "入力値に文字列が入力されています。", detail="入力値は整数もしくは少数しか認識されません。訂正してください。")
                return
            
            for i, job_number in enumerate(self.job_number_selected_list):
                self.job_list[job_number-1]["amp_calib"] = amp_calib_edit
                self.job_list[job_number-1]["A_analyze"] = A_analyze_edit
                self.job_list[job_number-1]["Loudness_analyze"] = Loudness_analyze_edit
                self.job_list[job_number-1]["FFT_analyze"] = FFT_analyze_edit
                self.job_list[job_number-1]["movie_post"] = movie_post_edit
                self.job_list[job_number-1]["freq_range"] = freq_range_edit
                self.tree.set(self.job_selected_ID[i], 5, amp_calib_edit)
                self.tree.set(self.job_selected_ID[i], 6, A_analyze_edit)
                self.tree.set(self.job_selected_ID[i], 7, Loudness_analyze_edit)
                self.tree.set(self.job_selected_ID[i], 8, FFT_analyze_edit)
                self.tree.set(self.job_selected_ID[i], 9, movie_post_edit)
                if freq_range_edit == "ALL":
                    self.tree.set(self.job_selected_ID[i], 10, "ALL")
                else:
                    self.tree.set(self.job_selected_ID[i], 10, f"{freq_range_edit[0]}Hz~{freq_range_edit[1]}Hz")
        
        
        elif self.setting_mode == "graph":
            if int(self.A1.get()) < int(self.A2.get()):
                range_Hz_edit = [int(self.A1.get()), int(self.A2.get())]
            else:
                messagebox.showerror("エラー", "FFT X軸[Hz]目盛項目にご入力があります。", detail="目盛最大値と目盛最小値が逆転していないか確認してください。")
                return
            
            try:
                yrange_FFT_FLAT_edit = [float(self.eboxB1.get()), float(self.eboxB2.get()), float(self.eboxB3.get())]
                yrange_FFT_A_edit = [float(self.eboxC1.get()), float(self.eboxC2.get()), float(self.eboxC3.get())]
                yrange_OA_edit = [float(self.eboxD1.get()), float(self.eboxD2.get()), float(self.eboxD3.get())]
                yrange_SN_edit = [float(self.eboxE1.get()), float(self.eboxE2.get()), float(self.eboxE3.get())]
                zrange_specFLAT_edit = [float(self.eboxF1.get()), float(self.eboxF2.get()), float(self.eboxF3.get())]
                zrange_specA_edit = [float(self.eboxG1.get()), float(self.eboxG2.get()), float(self.eboxG3.get())]
                zrange_specCORE_edit = [float(self.eboxH1.get()), float(self.eboxH2.get()), float(self.eboxH3.get())]
            except:
                messagebox.showerror("エラー", "入力値に文字列が入力されています。", detail="入力値は整数もしくは少数しか認識されません。訂正してください。")
                return
            
            for i, job_number in enumerate(self.job_number_selected_list):
                self.job_list[job_number-1]["range_Hz"] = range_Hz_edit
                self.job_list[job_number-1]["yrange_FFT_FLAT"] = yrange_FFT_FLAT_edit
                self.job_list[job_number-1]["yrange_FFT_A"] = yrange_FFT_A_edit
                self.job_list[job_number-1]["yrange_OA"] = yrange_OA_edit
                self.job_list[job_number-1]["yrange_SN"] = yrange_SN_edit
                self.job_list[job_number-1]["zrange_specFLAT"] = zrange_specFLAT_edit
                self.job_list[job_number-1]["zrange_specA"] = zrange_specA_edit
                self.job_list[job_number-1]["zrange_specCORE"] = zrange_specCORE_edit
                self.tree.set(self.job_selected_ID[i], 11, f"{range_Hz_edit[0]}Hz~{range_Hz_edit[1]}Hz")
                self.tree.set(self.job_selected_ID[i], 12, f"{yrange_FFT_FLAT_edit}")
                self.tree.set(self.job_selected_ID[i], 13, f"{yrange_FFT_A_edit}")
                self.tree.set(self.job_selected_ID[i], 14, f"{yrange_OA_edit}")
                self.tree.set(self.job_selected_ID[i], 15, f"{yrange_SN_edit}")
                self.tree.set(self.job_selected_ID[i], 16, f"{zrange_specFLAT_edit}")
                self.tree.set(self.job_selected_ID[i], 17, f"{zrange_specA_edit}")
                self.tree.set(self.job_selected_ID[i], 18, f"{zrange_specCORE_edit}")
        
        self.root_setting.destroy()
        self.root_setting.grab_release()
        return
    
    
    
    # =============================================================================
    #     キャンセルボタンを押したときの処理
    # =============================================================================
    def button_setting_cancel(self):
        self.root_setting.destroy()
        return
    
    
    
    # =============================================================================
    #     中止ボタンを押したときの処理
    # =============================================================================
    def button_stop(self):
        rsp = tk.messagebox.askyesno("確認", "解析プロセスを中断します", detail="本当によろしいですか？")
        if rsp:
            # スレッドの停止
            self.started.clear()
            self.tree.set(self.record, 2, "中断しています")
            self.s1.set("解析プロセスを中断しています。しばらくお待ちください。")
            # ウィンドウの更新
            self.btn_stop["state"] = "disable"
        else:
            pass
        return
    
    
    
    # =============================================================================
    #     中止完了時のGUI更新処理
    # =============================================================================
    def display_stop(self):
        # ウィンドウの更新
        self.tree.set(self.record, 2, "中断されました")
        self.s1.set("解析プロセスは正常に中断されました。結果ボタンから出力データを確認してください。また、終了する場合は終了ボタンを、新しく解析を始めたい場合はリセットボタンを押してください。")
        self.btn_reset["state"] = "able"
        # フレーム5再作成
        self.frame5.destroy()
        self.frame5 = tk.Frame(self.master)
        self.frame5.pack(side=tk.RIGHT, anchor="se", expand=0, fill=tk.X)
        #　終了ボタンの作成
        self.btn_end = ttk.Button(self.frame5, text="終了", command=self.button_end)
        self.btn_end.pack(side=tk.RIGHT, padx=10, pady=10, anchor="sw")
        #　結果ボタンの作成
        self.btn_result = ttk.Button(self.frame5, text="結果", command=self.button_result)
        self.btn_result.pack(side=tk.RIGHT, padx=10, pady=10, anchor="sw")
        
        # スレッドを待機
        self.started.wait()
        return
    
    
    
    # =============================================================================
    #     解析完了時のGUI更新処理
    # =============================================================================
    def display_finish(self):
        # ウィンドウの更新
        self.s1.set("解析がすべて完了しました。結果ボタンから出力データを確認してください。また、終了する場合は終了ボタンを、新しく解析を始めたい場合はリセットボタンを押してください。")
        self.btn_reset["state"] = "able"
        # フレーム5再作成
        self.frame5.destroy()
        self.frame5 = tk.Frame(self.master)
        self.frame5.pack(side=tk.RIGHT, anchor="se", expand=0, fill=tk.X)
        #　終了ボタンの作成
        self.btn_end = ttk.Button(self.frame5, text="終了", command=self.button_end)
        self.btn_end.pack(side=tk.RIGHT, padx=10, pady=10, anchor="sw")
        #　結果ボタンの作成
        self.btn_result = ttk.Button(self.frame5, text="結果", command=self.button_result)
        self.btn_result.pack(side=tk.RIGHT, padx=10, pady=10, anchor="sw")
        return
    
    
    
    # =============================================================================
    #     結果ボタンを押したときの処理
    # =============================================================================
    def button_result(self):
        sp.Popen(["explorer", self.folder_output], shell=False)
        return
    
    
    
    # =============================================================================
    #     終了ボタンを押したときの処理
    # =============================================================================
    def button_end(self):
        self.master.destroy()
        return
    
    
    
    # =============================================================================
    #     解析ボタンを押したときの処理
    # =============================================================================
    def button_analyze(self):
        #ジョブが一つも定義されていない場合はスキップする
        if len(self.tree.get_children()) == 0:
            return
        
        for job_number in range(1, len(self.tree.get_children())+1, 1):
            job = self.job_list[job_number-1]
            t_start = job["t_start"]
            t_start_sec = t_start.hour*3600+t_start.minute*60+t_start.second
            t_end = job["t_end"]
            t_end_sec = t_end.hour*3600+t_end.minute*60+t_end.second
            t_length = t_end_sec - t_start_sec
            if t_length > 60 and job["FFT_analyze"] == "on":
                rsp = tk.messagebox.askyesno("確認", "1分間以上の長時間範囲でFFT出力がonになっているジョブがあります",
                                             detail="この場合、解析に長時間を要します。このまま続行しますか？")
                if rsp:
                    break
                else:
                    return
            
        # マルチスレッドの定義＆定義したスレッドを動かす
        if __name__ != "__main__":
            self.started = threading.Event()
            self.threading_sub1 = threading.Thread(target=self.MainFunc, daemon=True)
            self.threading_sub1.start()
            self.started.set()
        
        # ウィンドウの更新
        self.s1.set("解析中です．．．")
        self.btn_add["state"] = "disable"
        self.btn_reset["state"] = "disable"
        self.btn_remove["state"] = "disable"
        self.btn_duplicate["state"] = "disable"
        self.btn_setting_analyze["state"] = "disable"
        self.btn_setting_time["state"] = "disable"
        self.btn_setting_graph["state"] = "disable"
        # フレーム5再作成
        self.frame5.destroy()
        self.frame5 = tk.Frame(self.master)
        self.frame5.pack(side=tk.RIGHT, anchor="se", expand=0, fill=tk.X)
        #　中止ボタンの作成
        self.btn_stop = ttk.Button(self.frame5, text="中止", command=self.button_stop)
        self.btn_stop.pack(side=tk.RIGHT, padx=10, pady=10, anchor="sw")
        #　結果ボタンの作成
        self.btn_result = ttk.Button(self.frame5, text="結果", command=self.button_result)
        self.btn_result.pack(side=tk.RIGHT, padx=10, pady=10, anchor="sw")
        self.btn_result["state"] = "disable"
        
        if __name__ == "__main__":
            self.display_finish()
        return
    
    

# =============================================================================
#### メイン実行時の処理
# =============================================================================
if __name__ == "__main__":
    version = "0.7"
    print(f"SoundAnalyzer (Version {version}) 起動中...")
    
    root = tk.Tk()
    app = GUI(version, master=root)
    app.mainloop()
    job_list = app.job_list