import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# pd.set_option('display.max_rows', 365) #Ограничение вывода 
# pd.reset_option('display.max_rows') #сброс до базы


tickers = ['AAPL']
data = yf.download(tickers, start='2020-01-01')
data = data['Close']

data_for_mean = data.copy()

data_for_mean['SMA50'] = data_for_mean[tickers].rolling(50).mean()
data_for_mean['SMA200'] = data_for_mean[tickers].rolling(200).mean()

condition_list = [
    (data_for_mean['SMA50'] > data_for_mean['SMA200']) & (data_for_mean['SMA50'].shift(1) <= data_for_mean['SMA200'].shift(1)), #Определяем Buy, т.е. 1
    (data_for_mean['SMA50'] < data_for_mean['SMA200']) & (data_for_mean['SMA50'].shift(1) >= data_for_mean['SMA200'].shift(1)) #Определяем Sell, т.е. -1
    ] 
choice_list = [1, -1] #0 - hold, 1 - buy, -1 - sell
data_for_mean['Signal'] = np.select(condition_list, choice_list, 0) #Код 0 = hold

data_for_mean['Дневная доходность в %'] = data_for_mean['AAPL'].pct_change()
cond = [
    data_for_mean['Signal'] == 1,
    data_for_mean['Signal'] == -1
]
choice = [1, 0]

data_for_mean['Позиция'] = np.select(cond, choice, np.nan)
data_for_mean['Позиция'] = data_for_mean['Позиция'].ffill()
data_for_mean['Прибыль'] = (data_for_mean['Позиция'] * data_for_mean['Дневная доходность в %']).cumsum()
data_for_mean['Купи и держи'] = data_for_mean['AAPL'].pct_change().cumsum()

# print(data_for_mean[data_for_mean['Signal'] != 0])
print(data_for_mean)

profit = round(data_for_mean['Прибыль'].iloc[-1] * 100, 2)
print(profit, '%')
buy_n_hold = round(data_for_mean['Купи и держи'].iloc[-1] * 100, 2)
print(buy_n_hold, '%')

#Линейный график скользящей средней
figure, axes = plt.subplots()

#Название осей
axes.set_xlabel('Дата')
axes.set_ylabel('Цена')

#Строим график
axes.plot(data_for_mean.index, data_for_mean['AAPL'], label='AAPL')
axes.plot(data_for_mean.index, data_for_mean['SMA50'], label='SMA50')
axes.plot(data_for_mean.index, data_for_mean['SMA200'], label='SMA200')
axes.set_title('Скользящая средняя')
axes.legend()
buy_scat = data_for_mean[(data_for_mean['Signal'] == 1)]
sell_scat = data_for_mean[(data_for_mean['Signal'] == -1)]

axes.scatter(sell_scat['SMA50'].index, sell_scat['SMA50'], marker='v', c='red', s=100)
axes.scatter(buy_scat['SMA50'].index, buy_scat['SMA50'], marker='^', c='green', s=100)
plt.savefig('linear.png')

#Столбчатый график
fig, ax = plt.subplots()
x_bar = ['SMA стратегия', 'Купи и держи']
y_bar = [profit, buy_n_hold]
label_s = ['SMA стратегия', 'Купи и держи']
bars = ax.bar(x_bar, y_bar)
ax.bar_label(bars, labels=label_s, padding=3)
ax.legend()
ax.set_title('Столбцовая диаграмма')

#Сохранение диаграмм
# figure.savefig('linear.png')  
# fig.savefig('barchart.png')

#Вывод диаграмм
plt.show()


print(data_for_mean[data_for_mean['Signal'] != 0].count())