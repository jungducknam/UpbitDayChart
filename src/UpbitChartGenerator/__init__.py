import time
import pyupbit
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

class UpbitChartGenerator:
    def __init__(self, fiat='KRW', days='day', count=1):
        self.fiat = fiat
        self.days = days
        self.count = count
        self.df = pd.DataFrame()
        #데이터프레임 포맷지정
        pd.set_option('display.float_format', '{:.2f}'.format)


    def setDfData(self):
        df = self.df
        #초기화에서 지정한대로 코인의 목록을 가져옴
        tickers = pyupbit.get_tickers(self.fiat)
        #코인의 목록을 5개씩 나눠 요청을 하며, 5개씩 요청을 던진 후에는 0.5초씩 쉰다. (API정책 때문)
        for i in range(0, len(tickers), 5):
            tickList = tickers[i:i + 5]
            for coin in tickList:
                #코인 심볼명으로 기간 값 받아오기 (기본옵션 : 일봉, 갯수 : 1개)
                temp = pyupbit.get_ohlcv(coin, self.days, count=self.count)
                temp = temp.drop(columns=['volume', 'value'])  # 필요없는 컬럼 삭제
                # 코인심볼 넣고 맨앞으로 오게 설정
                temp['coinName'] = coin.replace('KRW-', '')
                cols = ['coinName'] + [col for col in temp.columns if col != 'coinName']
                temp = temp[cols]
                #큰 데이터 프레임에 삽입
                df = pd.concat([df, temp], ignore_index=True);
            time.sleep(0.5)
        #가격 변동률 계산
        df['change'] = ((df['close'] - df['open']) / df['open']) * 100
        #정렬
        self.df = df.sort_values(by='change', ascending=True).reset_index(drop=True)
        return self

    def getChartImg(self):
        #데이터 프레임 들고와
        df = self.df
        # A4 크기에 가까운 비율과 DPI 설정
        fig_height = len(df) * 0.1
        dims = (8.27, fig_height)  # A4 용지 크기 (인치 단위)

        # 그래프를 그릴 준비, A4 용지 비율을 유지
        fig, ax = plt.subplots(figsize=dims)

        # Y축 레이블 설정을 위한 글꼴 크기 조정
        ax.tick_params(axis='y', which='major', labelsize=8)

        # 각 코인에 대해 반복
        for index, row in df.iterrows():
            # 개장 가격과 종가 사이의 막대 그리기
            color = 'green' if row['close'] >= row['open'] else 'red'
            ax.barh(index, row['change'], left=0, height=0.4, color=color, edgecolor=color)

            # 고가와 저가 사이 선 그리기
            # 종가를 기준으로 고가와 저가를 표현하기 위한 위치 계산
            high = (row['high'] - row['open']) / row['open'] * 100
            low = (row['low'] - row['open']) / row['open'] * 100
            ax.plot([low, high], [index, index], color=color, linewidth=2)


        # Y축에 코인 이름과 변동률 설정
        ax.set_yticks(range(len(df)))
        ax.set_yticklabels([f"{row['coinName']} ({row['change']:.2f}%)" for index, row in df.iterrows()])

        plt.title('Upbit_'+self.fiat+'_'+datetime.now().strftime("%Y%m%d%H%M"))
        plt.xlabel('Change (%)')

        plt.tight_layout()
        file_name = 'Today_Upbit_Chart_'+self.fiat+'_'+datetime.now().strftime("%Y%m%d%H%M")

        plt.savefig('./result/' + file_name + '.png', format='png', dpi=300)  # dpi는 이미지의 해상도를 지정

