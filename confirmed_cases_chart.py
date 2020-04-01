import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app import cache
from utils.settings import NCOV19_API

@cache.memoize(timeout=3600)
def confirmed_cases_chart(state='US') -> go.Figure:
    """Bar chart data for the selected state.

    :params state: get the time series data for a particular state for confirmed, deaths, and recovered. If None, the whole US.
    """

    root = 'https://covid19-us-api-staging.herokuapp.com/' # TODO change for production

    if state=='US':
        URL = root + 'country'
        payload = json.dumps({"alpha2Code": "US"})
    else:

        # TODO need to get from db when data is available
        # URL = root + 'stats'
        # payload = json.dumps({'state': state})

        ##########################################
        # Section for reading data from csv file #
        ##########################################

        codes = pd.read_csv('state-codes.csv')
        cases = pd.read_csv('time_series_covid19_confirmed_US.csv')
        deaths = pd.read_csv('time_series_covid19_deaths_US.csv')

        # look up state name from state code in codes table
        state_name = codes[codes['Two Letter String']==state].Name.iloc[0].strip()

        # get confirmed cases df
        data = cases[cases.Province_State == state_name]
        data = pd.DataFrame(data.aggregate('sum')[11:],columns=['Confirmed Cases'])

        # get death data
        deaths = deaths[deaths.Province_State == state_name]
        deaths = deaths.aggregate('sum')[12:]

        # combine
        data['Deaths'] = deaths
        data = data.reset_index()
        data.columns = ['Date', 'Confirmed Cases', 'Deaths']

        data = data.fillna(0)

        ###########################################
        #               end section               #
        ###########################################

        
    # staging API
    # URL = 'https://covid19-us-api-staging.herokuapp.com/' + "country"
    # production API
    # URL = "https://covid19-us-api.herokuapp.com/" + "country"
    # response = requests.post(URL, data=payload).json()
    # data = response["message"]
    # data = pd.DataFrame(data) # TODO remove for production
    # # data = pd.read_json(data, orient="records") # TODO uncomment for production
    # data = data.rename(columns={"Confirmed": "Confirmed Cases"})
    # data = data.tail(60)

    template_cases = "%{y} confirmed cases on %{x}<extra></extra>"
    template_deaths = "%{y} confirmed deaths on %{x}<extra></extra>"

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Confirmed Cases"],
            name="Confirmed Cases",
            line={"color": "#F4B000"},
            mode="lines",
            hovertemplate=template_cases,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Deaths"],
            name="Deaths",
            line={"color": "#870000"},
            mode="lines",
            hovertemplate=template_deaths,
        ),
    )
 

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 1},
        template="plotly_dark",
        # annotations=annotations,
        autosize=True,
        showlegend=True,
        legend_orientation="h",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        # xaxis_title="Number of Days",
        yaxis={"linecolor": "rgba(0,0,0,0)"},
        hoverlabel={"font": {"color": "black"}},
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        xaxis= {"tickformat": "%m/%y"},
        font=dict(
            family="Roboto, sans-serif",
            size=10,
            color="#f4f4f4"
        ),
        legend=dict(
                title=None, orientation="h", y=-.5, yanchor="bottom", x=0, xanchor="left"
        )
    )

    return fig

