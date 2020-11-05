import db_function
import plotly.express as px
from plotly.colors import n_colors
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
import plotly.figure_factory as ff
from plotly.offline import download_plotlyjs, init_notebook_mode,  iplot


def plot_trade_histogram(trade_df):
    # histogram
    fig = px.histogram(trade_df, x="dateTime", y="netCash", color="symbol")
    fig.update_traces(xbins_size="M1")
    fig.update_xaxes(showgrid=True, ticklabelmode="period", dtick="M1", tickformat="%b\n%Y")
    fig.update_layout(bargap=0.4)
    # fig = px.line(trade_df, x="dateTime", y="netCash")

    # fig = px.area(trade_df, facet_col="symbol", facet_col_wrap=2)
    fig.show()
    return


def display_cmap(cmap):  # Display  a colormap cmap
    plt.imshow(np.linspace(0, 100, 256)[None, :], aspect=25, interpolation='nearest', cmap=cmap)
    plt.axis('off')


def colormap_to_colorscale(cmap):
    # function that transforms a matplotlib colormap to a Plotly colorscale
    return [[k * 0.1, colors.rgb2hex(cmap(k * 0.1))] for k in range(11)]


def plot_table(trade_df):
    return


def normalize(x, a, b):  # maps  the interval [a,b]  to [0,1]
    if a >= b:
        raise ValueError('(a,b) is not an interval')
    return float(x - a) / (b - a)


def colorscale_from_list(alist, name):
    # Defines a colormap, and the corresponding Plotly colorscale from the list alist
    # alist=the list of basic colors
    # name is the name of the corresponding matplotlib colormap

    cmap = LinearSegmentedColormap.from_list(name, alist)
    display_cmap(cmap)
    colorscale = colormap_to_colorscale(cmap)
    return cmap, colorscale

def asymmetric_colorscale(data, div_cmap, ref_point=0.0, step=0.05):
    # data: data can be a DataFrame, list of equal length lists, np.array, np.ma.array
    # div_cmap is the symmetric diverging matplotlib or custom colormap
    # ref_point:  reference point
    # step:  is step size for t in [0,1] to evaluate the colormap at t

    if isinstance(data, pd.DataFrame):
        D = data.values
    elif isinstance(data, np.ma.core.MaskedArray):
        D = np.ma.copy(data)
    else:
        D = np.asarray(data, dtype=np.float)

    dmin = np.nanmin(D)
    dmax = np.nanmax(D)
    if not (dmin < ref_point < dmax):
        raise ValueError('data are not appropriate for a diverging colormap')

    if dmax + dmin > 2.0 * ref_point:
        left = 2 * ref_point - dmax
        right = dmax

        s = normalize(dmin, left, right)
        refp_norm = normalize(ref_point, left, right)  # normalize reference point

        T = np.arange(refp_norm, s, -step).tolist() + [s]
        T = T[::-1] + np.arange(refp_norm + step, 1, step).tolist()


    else:
        left = dmin
        right = 2 * ref_point - dmin

        s = normalize(dmax, left, right)
        refp_norm = normalize(ref_point, left, right)

        T = np.arange(refp_norm, 0, -step).tolist() + [0]
        T = T[::-1] + np.arange(refp_norm + step, s, step).tolist() + [s]

    L = len(T)
    T_norm = [normalize(T[k], T[0], T[-1]) for k in range(L)]  # normalize T values
    return [[T_norm[k], colors.rgb2hex(div_cmap(T[k]))] for k in range(L)]


if __name__ == '__main__':
    trade_query = "SELECT * from trade"
    trade_df = db_function.read_db(trade_query)
    print(trade_df.columns)
    print(trade_df.dtypes)
    # print(trade_df['dateTime'])
    # print(trade_df['netCash'])
    # table setup

    cols_to_show = ['symbol', 'description', 'dateTime', 'quantity', 'tradePrice',
                    'ibCommission', 'netCash', 'cost']
    print(trade_df.columns)

    tab = trade_df['netCash'].values.tolist()
    tab = np.array(tab)
    # print(np.min(tab))

    redgreen = ['#df0101', '#f5f6ce', '#31b404']
    fin_cmap, fin_cs = colorscale_from_list(redgreen, 'fin_cmap')
    fin_asymm_cs = asymmetric_colorscale(tab, fin_cmap, ref_point=0.0, step=0.05)
    print(fin_asymm_cs)
    # color scale
    a = [4, 11, 0, 32]
    blues = n_colors('rgb(200, 200, 255)', 'rgb(0, 0, 200)', max(a) + 1, colortype='rgb')
    print(blues)
    print([np.array(blues)[a]])
    '''

    
    for col in cols_to_show:
        if col!='':

    '''
    print(trade_df[cols_to_show].values.T)
    trace = dict(type = 'table',
             columnwidth= [20] + [50] + [50] + [20] + [20] + [20] + [20] + [20],
             header = dict(height = 50,
                           values=list(trade_df.columns),
                           line = dict(color='rgb(50, 50, 50)'),
                           align = 'left',
                           font = dict(color=['rgb(45, 45, 45)'], size=14),
                           fill = dict( color = 'rgb(235, 235, 235)' )
                              ),
                 cells=dict(values=trade_df[cols_to_show].values.T,
                            line=dict(color='#506784'),
                            align='left',
                            font=dict(color=['rgb(40, 40, 40)'], size=12),
                            format=[None, ",.2f"],
                            height=30,
                            fill=dict(color=['rgb(245, 245, 245)',  # unique color for the first column
                                             'rgb(245, 245, 245)',  # unique color for the first column
                                             'rgb(245, 245, 245)',  # unique color for the first column
                                             'rgb(245, 245, 245)',  # unique color for the first column
                                             'rgb(245, 245, 245)',  # unique color for the first column
                                             'rgb(245, 245, 245)',  # unique color for the first column
                                             ['rgba(0, 250, 0, 0.8)' if item >= 0 else 'rgba(250, 0, 0, 0.8)' for item in
                                              trade_df[cols_to_show].values.T[6]],
                                             'rgb(245, 245, 245)'] # unique color for the first column]
                                      # the cells in the second column are colored with green or red, according to their values(+ or -)
                                      )
                            )

            )

    layout = dict(width=1500, height=800, autosize=True,
                  title='Cells colored according to their values', showlegend=False)
    fig = dict(data=[trace], layout=layout)
    iplot(fig)

    '''
        # redblues = n_colors('rgb(255, 200, 255)', 'rgb(200, 200, 255)', max(a) + 1, colortype='rgb')
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(trade_df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=trade_df[cols_to_show].values.T,
                   # values =[trade_df.symbol, trade_df.dateTime, trade_df.quantity, trade_df.tradePrice],
                   fill_color=[np.array(blues)[a]],
                   align='left'))
    ])


    # fig.add_trace(go.Table(tbl))
    fig.show()

    '''

