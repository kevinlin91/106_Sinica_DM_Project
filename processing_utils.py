#!/usr/bin/env python

import pandas as pd
import numpy as np

from sklearn import preprocessing

#
# Util functions expects pandas dataframes
# 

def log_data(data, columns):
    def signed_log(x):
        if abs(x) < 1:
            return 0
        else:
            return np.log10(x)

    for col in columns:
        data[col] = data.loc[:,col].apply(signed_log)

    return data

def normalize_data(data):
    # Divide into numerical and non-numerical features
    num_data = data.select_dtypes(include=[np.number])
    data = data.drop(data.select_dtypes(include=[np.number]), axis=1)

    # Normalize numerical features with Sklearn MinMax
    min_max_scaler = preprocessing.MinMaxScaler()
    norm_data = pd.DataFrame(min_max_scaler.fit_transform(num_data), columns = num_data.columns)

    # Re-add non numerical features
    norm_data[data.columns] = data
    return norm_data
