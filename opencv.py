# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 23:40:57 2022

@author: Ryusei
"""

import os
import numpy as np
import cv2

def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None



def imwrite(filename, img, params=None):
    try:
        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(filename, mode='w+b') as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False




if __name__ == "__main__":
    filepath = r"C:\Users\Ryusei\OneDrive - Kyushu University\デスクトップ\20220303_セレクトプラン申請\マウス領収書.png"
    img = imread(filepath)
    filepath2 = r"C:\Users\Ryusei\OneDrive - Kyushu University\デスクトップ\20220303_セレクトプラン申請\マウス領収書2.png"
    imwrite(filepath2, img)