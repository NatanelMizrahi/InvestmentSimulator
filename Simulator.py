import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

pd.set_option('display.max_rows', 600)

#Data Source
import yfinance as yf

def plot(data):
    data_with_date = data.reset_index(level=0)
    fig = px.line(data_with_date, x='Date', y="weighted_sum")
    fig.show()

def reorder_weights(columns, tickers, weights =[]):
    weights = weights or len(columns) * [1]
    tickers_weights = zip(tickers,weights)
    sorted_tickers_weights = sorted(tickers_weights, key=lambda tickers_weight: columns.index(tickers_weight[0]))
    return [weight for ticker, weight in sorted_tickers_weights]


def normalize_data(tickers,weights=[]):
    data = yf.download(tickers=tickers, period='max', interval='1d')
    filtered_data = data['Close'].dropna() #.reset_index(level=0)
    normalized_data = filtered_data.div(filtered_data.iloc[0])
    weights = weights or len(normalized_data.columns) * [1]
    normalized_data['weighted_sum'] = normalized_data.dot(weights)
    return normalized_data

ticker_weight_map = {
    'iShares Core S&P 500 UCITS ETF USD (Acc)':                             ('CSSPX.MI',    .5),
    'iShares Core MSCI EM IMI UCITS ETF USD (Acc)':                         ('EIMI.MI',     .13),
    'iShares S&P 500 Information Technology Sector UCITS ETF USD (Acc)':    ('IUIT.L',      .2),
    'iShares MSCI Europe UCITS ETF EUR (Acc)':                              ('IMEA.SW',     .17)
}

ticker_weight_map = {
    'S&P500':                             ('^GSPC',    .5),
    'MSCI EM':                            ('EEM',     .13),
    # 'S&P 500 Information Technology':     ('^SP500-45',      .2),
    'MSCI Europe':                        ('^STOXX',     .37)
}


def weigthed_sum(ticker_weight_pairs):
    tickers, weights = zip(*ticker_weight_pairs)
    return normalize_data(tickers, weights)


def plot_candlestick(ticker):
    df = yf.download(tickers=ticker, period='max', interval='1d').reset_index(level=0)
    fig = go.Figure(data=[go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])
    fig.show()

plot(weigthed_sum(list(ticker_weight_map.values())))
# https://stackoverflow.com/questions/22081878/get-previous-rows-value-and-calculate-new-column-pandas-python
#https://plotly.com/python/builtin-colorscales/