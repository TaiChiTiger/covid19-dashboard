import dash_echarts
from dash.dependencies import Input, Output
from dash import dcc, Dash
import dash_html_components as html
import dash_bootstrap_components as dbc
from os import path
import pandas as pd
import json
import plotly.graph_objects as go
from datetime import datetime, timedelta
from copy import deepcopy
from datetime import datetime
import numpy as np
import time
import urllib3
# from dash import Dash


def connect_url(url):
    http = urllib3.PoolManager()
    retries = 1
    success = False
    while not success:
        try:
            response = http.request('GET', url)
            success = True
        except Exception as e:
            wait = retries * 5
            print("没能获取数据，重新连接...")
            time.sleep(wait)
            retries += 1
    
    return success

def connect_data_source():
    confirmed_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    death_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
    vcc_url = "https://raw.githubusercontent.com/govex/COVID-19/master/data_tables/vaccine_data/global_data/time_series_covid19_vaccine_global.csv"
    get_confirmed_url = connect_url(confirmed_url)
    get_death_url = connect_url(death_url)
    get_vcc_url = connect_url(vcc_url)
    if get_confirmed_url and get_death_url and get_vcc_url:
        return confirmed_url, death_url, vcc_url
    else:
        return None

def data_preparing():
    try:
        # x = datetime.today()
        # y = x.replace(day=0, hour=x.hour+1, minute=1, second=0, microsecond=0)
        # delta_t = y - x
        # secs = delta_t.seconds + 1
        # t = Timer(secs, connect_data_source)
        # t.start()
        # if connect_data_source() is None:
        #     print("未能连接数据")
        #     return None, None, None
        # else:
        #confirmed_url, death_url, vcc_url = connect_data_source()

        # 过去28天感染
        # confirmed = pd.read_csv(confirmed_url)
        basepath = path.dirname(__file__)
        confirmed_path = basepath + '/datasets/time_series_covid19_confirmed_global.csv'
        confirmed = pd.read_csv(confirmed_path)
        ll = [32070, 36552,42861,51014,59949,73299,90336,110003,130902,154106, 178858,205438,228507, 254814,282419, 305491, 329004, 353826, 374242, 396490, 415391, 433886, 451515, 474885, 495943, 515398, 545940, 556562, 571594]
        confirmed.iloc[confirmed[confirmed["Province/State"] == "Shanghai"].index, -29:] = ll
        confirmed = confirmed[(confirmed["Country/Region"] == "China") | (confirmed["Country/Region"] == "Taiwan*")]
        confirmed.loc[confirmed["Country/Region"] == 'Taiwan*', "Province/State"] = "Taiwan"
        confirmed.drop(["Country/Region", "Lat", "Long"], inplace=True, axis=1)
        confirmed.rename({"Province/State": "Province"}, axis=1, inplace=True)
        confirmed = confirmed[confirmed["Province"] != "Unknown"]
        confirmed = confirmed.iloc[:, [0] + list(range(-28, 0))]
        confirmed = confirmed.astype({"Province": str})
        province_dict = {"Xinjiang": "新疆",
            "Tibet": "西藏",
            "Inner Mongolia": "内蒙古",
            "Qinghai": "青海",
            "Sichuan": "四川",
            "Heilongjiang": "黑龙江",
            "Gansu": "甘肃",
            "Yunnan": "云南",
            "Guangxi": "广西",
            "Hunan": "湖南",
            "Shaanxi": "陕西",
            "Guangdong": "广东",
            "Jilin": "吉林",
            "Hebei": "河北",
            "Hubei": "湖北",
            "Guizhou": "贵州",
            "Shandong": "山东",
            "Jiangxi": "江西",
            "Henan": "河南",
            "Liaoning": "辽宁",
            "Shanxi": "山西",
            "Anhui": "安徽",
            "Fujian": "福建",
            "Zhejiang": "浙江",
            "Jiangsu": "江苏",
            "Chongqing": "重庆",
            "Ningxia": "宁夏",
            "Hainan": "海南",
            "Taiwan": "台湾",
            "Beijing": "北京",
            "Tianjin": "天津",
            "Shanghai": "上海",
            "Hong Kong": "香港",
            "Macau": "澳门"}
        confirmed["Province"] = confirmed["Province"].map(province_dict)
        past28_confirmed = pd.DataFrame(confirmed.T, index=confirmed.columns[1:])
        columns_dict = {k: v for k, v in zip(past28_confirmed.columns, confirmed["Province"])}
        past28_confirmed.rename(columns_dict, axis=1, inplace=True)

        # 过去28天全部死亡
        # deaths = pd.read_csv(death_url)
        dealth_path = basepath + '/datasets/time_series_covid19_deaths_global.csv'
        deaths = pd.read_csv(dealth_path)
        deaths = deaths[(deaths["Country/Region"] == "China") | (deaths["Country/Region"] == "Taiwan*")]
        deaths.loc[deaths["Country/Region"] == 'Taiwan*', "Province/State"] = "Taiwan"
        deaths.drop(["Country/Region", "Lat", "Long"], inplace=True, axis=1)
        deaths.rename({"Province/State": "Province"}, axis=1, inplace=True)
        deaths = deaths[deaths["Province"] != "Unknown"]
        deaths = deaths.iloc[:, [0] + list(range(-28, 0))]
        deaths = deaths.astype({"Province": str})
        deaths["Province"] = deaths["Province"].map(province_dict)
        # 过去28天全部死亡
        past28_deaths = pd.DataFrame(deaths.T, index=deaths.columns[1:])
        columns_dict = {k: v for k, v in zip(past28_deaths.columns, deaths["Province"])}
        past28_deaths.rename(columns_dict, axis=1, inplace=True)

        # 过去28天疫苗接种
        # vcc_df_orig = pd.read_csv(vcc_url)
        vcc_path = basepath + '/datasets/time_series_covid19_vaccine_global.csv'
        vcc_df_orig = pd.read_csv(vcc_path)
        vcc_df = vcc_df_orig[(vcc_df_orig["Country_Region"] == "China") | (vcc_df_orig["Country_Region"] == "Taiwan*")]
        columns = ["Country_Region", "Report_Date_String", "People_partially_vaccinated", "People_fully_vaccinated"]
        vcc_df = vcc_df[columns]
        vcc_df["Date"] = pd.to_datetime(vcc_df["Date"])
        vcc_df = vcc_df[vcc_df["Date"] > vcc_df["Date"].max() - pd.Timedelta(28, "d")]
        vcc_df.rename({'Date': 'Date'}, axis=1, inplace=True)
        vcc_df.dropna(inplace=True)
        vcc_df = vcc_df.groupby(by=["Date"]).sum(["People_at_least_one_dose", "Doses_admin"])

        return past28_confirmed, past28_deaths, vcc_df
    except ValueError:
        raise ValueError("未能下载数据！")

    

def plot_indicator(new_increase_confirmed, new_increase_deaths, 
                        new28_increase_confirmed, new28_increase_deaths,
                        num_current_confirmed, num_current_deaths):
    indicator1 = go.Indicator(
        mode = "number+delta",
        title = {"text": "单日新增感染"},
        value = new_increase_confirmed,
        number = {'valueformat':'f'},
        # delta = {'reference': num_past_confirmed, "valueformat": "f"},
        domain = {'row': 0, 'column': 0}
    )
    indicator2 = go.Indicator(
        mode = "number+delta",
        title = {"text": "单日新增死亡"},
        value = new_increase_deaths,
        number = {'valueformat':'f'},
        # delta = {'reference': num_past_confirmed, "valueformat": "f"},
        domain = {'row': 0, 'column': 1}
    )
    indicator3 = go.Indicator(
        mode = "number+delta",
        title = {"text": "过去28天新增确诊"},
        value = new28_increase_deaths,
        number = {'valueformat':'f'},
        # delta = {'reference': num_past_confirmed, "valueformat": "f"},
        domain = {'row': 0, 'column': 2}
    )
    indicator4 = go.Indicator(
        mode = "number+delta",
        title = {"text": "过去28天新增死亡"},
        value = new28_increase_confirmed,
        number = {'valueformat':'f'},
        # delta = {'reference': num_past_confirmed, "valueformat": "f"},
        domain = {'row': 0, 'column': 3}
    )
    indicator5 = go.Indicator(
        mode = "number+delta",
        title = {"text": "全部确诊"},
        value = num_current_confirmed,
        number = {'valueformat':'f'},
        # delta = {'reference': num_past_confirmed, "valueformat": "f"},
        domain = {'row': 0, 'column': 4}
    )
    indicator6 = go.Indicator(
        mode = "number+delta",
        title = {"text": "全部死亡"},
        value = num_current_deaths,
        number = {'valueformat':'f'},
        # delta = {'reference': num_past_deaths, "valueformat": "f"},
        domain = {'row': 0, 'column': 5}
    )
    fig = go.Figure(data=[indicator1, indicator2, indicator3, indicator4, indicator5, indicator6])
    fig.update_layout(
        grid = {'rows': 1, 'columns': 6, 'pattern': "independent"}
    )
    return fig

def plot_pie(confirmed, deaths, pie_title):
    colors = ['gold', 'red', 'darkorange', 'lightgreen']
    fig = go.Figure(data=[go.Pie(labels=['感染','死亡'],
                values=[confirmed, deaths], hole=.3)])
    fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=15,
                  marker=dict(colors=colors, line=dict(color='#000000', width=0)))
    fig.update_layout(
        title=dict(text=pie_title, x=0.5, y=0.992),
        legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.03,
                xanchor="right",
                x=1
            ),
        margin=dict(t=80, l=10, r=10, b=10),
        width=300,
        height=300,
        font_color="white",
        paper_bgcolor='rgba(0,0,0,0)',
        # plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig

def plot_time_series(df, ts_title):
    trace = go.Scatter(
        mode="lines+markers+text",
        x=df.index,
        y=df.values.ravel(),
        marker=dict(color='gold'),
        text=df.values.astype(str).ravel(),
        textposition="top center",
        textfont=dict(
            size=8,
        )
    )
    fig = go.Figure(data=trace)
    fig.update_layout(
        title=dict(text=ts_title, x=0.5),
        margin=dict(t=32, l=0, r=0, b=0),
        width=610,
        height=300,
        font_color="white",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    fig.update_xaxes(showgrid=False, tickangle=45)
    fig.update_yaxes(showgrid=False)
    return fig

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], update_title='更新中...')
confirmed, deaths, vcc = data_preparing()
update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 当前全部确诊
num_current_confirmed = confirmed.iloc[-1, :].sum()
# 当前全部死亡
num_current_deaths = deaths.iloc[-1, :].sum()
# 昨日新增感染
num_past_confirmed = confirmed.iloc[-2, :].sum()
new_increase_confirmed = num_current_confirmed - num_past_confirmed
# 昨日新增死亡
num_past_deaths = deaths.iloc[-2, :].sum()
new_increase_deaths = num_current_deaths - num_past_deaths
# 过去28天新增感染
last28_confirmed = confirmed.iloc[[0, -1], :]
new28_increase_confirmed = sum(last28_confirmed.iloc[-1, :] - last28_confirmed.iloc[-2, :])

# 过去28天新增死亡
last28_deaths = deaths.iloc[[0, -1], :]
new28_increase_deaths = sum(last28_deaths.iloc[-1, :] - last28_deaths.iloc[-2, :])
# 昨日新增疫苗接种人数
past1_vcc_df = vcc.iloc[-1, :] - vcc.iloc[-2, :]
past1_partial_vcc = int(past1_vcc_df["People_at_least_one_dose"])
past1_full_vcc = int(past1_vcc_df["Doses_admin"])
# 过去28天新增疫苗接种人数
past28_vcc_df = vcc.iloc[-1, :] - vcc.iloc[0, :]
past28_partial_vcc = int(past28_vcc_df["People_at_least_one_dose"])
past28_full_vcc = int(past28_vcc_df["Doses_admin"])
# 疫苗接种总人数
all_vcc_df = vcc.iloc[-1, :]
all_partial_vcc = int(all_vcc_df["People_at_least_one_dose"])
all_full_vcc = int(all_vcc_df["Doses_admin"])

# fig = plot_indicator(new_increase_confirmed, new_increase_deaths, 
#                     new28_increase_confirmed, new28_increase_deaths,
#                     num_current_confirmed, num_current_deaths)

# 昨日新增感染排名
last2days_confirmed = confirmed.iloc[[-2, -1], :]

# 单日新增死亡排名
last2days_deaths = deaths.iloc[[-2, -1], :]


# 建立仪表盘
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], update_title='更新中...')
app.title = '疫情概要'
server = app.server

config = {"displayModeBar": False}

last_increase_confirmed = sum(confirmed.iloc[-2, :] - confirmed.iloc[-3, :])
if new_increase_confirmed > last_increase_confirmed:
    refer_info = html.H6("比前日增加{}".format(new_increase_confirmed - last_increase_confirmed),
                        style={'color': 'red'})
elif new_increase_confirmed < last_increase_confirmed:
    refer_info = html.H6("比前日减少{}".format(last_increase_confirmed - new_increase_confirmed),
                        style={'color': 'lime'})
else:
    refer_info = None

new_confirmed_card = dbc.Col([
            dbc.Card([
                dbc.CardHeader("昨日新增感染", style={"color": 'gold'}),
                dbc.CardBody([
                    html.H2("{:,}".format(new_increase_confirmed), style={"color": 'gold'}),
                    refer_info
                ])
            ], style={"width": "16rem"})
        ], style={'margin-left': '10px', 'width': '100%', 'text-align': 'center', 'color':'white'},
    )
new_death_card = dbc.Col([
            dbc.Card([
                dbc.CardHeader("昨日新增死亡", style={"color": 'red'}),
                dbc.CardBody([
                    html.H2("{:,}".format(new_increase_deaths), style={"color": 'red'})
                ])
            ], style={"width": "16rem"})
        ], style={'width': '100%', 'text-align': 'center', 'color':'white'},
    )
new1_parvcc_card  = dbc.Col([
            dbc.Card([
                dbc.CardHeader("昨日新增部分疫苗接种", style={"color": 'lime'}),
                dbc.CardBody([
                    html.H2("{:,}".format(past1_partial_vcc), style={"color": 'lime'})
                ])
            ], style={"width": "19rem"})
        ], style={'width': '100%', 'text-align': 'center', 'color':'white'},
    )
new1_fulvcc_card  = dbc.Col([
            dbc.Card([
                dbc.CardHeader("昨日新增完全疫苗接种", style={"color": 'lime'}),
                dbc.CardBody([
                    html.H2("{:,}".format(past1_full_vcc), style={"color": 'lime'})
                ])
            ], style={"width": "19rem"})
        ], style={'margin-right': '10px', 'width': '100%', 'text-align': 'center', 'color':'white'},
    )
new28_confirmed_card = dbc.Col([
            dbc.Card([
                dbc.CardHeader("过去28天累计新增感染", style={"color": 'gold'}),
                dbc.CardBody([
                    html.H2("{:,}".format(new28_increase_confirmed), style={"color": 'gold'})
                ])
            ], style={"width": "16rem"})
        ], style={'margin-left': '10px', 'width': '100%', 'text-align': 'center', 'color':'white'},
    )
new28_deaths_card = dbc.Col([
            dbc.Card([
                dbc.CardHeader("过去28天累计新增死亡", style={"color": 'red'}),
                dbc.CardBody([
                    html.H2("{:,}".format(new28_increase_deaths), style={"color": 'red'})
                ])
            ], style={"width": "16rem"})
        ], style={'width': '100%', 'text-align': 'center', 'color':'white'},
    )
new28_parvcc_card  = dbc.Col([
            dbc.Card([
                dbc.CardHeader("过去28天累计新增部分疫苗接种", style={"color": 'lime'}),
                dbc.CardBody([
                    html.H2("{:,}".format(past28_partial_vcc), style={"color": 'lime'})
                ])
            ], style={"width": "19rem"})
        ], style={'width': '100%', 'text-align': 'center', 'color':'white'},
    )
new28_fulvcc_card  = dbc.Col([
            dbc.Card([
                dbc.CardHeader("过去28天累计新增完全疫苗接种", style={"color": 'lime'}),
                dbc.CardBody([
                    html.H2("{:,}".format(past28_full_vcc), style={"color": 'lime'})
                ])
            ], style={"width": "19rem"})
        ], style={'margin-right': '10px', 'width': '100%', 'text-align': 'center', 'color':'white'},
    )
all_confirmed_card = dbc.Col([
            dbc.Card([
                dbc.CardHeader("全部累计感染", style={"color": 'gold'}),
                dbc.CardBody([
                    html.H2("{:,}".format(num_current_confirmed), style={"color": 'gold'})
                ])
            ], style={"width": "16rem"})
        ], style={'margin-left': '10px', 'width': '100%', 'text-align': 'center', 'color':'white'},
    )
all_deaths_card = dbc.Col([
            dbc.Card([
                dbc.CardHeader("全部累计死亡", style={"color": 'red'}),
                dbc.CardBody([
                    html.H2("{:,}".format(num_current_deaths), style={"color": 'red'})
                ])
            ], style={"width": "16rem"})
        ], style={'width': '100%', 'text-align': 'center', 'color':'white'},
    )
all_parvcc_card  = dbc.Col([
            dbc.Card([
                dbc.CardHeader("全部累计部分疫苗接种", style={"color": 'lime'}),
                dbc.CardBody([
                    html.H2("{:,}".format(all_partial_vcc), style={"color": 'lime'})
                ])
            ], style={"width": "19rem"})
        ], style={'width': '100%', 'text-align': 'center', 'color':'white'},
    )
all_fulvcc_card  = dbc.Col([
            dbc.Card([
                dbc.CardHeader("全部累计完全疫苗接种", style={"color": 'lime'}),
                dbc.CardBody([
                    html.H2("{:,}".format(all_full_vcc), style={"color": 'lime'})
                ])
            ], style={"width": "19rem"})
        ], style={'margin-right': '10px', 'width': '100%', 'text-align': 'center', 'color':'white'},
    )
# yesterday = datetime.today() - timedelta(days=1)
# yesterday = yesterday.strftime("%Y-%m-%d")

# 过去28天感染
past28_new_confirmed = confirmed - confirmed.shift(1, fill_value=0)
past28_new_confirmed = past28_new_confirmed.iloc[1:, :]
last_row = past28_new_confirmed.iloc[-1, :]
sorted_columns = past28_new_confirmed.columns[np.argsort(last_row.values)[::-1]]
past28_new_confirmed = past28_new_confirmed[sorted_columns]
large_city = sorted_columns[0]
past28_confirmed_large = past28_new_confirmed[large_city]

# 数据发布日期
collect_date = pd.to_datetime(past28_new_confirmed.index[-1])
publish_date = (collect_date + timedelta(days=1)).strftime("%Y年%m月%d日")

ts_title = "过去28天{}每日新增感染病例".format(large_city)
ts_fig = plot_time_series(past28_confirmed_large, ts_title)

# 全部累计感染
all_confirmed_large = last2days_confirmed[[large_city]].iloc[-1, :].values[0]
all_deaths_large = last2days_deaths[[large_city]].iloc[-1, :].values[0]
pie_title = "{}全部累计病例".format(large_city)
pie_fig = plot_pie(all_confirmed_large, all_deaths_large, pie_title)

# 昨日感染地图数据
new_confirmed_lst = [{"name": k, "value": v} 
                    for k, v in zip(past28_new_confirmed.columns, past28_new_confirmed.iloc[-1, :].tolist())]
# 过去28天新增感染地图数据
last28_confirmed_map = pd.DataFrame()
last28_confirmed_map['name'] = last28_confirmed.columns
last28_confirmed_map['value'] = last28_confirmed.iloc[-1, :].values - last28_confirmed.iloc[-2, :].values
last28_confirmed_lst = [{"name": k, "value": v} 
                        for k, v in zip(last28_confirmed_map['name'], last28_confirmed_map['value'].tolist())]
# 累计感染
all_confirmed = confirmed.iloc[-1, :]
all_confirmed_map = pd.DataFrame()
all_confirmed_map['name'] = confirmed.columns
all_confirmed_map['value'] = all_confirmed.tolist()
all_confirmed_lst = [{"name": k, "value": v} for k, v in all_confirmed_map.values]

option =  {
    'title': {
        # 'text': '全国疫情地图',
        'left': 'center',
        'textStyle': {'color': 'white', 'fontFamily': 'Microsoft YaHei', 'fontWeight': 'normal'}
    },
    'tooltip': {
        'trigger': 'item',
        'formatter': '{b}<br/>{c}'
    },
    'toolbox': {
        'show': False,
        'orient': 'vertical',
        'left': 'right',
        'top': 'center',
        'feature': {
            'dataView': {'readOnly': False},
            'restore': {},
            'saveAsImage': {}
        }
    },
    'visualMap': {
        'min': 0,
        'max': num_current_confirmed,
        'text': ['高', '低'],
        'textStyle': {'color': 'white'},
        'realtime': False,
        'calculable': True,
        'inRange': {
            'color': ['lightskyblue', 'yellow', 'orangered']
        }
    },
    'series': [
        {
            'name': '全国疫情地图',
            'type': 'map',
            'mapType': 'china', 
            'label': {
                'show': True,
                'fontSize': 10,
                'position': 'right'
            },
            'zoom': 1.2,
            'data': None,
        }
    ]
}
option["series"][0]['data'] = new_confirmed_lst
option["visualMap"]['max'] = int(new_increase_confirmed / 15)
new_confirmed_opt = deepcopy(option)
option["series"][0]['data'] = last28_confirmed_lst
option["visualMap"]['max'] = int(new28_increase_confirmed / 15)
last28_confirmed_opt = deepcopy(option)
option["series"][0]['data'] = all_confirmed_lst
option["visualMap"]['max'] = int(num_current_confirmed / 15) 
all_confirmed_opt = option

# 加载底图
basepath = path.dirname(__file__)
filepath = path.abspath(path.join(basepath+'/static', 'china2.json'))
# filepath = "E:/Docker/Projects/flask/flask-dash-app-master/app/dash/use_cases/pages/covid19/static/china2.json"
with open(filepath, encoding='UTF-8') as json_file:
    china_map = json.load(json_file)

new_confirmed_map_data = dash_echarts.DashECharts(
        option = new_confirmed_opt,
        id='new_confirmed_echarts',
        style={
            "width": '80vw',
            "height": '80vh',
        },
        maps={
            "china": china_map
        }
    )
last28_confirmed_map_data = dash_echarts.DashECharts(
        option = last28_confirmed_opt,
        id='last28_confirmed_echarts',
        style={
            "width": '80vw',
            "height": '80vh',
        },
        maps={
            "china": china_map
        }
    )
all_confirmed_map_data = dash_echarts.DashECharts(
        option = all_confirmed_opt,
        id='all_confirmed_echarts',
        style={
            "width": '80vw',
            "height": '80vh',
        },
        maps={
            "china": china_map
        }
    )
new_confirmed_by_prov = last2days_confirmed[[large_city]].iloc[:, -1].values[-1] - \
                        last2days_confirmed[[large_city]].iloc[:, -1].values[0]
new_deaths_by_prov = last2days_deaths[[large_city]].iloc[:, -1].values[-1] - \
                    last2days_deaths[[large_city]].iloc[:, -1].values[0]

copyright = html.Footer([
                html.Div(dbc.Row(["本程序由叶问创建"], justify='end'), 
                        id='footer-text', 
                        style={'margin-right': '10px', 'color': '#808080', 'font-family': 'KaiTi'}),
            ])
alert = dbc.Toast(
    dbc.Alert([
        "本程序仅用于演示目的，所有数据均来源于约翰霍普金斯大学。点击进入",
        html.A("这里", href="https://github.com/CSSEGISandData/COVID-19", target="_blank"),
        "查看疫情数据，点击进入",
        html.A("这里", href="https://github.com/govex/COVID-19", target="_blank"),
        "查看疫苗接种数据，其中上海疫情数据经过",
        html.A("维基中文百科", href="", target="_blank"),
        "修正。查看官方疫情数据点击进入",
        html.A("国家卫生健康委员会的疫情通报", href="http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml", target="_blank"),
        "。如果研究数据与官方数据存在差异，请以官方数据为准。"
    ], color="warning"),
    header="声明",
    icon="warning")
alert = dbc.Alert([
        "声明：本程序仅用于演示目的，所有数据均来源于约翰霍普金斯大学。点击进入",
        html.A("这里", href="https://github.com/CSSEGISandData/COVID-19", target="_blank"),
        "查看疫情数据，点击进入",
        html.A("这里", href="https://github.com/govex/COVID-19", target="_blank"),
        "查看疫苗接种数据。查看官方疫情数据点击进入",
        html.A("国家卫生健康委员会的疫情通报", href="http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml", target="_blank"),
        "。如果研究数据与官方数据存在差异，请以官方数据为准。"
    ], color="warning", style={'font-size': 12})


# app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], update_title='更新中...')

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([], 
                width={"size": 1, "order": 1, "offset": 3}),
        dbc.Col([html.Br(), html.H2("全国新冠疫情概要")], 
                width={"size": 4, "order": 2, "offset": 0},
                ),
        dbc.Col(alert, width={"size": 4, "order": 'last', "offset": 0},
                )
        ]),
    dbc.Row([
        dbc.Col(html.Div("数据发布日期：{}".format(publish_date), 
                        style={'color': 'white', 'font-size': 14}),
                        width={"size": 3, "order": 1, "offset": 0}, 
                        style={'margin-left': '32px'}), 
        dbc.Col(html.Div("最近下载数据时间：{}".format(update_time), 
                        style={'color': 'gray', 'font-size': 12}),
                        width={"size": 3, "order": "last", "offset": 5},
                        style={'margin-left': '595px'}), 
        ]),
    dbc.Row([
        new_confirmed_card,
        new_death_card,
        new1_parvcc_card,
        new1_fulvcc_card
    ], justify='center'),
    dbc.Row([
        new28_confirmed_card,
        new28_deaths_card,
        new28_parvcc_card,
        new28_fulvcc_card
    ], justify='center'),
    dbc.Row([
        all_confirmed_card,
        all_deaths_card,
        all_parvcc_card,
        all_fulvcc_card
    ], justify='center'),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(past28_new_confirmed.columns, past28_new_confirmed.columns[0], 
                        id='dropdown', placeholder="选择城市", style={'color': 'black'}),
            html.Br(),
            html.H6("{}".format(publish_date), style={"text-align": "center"}),
            html.Br(),
            html.H6("昨日新增感染", style={"text-align": "center", 'color': 'gold'}),
            html.H6(new_confirmed_by_prov,
                    style={"text-align": "center", 'color': 'gold'}, id="new_confirmed_value"),
            html.Br(),
            html.H6("昨日新增死亡", style={"text-align": "center", 'color': 'red'}),
            html.H6(new_deaths_by_prov, 
                    style={"text-align": "center", 'color': 'red'}, id="new_deaths_value"),
        ], width=2, style={'margin-left': '20px'}),
        dbc.Col([
            # html.H5("{}全部病例".format("香港"), style={"text-align": "center"}),
            dcc.Graph(id="pie-graph", figure=pie_fig, config=config)
        ]),
        dbc.Col([
            # html.H5("过去28天{}感染病例".format("香港"), style={"text-align": "center"}),
            dcc.Graph("ts-graph", figure=ts_fig, config=config)
        ], style={'margin-right': '20px'})
    ], justify='center'),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
            dbc.Tab(new_confirmed_map_data, label="昨日新增感染病例分布", 
                    active_label_style={"color": "gold"}),
            dbc.Tab(last28_confirmed_map_data, label="过去28天累计新增感染病例分布",
                    active_label_style={"color": "gold"}, activeTabClassName="fw-bold fst-italic"),
            dbc.Tab(all_confirmed_map_data, label="全部累计感染病例分布",
                    active_label_style={"color": "gold"}, activeTabClassName="fw-bold fst-italic")
            ])
        ], width=10)
    ], justify='center'),
], fluid=True)

# @app.callback(
#     Output('output', 'children'),
#     [Input('echarts', 'click_data')])
# def update(data):
#     if data:
#         return f"clicked: {data['name']}"
#     return 'not clicked!'

# @callback(
#     [Output('new_confirmed_value', 'children'),
#     Output('new_deaths_value', 'children')],
#     Input('dropdown', 'value')
# )
def update_output(value):
    new_confirmed_by_prov = last2days_confirmed[[value]].iloc[:, -1].values[-1] - \
                        last2days_confirmed[[value]].iloc[:, -1].values[0]
    new_deaths_by_prov = last2days_deaths[[value]].iloc[:, -1].values[-1] - \
                        last2days_deaths[[value]].iloc[:, -1].values[0]
    return new_confirmed_by_prov, new_deaths_by_prov

# @callback(
#     Output('pie-graph', 'figure'),
#     Input('dropdown', 'value')
# )
def update_pie_graph(value):
    pie_title = "{}全部累计病例".format(value)
    all_confirmed_by_prov = last2days_confirmed[[value]].iloc[-1, :].values[-1]
    all_deaths_by_prov = last2days_deaths[[value]].iloc[-1, :].values[-1]
    pie_fig = plot_pie(all_confirmed_by_prov, all_deaths_by_prov, pie_title)
    return pie_fig

# @callback(
#     Output('ts-graph', 'figure'),
#     Input('dropdown', 'value')
# )
def update_ts_graph(value):
    past28_new_confirmed = confirmed - confirmed.shift(1, fill_value=0)
    past28_new_confirmed = past28_new_confirmed.iloc[1:, :]
    last_row = past28_new_confirmed.iloc[-1, :]
    sorted_columns = past28_new_confirmed.columns[np.argsort(last_row.values)[::-1]]
    past28_new_confirmed = past28_new_confirmed[sorted_columns]
    ts_title = "过去28天{}每日新增感染人数".format(value)
    ts_fig = plot_time_series(past28_new_confirmed[[value]], ts_title)
    return ts_fig


def init_callbacks(app):
    app.callback(
        [Output('new_confirmed_value', 'children'), Output('new_deaths_value', 'children')],
        Input('dropdown', 'value'))(
            update_output
        )
    app.callback(
        Output('pie-graph', 'figure'),
        Input('dropdown', 'value'))(
            update_pie_graph
        )
    app.callback(
        Output('ts-graph', 'figure'),
        Input('dropdown', 'value'))(
            update_ts_graph
        )

if __name__ == '__main__':
    app.run_server(debug=False, port=8518)
