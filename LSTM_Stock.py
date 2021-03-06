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

def LSTM_Stock(buy_list):
    # 1000일치 데이터 학습
    Num = 1000
    plt.figure(figsize=(10, 10))
    lenth = len(buy_list)

    for code in buy_list:
        # SQLite3를 이용해 해당 코드 종목 가격 데이터 로드
        try:
            con = sqlite3.connect("종목별_가격정보.db")
            data = pd.read_sql(f"SELECT * FROM '{code}' order by date LIMIT {Num}", con)
            con.close()
        except:
            continue

        # 당일 고가와 저가 사이의 중간 값을 추정
        midPrice = (data['High'].values + data['Low'].values) / 2


        # 학습할 윈도우 사이즈 지정
        winSize = 30
        winLen = winSize + 1
        
        result = []
        for i in range(len(midPrice) - winLen):
            result.append(midPrice[i: i+winLen])

        # 윈도우 데이터 정규화
        normlData = []
        for window in result:
            if(window[0]==0):
                pass
            else:    
                normlWindow = [((float(w) / float(window[0])) - 1) for w in window]
                normlData.append(normlWindow)

        result = np.array(normlData)

        # Train Set과 Test Set으로 분리
        row = int(round(result.shape[0] * 0.9))
        train = result[:row, :]
        np.random.shuffle(train)

        x_train = train[:, :-1]
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
        y_train = train[:, -1]

        x_test = result[row:, :-1]
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        y_test = result[row:, -1]

        # LSTM 모델 설계
        model = Sequential()
        model.add(LSTM(30, return_sequences=True, input_shape=(30, 1)))
        model.add(Dropout(0.2))
        model.add(LSTM(100, return_sequences=False))
        model.add(Dropout(0.2))
        # model.add(LSTM(64, return_sequences=False))
        model.add(Dense(1, activation='linear'))
        model.compile(loss='mse', optimizer='rmsprop')
        model.summary()

        # Training 을 실행하는 부분
        model.fit(x_train, y_train, validation_data=(x_test, y_test), batch_size=10, epochs=20)
        prdcData = model.predict(x_test)
        # 예측치와 실제 값 편차 계산
        deviation = prdcData.flatten() - y_test.flatten()
        devMean = deviation.mean()

        # 결과 데이터를 나타내기 위한 코드
        plt.subplot(int('32'+str(buy_list.index(code)+1)))
        # plt.subplot(int(str(round(lenth/2)+'1'+str(buy_list.index(code)+1)))
        plt.plot(y_test, label='Real Data')
        plt.plot(prdcData, label='Prediction Data')
        plt.plot(prdcData.flatten() - y_test.flatten(), label='Deviation')
        plt.title(str(code) + ", Mean of Deviation : " + str(round(float(devMean), 3)))
        plt.grid()
        plt.legend()
    plt.savefig('result.png')
    plt.show()


if __name__ == "__main__":
    LSTM_Stock(["005930", "007120"])