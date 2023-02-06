# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 17:36:31 2022

@author: Ryusei
"""

import sys
import datetime

def calc_t_tick(t_start, t_end):
    """
    Parameters
    ----------
    t_start : datetime
        the time in start point
    t_end : datetime
        the time in end point

    Returns
    -------
    sec_start : integer
        time[sec] in start point
    sec_end : integer
        time[sec] in end point
    t_tick : integer
        the tick of time axis
    dec : integer
        decimation value for plot time reducing
    """
    
    # t_start, t_endがdatetime型でなかった場合に、エラー表示
    if type(t_start) != datetime.time or type(t_end) != datetime.time:
        raise ValueError("the data types of t_start and t_end as input argument must be datetime.time")
        sys.exit()
    
    td_start = datetime.timedelta(hours=t_start.hour, minutes=t_start.minute, seconds=t_start.second)
    #td_start = datetime.timedelta(hours=t_start.hour, minutes=t_start.minute, seconds=t_start.second, milliseconds=t_start.microsecond*1e-3)
    td_end = datetime.timedelta(hours=t_end.hour, minutes=t_end.minute, seconds=t_end.second)
    #td_end = datetime.timedelta(hours=t_end.hour, minutes=t_end.minute, seconds=t_end.second, milliseconds=t_end.microsecond*1e-3)
    sec_start = td_start.total_seconds()
    sec_end = td_end.total_seconds()
    t_length = sec_end - sec_start
    if t_length < 10: #(0 < t_length <10) [sec]
        t_tick = 1
        dec = 10 #dt=5e-4*dec = 0.005sec
        
    elif t_length < 30: #(10 <= t_length < 30) [sec]
        t_tick = 2
        dec = 20 #dt=5e-4*dec = 0.01sec ex)10sec:1000plot
    
    elif t_length < 60: #(30 <= t_length < 60) [sec]
        t_tick = 5
        dec = 50 #dt=5e-4*dec = 0.025sec ex)30sec:1200plot
    
    elif t_length < 180: #(60 <= t_length < 180) [sec]
        t_tick = 10
        dec = 100 #dt=5e-4*dec = 0.05sec ex)60sec:1200plot
    
    elif t_length < 300: #(180 <= t_length < 300) [sec]
        t_tick = 20
        dec = 300 #dt=5e-4*dec = 0.15sec ex)180sec:1200plot
    
    elif t_length < 540: #(300 <= t_length < 540) [sec]
        t_tick = 30
        dec = 500 #dt=5e-4*dec = 0.25sec ex)300sec:1200plot
    
    elif t_length < 1080: #(540 <= t_length < 1080) [sec]
        t_tick = 60
        dec = 900 #dt=5e-4*dec = 0.45sec ex)540sec:1200plot
    
    elif t_length < 2160: #(1080 <= t_length < 2160) [sec]
        t_tick = 120
        dec = 1800 #dt=5e-4*dec = 0.9sec ex)1080sec:1200plot
    
    elif t_length < 2880: #(2160 <= t_length < 2880) [sec]
        t_tick = 300
        dec = 3600 #dt=5e-4*dec = 1.8sec ex)2160sec:1200plot
    
    elif t_length < 3600: #(2880 <= t_length < 3600) [sec]
        t_tick = 300
        dec = 4800 #dt=5e-4*dec = 2.4sec ex)2880sec:1200plot
    
    elif t_length < 6000: #(3600 <= t_length < 6000) [sec]
        t_tick = 300
        dec = 6000 #dt=5e-4*dec = 3.0sec ex)3600sec:1200plot
    
    elif t_length < 12000: #(6000 <= t_length < 12000) [sec]
        t_tick = 600
        dec = 10000 #dt=5e-4*dec = 5.0sec ex)6000sec:1200plot
    
    elif t_length >= 12000:
        print("時間範囲が180分以上のため、時間軸目盛が見えづらくなる可能性があります。")
        t_tick = 1200
        dec = 20000 #dt=5e-4*dec = 10.0sec ex)12000sec:1200plot
        
    return sec_start, sec_end, t_tick, dec



def convert_time(time_sec):
    """
    Parameters
    ----------
    time_sec : integer
        total seconds
        ex) 123s, 1200s

    Returns
    -------
    time_object : time object
        --
    time_delta : timedelta
        timedelta object to check the time of hour, minute, second at the same time
        ex) 00:00:10, 01:30:25
    """
    
    hour = int(time_sec//3600)
    time_rem = time_sec % 3600
    minute = int(time_rem//60)
    time_rem = time_rem % 60
    second = int(time_rem)
    time_object = datetime.time(hour, minute, second)
    time_delta = datetime.timedelta(hours=time_object.hour, minutes=time_object.minute, seconds=time_object.second)
    
    return time_object, time_delta



def convert_time_micro(time_sec):
    """
    Parameters
    ----------
    time_sec : integer
        total seconds
        ex) 123s, 1200s

    Returns
    -------
    time_object : time object
        --
    time_delta : timedelta
        timedelta object to check the time of hour, minute, second, microsecond at the same time
        ex) 00:00:10:00, 01:30:25:00
    """
    
    hour = int(time_sec//3600)
    time_rem = round(time_sec % 3600, 1)
    minute = int(time_rem//60)
    time_rem = round(time_rem % 60, 1)
    second = int(time_rem)
    microsecond = int(round(time_rem-second, 1)*1e3)
    time_object = datetime.time(hour, minute, second, microsecond)
    time_delta = datetime.timedelta(hours=time_object.hour, minutes=time_object.minute, seconds=time_object.second, milliseconds=time_object.microsecond)
    
    return time_object, time_delta



if __name__ == "__main__":
    t_start = datetime.time(0, 0, 30, 0)
    t_end = datetime.time(0, 20, 30, 0)
    sec_start, sec_end, t_tick, dec = calc_t_tick(t_start, t_end)
    
    time_sec = 40.3
    time_delta = convert_time_micro(time_sec)
    print(str(time_delta))
    print(str(time_delta)[:10])