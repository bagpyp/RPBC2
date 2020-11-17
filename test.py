# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 16:17:13 2020

@author: Web
"""

import pandas as pd
pd.options.display.max_rows = 150
pd.options.display.max_columns = 50
pd.options.display.width = 180
pd.options.display.max_colwidth = 30

p = pd.read_pickle('products.pkl')
co = p[(p.v_upc.duplicated(keep=False))&(p.v_upc!='')]\
    .groupby('v_upc')
    
for i,g in co:
    print(g)
    break

