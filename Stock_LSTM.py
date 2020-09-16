import pandas as pd
import numpy as np
import requests, sqlite3
import pandas as D_FMT
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import LSTM, Dropout, Dense, Activation
# from keras.callbacks import TensorBoard, ModelCheckpoint, ReduceLROnPlateau
import datetime
from sklearn.preprocessing import MinMaxScaler

def LSTM_Stock(code):
    # 1000일치 데이터 학습
    Num = 1000
    
    con = sqlite3.connect("종목별_가격정보.db")
    data = pd.read_sql(f"SELECT * FROM '{code}' order by date LIMIT {Num}", con)
    con.close()

    high_prices = data['High'].values
    low_prices = data['Low'].values
    mid_prices = (high_prices + low_prices) / 2

    # Window Size
    seq_len = 30
    sequence_length = seq_len + 1

    result = []
    for index in range(len(mid_prices) - sequence_length):
        result.append(mid_prices[index: index + sequence_length])

    normalized_data = []
    for window in result:
        normalized_window = [((float(p) / float(window[0])) - 1) for p in window]
        normalized_data.append(normalized_window)

    result = np.array(normalized_data)

    # split train and test data
    row = int(round(result.shape[0] * 0.9))
    train = result[:row, :]
    np.random.shuffle(train)

    x_train = train[:, :-1]
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    y_train = train[:, -1]

    x_test = result[row:, :-1]
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    y_test = result[row:, -1]

    model = Sequential()

    model.add(LSTM(30, return_sequences=True, input_shape=(30, 1)))

    model.add(LSTM(64, return_sequences=False))

    model.add(Dense(1, activation='linear'))

    model.compile(loss='mse', optimizer='rmsprop')

    model.summary()

    model.fit(x_train, y_train,
    validation_data=(x_test, y_test),
    batch_size=10,
    epochs=20)

    pred = model.predict(x_test)

    fig = plt.figure(facecolor='white', figsize=(20, 10))
    ax = fig.add_subplot(111)
    ax.plot(y_test, label='Real Data')
    ax.plot(pred, label='Prediction Data')
    ax.legend()
    ax.set_title(code)
    plt.show()


if __name__ == "__main__":
    print(LSTM_Stock("005930"))
