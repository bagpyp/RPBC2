# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:29:51 2020

@author: Bagpyp
"""

from receipts import *
from out import *
from api import *
from media import *
from maps import *
from payloads import *


#%% 
from datetime import datetime as dt

def log(text, stamp=False, base='log'):
    with open(f"logs/{base} {dt.now().strftime('%d-%m-%Y')}.txt", 'a') as file:
        if stamp:
            file.write(f"\n\n\n{dt.now().strftime('%H:%M:%S')}\n\n")
        file.write(text)
        file.write('\n')   