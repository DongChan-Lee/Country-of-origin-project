# title: Convolutional Neural Network (CNN)
# author: Lee Dong Chan, Lee Sun Yeop

# <목차>
# 1. 라이브러리 임포트
# 2. 데이터 로드
# 3. 전체데이터를 트레이닝셋, 테스트셋으로 분리
# 4. 모델 빌딩
# 5. 모델 설정
# 6. 모델 피팅
# 7. 모델 평가

# 1. 라이브러리 임포트
import numpy as np
import pandas as pd
import pickle
import os
import glob
from random import shuffle

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

import sklearn
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.pipeline import Pipeline
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import MinMaxScaler, StandardScaler

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import initializers
from tensorflow.keras.models import Sequential, model_from_json
from tensorflow.keras.layers import Dense, Flatten, Dropout, Activation, Conv1D, \
    GlobalMaxPool1D, MaxPool1D, AvgPool1D, Masking
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.wrappers.scikit_learn import KerasRegressor
from tensorflow.keras.utils import normalize, to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import BatchNormalization

# 디렉토리 설정
os.chdir(r"C:\Users\PC\Desktop\제출용\데이터") # 데이터 폴더로 디렉토리 설정

# 2. 데이터 로드
cnndata_x = np.load('Deep_input_X_scaled_36.npy')
cnndata_y = np.load('Deep_input_Y_MSE_scaled.npy') # continuous
# cnndata_y = np.load('Deep_input_Y_binary.npy') # binary

x = cnndata_x
y = cnndata_y

# 3. 전체데이터를 트레이닝셋, 테스트셋으로 분리
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=True)
# x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.2, shuffle=True)
print(x_train.shape, y_train.shape, 'train examples')
# print(x_val.shape, y_val.shape, 'validation examples')
print(x_test.shape, y_test.shape, 'test examples')

# 하이퍼파라미터 설정
l2 = tf.keras.regularizers.l2(0.005)
n_features = x.shape[2]

# 4. 모델 빌딩
model = Sequential()
## convolutional layer
model.add(Masking(mask_value=-1, input_shape=(108, n_features))) # subsequent layers must be able to take masking function
model.add(Conv1D(filters=20, kernel_size=3, padding='valid', strides=1, input_shape=(108, n_features),
                 kernel_regularizer=None))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPool1D())
model.add(Conv1D(filters=20, kernel_size=3, padding='valid', strides=1,
                 kernel_regularizer=None))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(GlobalMaxPool1D())
## dense layer
# model.add(Flatten())
model.add(Dense(16, activation='relu'))
model.add(Dropout(0.2))
## output layer
model.add(Dense(units=1, activation='linear'))    # continuous
# model.add(Dense(units=1, activation='sigmoid')) # binary

model.summary()

# 5. 모델 설정
rmse = tf.keras.metrics.RootMeanSquaredError()
# binary = tf.keras.losses.BinaryCrossentropy(reduction='sum_over_batch_size')
opt = tf.keras.optimizers.Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-07,
                               amsgrad=False, name="Adam")
model.compile(loss='mse', optimizer=opt, metrics=[rmse])
# model.compile(loss=binary, optimizer=opt, metrics=['acc'])

# 6. 모델 피팅
model_path = 'C:/Users/PC/Desktop/제출용/데이터'
model_name = 'CNN_test_model.h5'
model_location = os.path.join(model_path, model_name)
early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=10,
                                                  mode='min', restore_best_weights=False)
model_checkpoint = tf.keras.callbacks.ModelCheckpoint(filepath=model_location, monitor='val_loss', save_best_only=True)
callbacks_list = [early_stop, model_checkpoint]

history = model.fit(x_train, y_train, batch_size=128, epochs=1, validation_split=0.2, verbose=2,
                    callbacks=callbacks_list) # 실제로는 에포크를 100으로 설정한다.

# 7. 모델 평가
saved_model = load_model('CNN-cont-first-9-1-2020.h5')
train_metrics = saved_model.evaluate(x_train, y_train, verbose=0)
test_metrics = saved_model.evaluate(x_test, y_test, verbose=0)
print('Train: %.3f, Test: %.3f' % (train_metrics[1], test_metrics[1]))