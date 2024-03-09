import pyupbit
import pandas as pd
import matplotlib.pyplot as plt
from UpbitChartGenerator import UpbitChartGenerator


if __name__ == '__main__':
    chrt =  UpbitChartGenerator('KRW',1)
    chrt.setDfData().getChartImg()
