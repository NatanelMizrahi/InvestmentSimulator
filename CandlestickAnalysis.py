import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import yfinance as yf

### IMPLEMENTED ###
MAX_HIST = 5
TICKERS  = ['AAPL', 'MSFT']
class CandleStickAnalyzer:
    def get_stock_data(ticker):
        return yf.download(tickers=ticker, period='max', interval='1d').reset_index(level=0)

    def add_prediction(df):
        hist = list(map(df.shift, range(0,MAX_HIST))) # hist[i] = data shifted by i days
        # simplest predicate for now: how small are the tails of the previous day
        df["prediction"] = (hist[1]['Open']-hist[1]['Close'])/(hist[1]['High']-hist[1]['Low']) 
        return df

    def add_score(df):
        df["actual"] = (df['Open'] >= df['Close']).replace({True: 1, False: -1}) # TODO: add weight
        df["score"]  = df["prediction"] * df["actual"]
        df["binary_score"] = (df["score"] >= 0)
        df["continuous"] = -10 # constant to keep as a line under the chart
        df["discrete"]   = -20 # constant to keep as a line under the chart
        return df

    def plot_candlestick_and_score(df):
        fig = px.scatter(df, 
                         x=df['Date'], 
                         y="continuous", 
                         color="score", 
                         color_continuous_scale=px.colors.diverging.RdYlGn)
        for trace in px.scatter(df, 
                         x=df['Date'], 
                         y="discrete", 
                         color="binary_score",
                         color_discrete_sequence=px.colors.qualitative.Light24).data:
            fig.add_trace(trace)
            
        fig.add_trace(go.Candlestick(
                        x=df['Date'],
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close']))
        fig.show()
    
def get_avg_score(df):
    return df["score"].mean()

def fetch_and_display_stock_data(ticker):
    df = get_stock_data(ticker)
    df = add_prediction(df)
    df = add_score(df)
    plot_candlestick_and_score(df)
    print(get_avg_score(df))
    return df

#### TODO ####
def main():
    for ticker in TICKERS:
        df = get_stock_data(ticker)
        candle_stick_analysis(df) 
        lstm_analysis(df)         
        sentiment_analysis(df)    
        predict(df)
    view_predictions()
##############
if __name__ == "__main__":
   main() 

df = fetch_and_display_stock_data('DJI')
