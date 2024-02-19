import json
from datetime import date
from urllib.request import urlopen
import time

import altair as alt
import numpy as np
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
import hydralit_components as hc
from streamlit_lottie import st_lottie
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


st.set_page_config(
    page_title="Beirut Port Explosion",
    page_icon= "✅",
    layout='wide'
)


menu_data = [
    {'label': "Overview", 'icon': 'bi bi-bar-chart-line'},
    {'label': 'California', 'icon': '🇺🇸'},
    {'label': 'Vaccines', 'icon': '💉'},
    {'label': 'Health Equity', 'icon': '⚖️'},
    {'label':"Overview", 'icon':'🔍'}]

over_theme = {'txc_inactive': 'white','menu_background':'rgb(0,0,128)', 'option_active':'white'}

menu_id = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    hide_streamlit_markers=True,
    sticky_nav=True, #at the top or not
    sticky_mode='sticky', #jumpy or not-jumpy, but sticky or pinned
)



