import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from functools import lru_cache as cache
# Data Source
import yfinance as yf


class Config:
    MAX_HIST = 5
    TICKERS = ['AAPL', 'MSFT']
    WEIGHTS = {
        'Candlestick': .3,
        'LTSM': .5,
        'Sentiment': .2
    }


class BaseAnalyzer:
    def __init__(self, ticker):
        self.ticker = ticker
        self.df = self.get_stock_data(ticker)  # TODO cache
        self.hist_dfs = self.get_hist()
        self.short_term_prediction_df = None
        self.mid_term_prediction_df = None

    def get_hist(self):
        """hist_dfs[i] = stock data shifted by i days"""
        return list(map(self.df.shift, range(0, Config.MAX_HIST)))

    @staticmethod
    @cache()
    def get_stock_data(ticker):
        """get stock data from yahoo finance"""
        return yf.download(tickers=ticker, period='max', interval='1d').reset_index(level=0)

    def analyze(self):
        return NotImplemented

    def get_prediction(self):
        return NotImplemented


class CandlestickAnalyzer(BaseAnalyzer):
    def analyze(self):
        self.add_prediction()
        self.add_score()
        self.plot_candlestick_and_score()

    def add_prediction(self):
        # simplest predicate for now: how small are the tails of the previous day
        hist = self.hist_dfs
        self.df["prediction"] = (hist[1]['Open'] - hist[1]['Close']) / (hist[1]['High'] - hist[1]['Low'])

    def add_score(self):
        self.df["actual"] = (self.df['Open'] >= self.df['Close']).replace({True: 1, False: -1})  # TODO: add weight
        self.df["score"] = self.df["prediction"] * self.df["actual"]
        self.df["binary_score"] = (self.df["score"] >= 0)
        self.df["continuous"] = -10  # constant to keep as a line under the chart
        self.df["discrete"] = -20  # constant to keep as a line under the chart

    def plot_candlestick_and_score(self):
        fig = px.scatter(self.df,
                         x=self.df['Date'],
                         y="continuous",
                         color="score",
                         color_continuous_scale=px.colors.diverging.RdYlGn)
        for trace in px.scatter(self.df,
                                x=self.df['Date'],
                                y="discrete",
                                color="binary_score",
                                color_discrete_sequence=px.colors.qualitative.Light24).data:
            fig.add_trace(trace)

        fig.add_trace(go.Candlestick(
            x=self.df['Date'],
            open=self.df['Open'],
            high=self.df['High'],
            low=self.df['Low'],
            close=self.df['Close']))
        fig.show()

    def get_avg_score(self):
        return self.df["score"].mean()


class LSTMAnalyzer(BaseAnalyzer):
    pass


class SentimentAnalyzer(BaseAnalyzer):
    pass


class StockAnalyzer(BaseAnalyzer):
    def __init__(self, ticker):
        super().__init__(ticker)
        self.analyzers = {}
        self.analyzers['Candlestick'] = CandlestickAnalyzer(ticker)
        self.analyzers['LSTM'] = LSTMAnalyzer(ticker)
        self.analyzers['Sentiment'] = SentimentAnalyzer(ticker)

    def analyze(self):
        for analyzer in self.analyzers.values():
            analyzer.analyze()

    def get_prediction(self):
        return NotImplemented


def get_tickers_data(tickers):
    df = yf.download(tickers=tickers, period='max', interval='1d').reset_index(level=0)
    df.columns = df.columns.swaplevel(0, 1)
    df.sort_index(axis=1, level=0, inplace=True)


get_tickers_data(['AAPL', 'MSFT', 'GOOGL'])


def main():
    predictions = {}
    for ticker in Config.TICKERS:
        predictions[ticker] = StockAnalyzer(ticker).analyze()


if __name__ == "__main__":
    main()
