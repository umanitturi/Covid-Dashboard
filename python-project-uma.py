import streamlit as st              # used for webapp creation
import pandas as pd                 # used for data wrangling
from urllib.error import HTTPError  # used to handly http errors
import matplotlib.pyplot as plt     # used to modify plot/graphs
import numpy as np                  # working with arrays and martices (need for some pandas stuff)
import plotly.express as px         # for plotting
import pycountry                    # used to associate country names to iso abbreviations
import datetime as dt               # working with dates
import json                         # loading/saving JSON files
import os.path                      # working with local filepaths
import copy                         # for creating deep copies

# run this script with "streamlit run python-project-uma.py" in e.g. anaconda prompt


#*############################ Functions ################################

def up_to_date(verbose = False):
    """Checks, if the covid-19 data are up to date.

    Args:
        verbose (bool, optional): Flag if the last update date should be printed. Defaults to False.

    Returns:
        bool: returns if data is up to date
    """
    try:
        with open(f"last_updated.dat", "r") as f:
            today = dt.datetime.today().strftime('%d.%m.%Y')
            last_update = f.read().strip()
            if verbose:
                st.text(f"Last updated: {last_update}.")
            return today == last_update
    except:
        return False


def change_last_update():
    """Change covid-19 data update status

    """
    with open(f"last_updated.dat", "w") as f:
        f.write(dt.datetime.today().strftime("%d.%m.%Y"))


def save_iso_dict(iso_dict):
    """Save country iso code dictionary as a JSON file.

    Args:
        iso_dict (dictionary): iso code dictionary to save
    """
    with open("iso_dict.json", "w") as f:
        json.dump(iso_dict, f)


def load_iso_dict():
    """Load country iso code from JSON file into dictionary.

    Returns:
        dictionary: contains iso code dictionary
    """
    with open("iso_dict.json", "r") as f:
        return json.load(f)


def check_for_iso_dict():
    """Checks if iso code JSON file exists.

    Returns:
        bool: True, if iso code JSON file exists
    """
    return os.path.isfile("iso_dict.json")


def get_iso_a3(country):
    """Get three letter iso code for given country.

    Args:
        country (string): country name

    Returns:
        string: country three letter iso code
    """
    try:
        result = pycountry.countries.search_fuzzy(country)
        return result[0].alpha_3
    except:
        return np.nan
    
def get_label(data_option, data_selection):
    """Translate data option and selection into a string

    Args:
        data_option (string): string with the data options
        data_selection (string): string with the data selection

    Returns:
        string: label for plotting etc.
    """
    if data_selection in ["confirmed", "recovered"]:
        return f"{data_option.title()} {data_selection} cases"
    else:
        return f"{data_option.title()} {data_selection}"

def get_color_scale_list():
    """Get list of available color scales

    Returns:
        list: list of available color scales
    """
    return ["reds",
            "ylorrd",
            "bluered"]

def get_color_scale_label(color_scale):
    """Generate color scale label from color scale string

    Args:
        color_scale (string): color scale string representation

    Returns:
        string: label for the color scale
    """
    return {
        "reds": "reds",
        "ylorrd": "yellow to red",
        "bluered": "blue to red"
    }.get(color_scale)

def get_date_string(date):
    """Convert numpy.datetime64 to a string containing only the date (DD.MM.YYYY)

    Args:
        date (numpy.datetime64): the date to convert

    Returns:
        string: date string in the format DD.MM.YYYY
    """
    return pd.to_datetime(str(date)).strftime("%d.%m.%Y")

def print_statistics(df, ):
    current_active = int(df.daily_active.values[-1])
    new_cases = int(df.daily_confirmed.values[-1])
    new_deaths = int(df.daily_deaths.values[-1])
    total_cases = df.total_confirmed.values[-1]
    total_deaths = df.total_deaths.values[-1]
    
    week_change_cases = (new_cases - df.daily_confirmed.values[-8]) / new_cases * 100
    week_change_deaths = (new_deaths - df.daily_deaths.values[-8])/ new_deaths * 100
    
    twoweek_change_cases = (new_cases - df.daily_confirmed.values[-15]) / new_cases * 100
    twoweek_change_deaths = (new_deaths - df.daily_deaths.values[-15]) / new_deaths * 100
    
    stats_col1, stats_col2 = st.beta_columns(2)

    with stats_col1:
        st.markdown("Cases\n----------")
        st.markdown(f"Active: {current_active:}")
        st.markdown(f"New: {new_cases}")
        st.markdown(f"Total: {total_cases}")
        st.markdown(f"7-day change: {week_change_cases:.2g}%")
        st.markdown(f"14-day change: {twoweek_change_cases:.2g}%")

    with stats_col2:
        st.markdown(f"Deaths\n----------")
        st.markdown(f"New: {new_deaths}")
        st.markdown(f"Total: {total_deaths}")
        st.markdown(f"7-day change: {week_change_deaths:.2g}%")
        st.markdown(f"14-day change: {twoweek_change_deaths:.2g}%")

@st.cache(suppress_st_warning=True) # chache this function to speed up webapp
def load_data():
    """Update world covid-19 data from github repository, if necesseary,
    otherwise load data from file. 

    Returns:
        dataframe, dataframe, dataframe: confirmed, deaths and recovered covid data
    """
    # URLs to load data from
    url_global_confirmed = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    url_global_deaths = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
    url_global_recovered = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
    
    # if the data are up to date
    if up_to_date():
        # load data from files
        st.text("Already updated today. Loading data from files.")
        df_global_confirmed = pd.read_csv("data/covid_world_confirmed.csv")
        df_global_deaths = pd.read_csv("data/covid_world_deaths.csv")
        df_global_recovered = pd.read_csv("data/covid_world_recovered.csv")
    else: # otherwise load data from github
        st.text("Loading data from URL.")
        try:
            df_global_confirmed = pd.read_csv(url_global_confirmed)
            df_global_deaths = pd.read_csv(url_global_deaths)
            df_global_recovered = pd.read_csv(url_global_recovered)
        except HTTPError: # if there is no connection, read data from file
            st.error("Live data not available. Loading locally saved data.")
            df_global_confirmed = pd.read_csv("data/covid_world_confirmed.csv")
            df_global_deaths = pd.read_csv("data/covid_world_deaths.csv")
            df_global_recovered = pd.read_csv("data/covid_world_recovered.csv")
        else: # if data were successfully loaded, save them into files
            df_global_confirmed.to_csv("data/covid_world_confirmed.csv", index=False)
            df_global_deaths.to_csv("data/covid_world_deaths.csv", index=False)
            df_global_recovered.to_csv("data/covid_world_recovered.csv", index=False)

            # change date of last update
            change_last_update()

    return df_global_confirmed, df_global_deaths, df_global_recovered

@st.cache(suppress_st_warning=True)

def load_world_data():
    """Load world covid data and transform data for use and return the
    resulting dataframe.

    Returns:
        dataframe: dataframe with the complete covid-19 data
    """
    # update and load data
    df_global_confirmed, df_global_deaths, df_global_recovered = copy.deepcopy(load_data())

    # melt from wide to long format
    df_global_confirmed_melt = df_global_confirmed.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long']).rename(columns={"variable": "date", "value": "confirmed"})
    df_global_deaths_melt = df_global_deaths.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long']).rename(columns={"variable": "date", "value": "deaths"})
    df_global_recovered_melt = df_global_recovered.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long']).rename(columns={"variable": "date", "value": "recovered"})

    # merge the three dataframes into one
    #! MAYBE CHANGE LEFT TO OUTER !#
    df_global_merge1 = pd.merge(df_global_confirmed_melt, 
                                df_global_deaths_melt, 
                                how="left", 
                                on=['Province/State', 'Country/Region', 'Lat', 'Long', 'date'])
    df_global = pd.merge(df_global_merge1, 
                         df_global_recovered_melt, 
                         how="left", 
                         on=['Province/State', 'Country/Region', 'Lat', 'Long', 'date'])

    # rename columns and set data as a date
    df_global.rename(columns={"Province/State": "province", "Country/Region": "country", "Lat": "lat", "Long": "long"}, inplace=True)
    df_global["date"] = pd.to_datetime(df_global["date"])

    #! take original data and omit all provinces, !#
    #! then merge lat and long into df_global_agg !#
    df_global_agg=df_global.groupby(['country', 'date']).agg({'lat': 'mean', 'long': 'mean', 'confirmed': 'sum', 'deaths': 'sum', 'recovered': 'sum'}).reset_index()

    # sort dataframe by country and date
    df_global_agg.sort_values(by=["country", "date"], axis=0, ignore_index=True, inplace=True)
    
    # rename accumulated cases etc.
    df_global_agg.rename(columns={"confirmed": "total_confirmed", 
                              "deaths": "total_deaths",
                              "recovered": "total_recovered"},
                        inplace=True)
    
    # calculate daily cases/deaths/recovered
    df_global_agg["daily_confirmed"] = df_global_agg.total_confirmed.diff()
    df_global_agg["daily_deaths"] = df_global_agg.total_deaths.diff()
    df_global_agg["daily_recovered"] = df_global_agg.total_recovered.diff()

    df_global_agg.fillna(0, inplace=True)
    df_global_agg.loc[df_global_agg["daily_confirmed"] < 0, "daily_confirmed"] = 0
    df_global_agg.loc[df_global_agg["daily_deaths"] < 0, "daily_deaths"] = 0
    df_global_agg.loc[df_global_agg["daily_recovered"] < 0, "daily_recovered"] = 0
    
    # calculate active cases
    df_global_agg["daily_active"] = df_global_agg.total_confirmed \
                                    - df_global_agg.total_recovered \
                                    - df_global_agg.total_deaths
                                    
    return df_global_agg


#*############################ WebApp ###################################

st.title("Covid-19 Dashboard")

up_to_date(verbose = True)

# General options for displaying the data
# show available plot type options
plot_option = st.sidebar.radio(label="Plot type",
                               options=["Time Series"
                                        
                                        ])

# show available region type options
country_option = st.sidebar.radio(label="Region",
                                  options=["World"
                                          ])

# load required dataset
if country_option == "World":
    df = copy.deepcopy(load_world_data())
    regions = df.country.unique()
else:
    st.sidebar.error(f"Sorry, {country_option} is not available at the moment.")



#*############################ Time Series ##############################
if plot_option == "Time Series":
    
    # if world is selected
    if country_option == "World":
        # get index of germany in region list to set default region
        reg_index = int(np.where(regions == "Germany")[0][0])
    else:
        # otherwise set default index to 0
        reg_index = 0

    # create columns to insert selectboxes into
    col1, col2, col3 = st.beta_columns(3)

    # show all available regions to select
    with col1:
        region = st.selectbox("Choose a region", regions, index=reg_index)

    # select one of the data options
    with col2:
        data_option = st.selectbox("Choose data options",
                                    ["total",
                                    "daily",
                                    "weekly"])
    
    # select one of the available data
    available_data_selection =  ["confirmed", "deaths", "recovered"]
    if data_option == "daily":                      # active cases are only available daily
        available_data_selection.append("active")
    elif data_option == "weekly":                   # all data are only available weekly
        available_data_selection.append("all")      # otherwise the data amount is too large
    with col3:
        data_selection = st.selectbox("Choose data to plot",
                                available_data_selection)

    # if world is chosen
    if country_option == "World":
        region_column = "country"  # select country for world data
    elif country_option == "China":
        region_column = "province" # select province for china data

    # if weekly is chosen, create new dataframe by resampling into weeks
    if data_option == "weekly":
        df_weekly = df[df[region_column] == region].resample("W", on='date').sum()
        # if all is chosen, plot all three data columns
        if data_selection == "all":
            fig = px.line(df_weekly, 
                    y=['daily_confirmed', 
                        'daily_deaths', 
                        'daily_recovered'])
        else:
            fig = px.line(df_weekly, 
                    y=f"daily_{data_selection}")
    # else plot dataframe as is
    else: 
        fig = px.line(df[df[region_column] == region], 
                    x='date', 
                    y=f"{data_option}_{data_selection}")

    fig.update_layout(title_text = get_label(data_option, data_selection),
                    xaxis_title = "Date",
                    yaxis_title = get_label(data_option, data_selection))

    # show time series plot
    st.plotly_chart(fig)

    print_statistics(df[df[region_column] == region])

    
    
# add author info
st.sidebar.info("Designed and programmed by: Uma Nitturi \
                \n\nJanuary 2021")