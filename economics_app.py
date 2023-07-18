# import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from dotenv import load_dotenv # pip install python-dotenv. This takes environment variables from .env
from fredapi import Fred
import streamlit as st
import os

# --- Hide Streamlit Style ---
hide_st_style = """
                <style>
                #MainMenu {Visibility: hidden;}
                footer {Visibility: hidden;}
                header {Visibility: hidden;}
                </style>
"""

plt.style.use('fivethirtyeight')
page_title = "Economic Data Analysis FRED data"
layout = "centered"

def main():
    st.set_page_config(page_title = page_title, layout = layout)
    st.title(page_title)

if __name__ == '__main__':
    main()

# --- Hide Streamlit Style ---
hide_st_style = """
                <style>
                #MainMenu {Visibility: hidden;}
                footer {Visibility: hidden;}
                header {Visibility: hidden;}
                </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

color_pal = plt.rcParams["axes.prop_cycle"].by_key()["color"] 

# Load the FRED API KEY from the environment variables
def configure():
    load_dotenv()

configure()
FRED_KEY = os.getenv('FRED_KEY')

# Initialize with a FRED API key
fred_key = FRED_KEY

# Creation the fred object
fred = Fred(api_key=fred_key)

# Search for economic data
sp_search = fred.search('S&P', order_by='popularity')


# Function to plot horziontal bar chart
# Function takes as inpur the x, y and title values
def barchart_layout(x, y, xtitle, title):
    fig = go.Figure(go.Bar(
        x = x,
        y = y,               
        marker=dict(
            color='rgba(50, 171, 96, 0.6)',
            line=dict(
                color='rgba(50, 171, 96, 1.0)',
                width=1),
        ),
        orientation='h' ))
    
    fig.update_layout(
    autosize=False,
    title = title,
    title_x=0.3,
    xaxis_title = xtitle,
    width=600,
    height=1000    
    )
    return fig

# Format line chart with x, y axis lables and lable title
def formatline_chart(x, y, plottitle, legendtitle, df_current):
    fig = px.line(df_current) 
    fig.update_layout(
    title=plottitle,
    title_x=0.3,
    xaxis_title=x,
    yaxis_title=y,
    legend_title=legendtitle,
    autosize=False,
    width=500,
    height=700 )
    return fig 

# Pull raw data and plot
def sp500chart():
    sp500 = fred.get_series(series_id='SP500')
    # create a dict from series data and pass this as the data param to the dataframe constructor
    sp500_df = pd.DataFrame({'Period':sp500.index, 'Points':sp500.values})
    st.write('S&P 500 points over a period')
    st.write(sp500_df)
    fig = px.line(sp500_df, x="Period", y="Points", title='S&P 500')
    # df_current = sp500_df.copy()
    # df_current.set_index('Period')
    # st.write(df_current)
    x="Period"
    y="Points"
    plottitle='S&P 500 by period'
    legendtitle ="S&P 500 by period"
    fig.update_layout(
    title=plottitle,
    title_x=0.5,
    xaxis_title=x,
    yaxis_title=y,
    autosize=True,
    )
    st.plotly_chart(fig, use_container_width=True)

# Unemployment data
def unemp():
    fred.search('unemployment',order_by='popularity')
    unrate = fred.get_series('UNRATE')
    unemp_df = fred.search('unemployment state', filter =('frequency','Monthly'))
    unemp_df = unemp_df.query('seasonal_adjustment == "Seasonally Adjusted" and units == "Percent"')
    unemp_df = unemp_df.loc[unemp_df['title'].str.contains('Unemployment Rate')]
    
    all_results = []
    for stateid in unemp_df.index:
        if len(stateid) == 4:
            results = fred.get_series(stateid)
            results = results.to_frame(name=stateid)              
            all_results.append(results) 

    unemp_results = pd.concat(all_results, axis=1)

    unemp_states = unemp_results.dropna()
    st.write('Unemployment rates by states dataframe')
    unemp_states    
    id_to_state = unemp_df['title'].str.replace('Unemployment Rate in', '').to_dict()
    unemp_states.columns = [id_to_state[c] for c in unemp_states.columns]
    df_current = unemp_states.copy()
    #fig = px.line(unemp_states)
    plottitle="Unemployment rate by state"
    x = "Period (year)"
    y = "Unemployment rate (%)"
    legendtitle ="State"
    
    fig = formatline_chart(x, y, plottitle, legendtitle, df_current)
    st.write(unemp_states)   
    st.plotly_chart(fig, use_container_width=True)
    
    return unemp_states

# Unemployement by states for a given date
def unempstates(unemp_states):
    # print("Enter unempstates")
    # st.write("Enter unempstates")
    ax = unemp_states.loc[unemp_states.index == '2020-05-01'].T  \
    .sort_values('2020-05-01')
    ax['State'] = ax.index
    # Change value of a cell from the District of Columbia to DC
    ax.at[' the District of Columbia','State']='DC'
    # Renaming columns of the dataframe
    ax.columns = ['Unemployment rate', 'State']
    ax
    x = ax['Unemployment rate']
    y = ax['State']    
    xtitle = "Unemployment rate (%)"
    #ytitle = "State"
    title = 'Unemployment rate by states for 2020-05-01'
    
    st.write(' ')
    # Plottting a horizontal bar char with plotly indicating the unemployment rate by state
    fig = barchart_layout(x, y, xtitle, title)     
    st.plotly_chart(fig, use_container_width=True)


# Employee participation rate data
def particip():
    part_df = fred.search('participation rate state', filter =('frequency','Monthly'))
    part_df = part_df.query('seasonal_adjustment == "Seasonally Adjusted" and units == "Percent"')
    part_id_to_state = part_df['title'].str.replace('Labor Force Participation Rate for', '').to_dict()
    #part_df.shape
    all_results_part = []
    #part_df
    for id in part_df.index:
        if len(id) == 7:
            results = fred.get_series(id)
            results = results.to_frame(name=id)   
            all_results_part.append(results) 
        
    part_results = pd.concat(all_results_part, axis=1)    
    
    part_states = part_results.dropna()
    part_states.columns = [part_id_to_state[c] for c in part_states.columns]
    
    part_states
    df_current = part_states.copy()
    # plotting employee participation rate by states
    #figline = px.line(part_states)
    plottitle="Participation rate by state"
    x = "Period (year)"
    y = "Participation rate (%)"
    legendtitle ="State"
    
    fig = formatline_chart(x, y, plottitle, legendtitle, df_current)
       
    st.plotly_chart(fig, use_container_width=True)
    st.write('Employee participation rates by states dataframe')
    part_states 
       
    return part_states

# Employee participation rate by states for a given date
def participstates(part_states):
    part_ax = part_states.loc[part_states.index == '2020-05-01'].T \
    .sort_values('2020-05-01')
    part_ax['State'] = part_ax.index
    # Change value of a cell from the District of Columbia to DC
    part_ax.at[' the District of Columbia','State']='DC'
    # Renaming columns of the dataframe
    part_ax.columns = ['Employee participation rate', 'State']
    part_ax
    x = part_ax['Employee participation rate']
    y = part_ax['State']
    xtitle = "Participation rate (%)"
    #ytitle = "State" 
    title="Employee participation rates by states for 2020-05-01"
    
    st.write(' ')
    # Plottting a horizontal bar char with plotly indicating the employee participation rate by state
    fig = barchart_layout(x, y, xtitle, title)
    st.plotly_chart(fig, use_container_width=True)


def unempparticip(unemp_states, part_states):
    unemp_states.rename(columns={' the District of Columbia':'District of Columbia'})
    fig, axs = plt.subplots(10, 5, figsize=(30,30), sharex=True)
    
    #fig = make_subplots(rows=10, cols=5,
     #                   shared_xaxes=True,
     #                   vertical_spacing=0.02)
    axs = axs.flatten()

    i = 0
    for state in unemp_states.columns:
        if state == 'District of Columbia' or ' Puerto Rico':
            continue
        #fig, ax = plt.subplots()
        ax2 = axs[i].twinx()
        unemp_states.query('index >= 2020 and index < 2022')[state] \
            .plot(ax=axs[i], label='Unemployment')
        part_states.query('index >= 2020 and index < 2021')[state] \
            .plot(ax=ax2, label='Participation', color=color_pal[1])
        ax2.grid(False)
        axs[i].set_title(state, fontsize=8)
        #fig.add_trace(go.Scatter(x= [1, 1.75, 2.5, 3.5], y=[axs[i], ax2]),
        #      row=1, col=1)
        i += 1

    plt.tight_layout()
    fig = plt.show()
    st.plotly_chart(fig) 

# Plot s&P 500 chart    
sp500chart()

def all_options():
    # Function call to plot unemployment rate
    unemp_states = unemp()
    unempstates(unemp_states)
        
    # Function call to plot participation rate
    part_states = particip()
    participstates(part_states) 

    # Function call to plot unemployment and participation rate by state
    #unempparticip(unemp_states, part_states)

def options_select():

    available_options = ["Unemployment rate by period", "Unemployment rate for a fixed period", \
                         "Participation rate by period", "Participation rate for a fixed period"] #, \
                        # "Unemployment vs Participation rate" ]
                        
    selectedoptions = []

    options_df = pd.DataFrame(available_options)
    options = st.sidebar.multiselect('Select options', options_df)

    pick_all_options = st.sidebar.checkbox(' All options')
    option_selected = False
    
    if not pick_all_options:
        for option in options:
            selectedoptions.append(option)
            option_selected = True
    
    else:
        all_options()

    # st.write(selectedoptions)
    # # print(type(selectedoptions))
    # st.write(available_options[1:2])
    # st.write(available_options[3:4])
    # print(type(available_options[1:2]))
    if (available_options[0:1] == selectedoptions) or ((available_options[0:2]) == selectedoptions):
        unemp_states = unemp()
        if (available_options[0:2]) == selectedoptions:
            unempstates(unemp_states)

    elif (available_options[1:2] == selectedoptions):
        #st.write(f'{available_options[1]}  cannot be chosen without {available_options[0]}')
        st.error(f'{available_options[1]}  cannot be chosen without {available_options[0]}', icon="🚨")
    
    elif (available_options[2:3] == selectedoptions) or ((available_options[2:4]) == selectedoptions):
        part_states = particip()
        if (available_options[2:4]) == selectedoptions:
            participstates(part_states)
    
    elif (available_options[3:4] == selectedoptions):
        st.error(f'{available_options[3]}  cannot be chosen without {available_options[2]}', icon="🚨")

    elif (available_options[1] in selectedoptions) and (available_options[3] in selectedoptions):
        st.error(f'{available_options[1]}  cannot be chosen without {available_options[0]}', icon="🚨")
        st.error(f'{available_options[3]}  cannot be chosen without {available_options[2]}', icon="🚨")

    elif (available_options[0:4]) == selectedoptions:
        all_options()
    
    

# Call function to select options
options_select()