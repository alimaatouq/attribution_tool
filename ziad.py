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
    {'label': 'Tableau'},
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

# Read the CSV file into a DataFrame
df = pd.read_csv('Cleaned_Data.csv')

# Filter out rows with negative number of floors
df = df[df['NoofFloor'] >= 0]

# Strip leading and trailing whitespaces from the "Type_of_St" column
df['Type_of_St'] = df['Type_of_St'].str.strip()


if menu_id == "Tableau":
    colll1,colll2,colll3, colll4, colll5 = st.columns(5)
    coll1, coll2, coll3 = st.columns([1,10,1])
    

    
    with coll2:
        def main():

            html_temp = """
        <div class='tableauPlaceholder' id='viz1708332791209' style='position: relative'><noscript><a href='#'><img alt='Dashboard 2 (6) ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Th&#47;TheDayLebanonChanged_17073863133250&#47;Dashboard26&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='TheDayLebanonChanged_17073863133250&#47;Dashboard26' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Th&#47;TheDayLebanonChanged_17073863133250&#47;Dashboard26&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1708332791209');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='1300px';vizElement.style.height='4527px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
        """
        
            #st.components.v1.html(html_temp, height=550, scrolling=False)

        if __name__ == "__main__":
            main()



#edit footer
page_style= """
    <style>
    footer{
        visibility: visible;
        }
    footer:after{
        content: 'Developed by Ziad Moghabghab - MSBA @ OSB - AUB';
        display:block;
        position:relative;
        color:#1e54e4;
    }
    </style>"""

st.markdown(page_style, unsafe_allow_html=True)

