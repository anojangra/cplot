import mplfinance as mpf
import matplotlib.pyplot as plt
import datetime
import numpy as np
import pandas as pd
from typing import Union


def cplot(data1: pd.DataFrame,
          kind='candle',
          volume=True,
          main_panel=0,
          hide: Union[list, str] = None,
          style: dict = None):
    df = data1.copy()

    # columns to hide
    hide = [hide] if isinstance(hide, str) else [] if hide is None else hide

    # remove columns to hide from df
    df = df[[col for col in df.columns if col not in hide]]

    # hide non plotable cols or if has all na's
    df = df[[col for col in df.columns if
             df[col].dtype in [int, float] and len(df[col].dropna()) > 0]]

    # hide vol panel if no volume or volume hide requested
    volume = 'volume' in df.columns if volume else False

    # columns to be plotted as indicators
    indicator_columns = [col for col in df.columns if col not in 'open high low close volume'.split()]

    # default style for indicators
    default_style = {'ylabel': '{}', 'width': 0.4, 'panel': 0}

    # update default style
    style = {col: (style[col] if col in style.keys() else default_style) for col in indicator_columns}

    no_of_panels = len(set(v['panel'] if 'panel' in v else 0 for k, v in style.items()))
    print(no_of_panels)
    # update ylabel for default style
    for k in style.keys():
        style[k]['ylabel'] = k if 'ylabel' not in style[k] \
            else style[k]['ylabel'].format(k) if ('{' in style[k]['ylabel'] and '}' in style[k]['ylabel']) \
            else style[k]['ylabel']

    # add " to preserve strings in fstring
    style = {k: {k1: f'"{v1}"' if isinstance(v1, str) else v1 for k1, v1 in v.items()} for k, v in style.items() if
             k in df.columns}

    styled_plot = [
        eval(f'mpf.make_addplot(df[k],{"".join([f"{k1}={v1}, " for k1, v1 in v.items()])})', {'mpf': mpf},
             {'df': df, 'k': k})
        for k, v in style.items()]

    fig, ax = mpf.plot(df,
                       volume=volume,
                       type='candle',
                       style='yahoo',
                       addplot=styled_plot,
                       figratio=(16, 9),
                       figscale=1.0,
                       scale_padding=dict(left=0.25, right=0.6, top=0.5, bottom=0.6),
                       panel_ratios=(.8, .2)[:no_of_panels],
                       datetime_format='%H:%M %d/%m/%y',
                       xrotation=25,
                       returnfig=True)
    for i in range(len(ax)):
        ax[i].tick_params(axis='both', which='major', labelsize=8)
    # ax[1].tick_params(axis='both', which='major', labelsize=8)
    # # ax[2].tick_params(axis='both', which='major', labelsize=8)

    plt.show()


if __name__ == '__main__':
    from pronse.pronse import *
    import talib

    nse = Nse()

    data = nse.get_hist(symbol='SBIN', from_date=datetime.date(2019, 5, 1), to_date=datetime.date(2020, 11, 15))[
        'open high low close volume'.split()]

    bb = talib.BBANDS(data.close, 20, 2.5)

    data['BBU'] = bb[0].shift()
    data['BBM'] = bb[1].shift()
    data['BBL'] = bb[2].shift()
    data['atr'] = talib.ATR(data.high, data.low, data.close)
    data['ma'] = data.close.rolling(10).mean()

    cplot(data, style={
        'BBL': {'ylabel': 'ty', 'width': 0.4, 'panel': 0, 'color': 'b'},
        'BBM': {'ylabel': 'kh', 'width': 0.4, 'panel': 0, 'color': 'r'},
        'BBU': {'ylabel': 'sd', 'width': 0.4, 'panel': 0, 'color': 'b'},
        'atr': {'width': 0.4, 'panel': 1, 'color': 'b'},
    },
          hide='batr',
          volume=False)
