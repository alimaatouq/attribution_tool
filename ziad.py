import json
from datetime import date
from urllib.request import urlopen
import time
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
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
    page_icon= "https://cdn-icons-png.flaticon.com/512/2824/2824980.png",
    layout='wide'
)


# Load css style file from local disk
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)
# Load css style from url
def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">',unsafe_allow_html = True)

# Display lottie animations
def load_lottieurl(url):

    # get the url
    r = requests.get(url)
    # if error 200 raised return Nothing
    if r.status_code !=200:
        return None
    return r.json()

# Extract Lottie Animations

lottie_eda = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_ic37y4kv.json")

# Load css library
remote_css("https://unpkg.com/tachyons@4.12.0/css/tachyons.min.css")
# Load css style
local_css('style.css')

menu_data = [
    {'label': "Overview", 'icon': 'bi bi-bar-chart-line'},
    {'label':"EDA", 'icon': "bi bi-graph-up-arrow"},
    {'label': 'Tableau', 'icon': 'bi bi-clipboard-data'},
    {'label':"Applicatiion", 'icon':'fa fa-brain'}]

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

#count damage categories
unique_categories = len(np.unique(df['FINAL_CLAS']))

#count type of structure categories
unique_categories_str = len(np.unique(df['Type_of_St']))


#Calculate the average number of floors
average_floors = df['NoofFloor'].mean()

# Round the average to the nearest integer
rounded_average_floors = round(average_floors)

# Retreive detailed report of the Exploratory Data Analysis
def profile(df):
    pr = ProfileReport(df, explorative=True)
    tbl = st_profile_report(pr)
    return  tbl



# EDA page

if menu_id == "EDA":

    # Drop unnecessary columns
    df1 = df.drop(['FID','ParcelID','PID','F__id','Source','ObjectID', 'FINAL_CONS'],axis=1)
    

    # 2 Column Layouts of Same Size
    col4,col5 = st.columns([1,1])

    # First Column - Shows Description of EDA
    with col4:
        st.markdown("""
        <h3 class="f2 f1-m f-headline-l measure-narrow lh-title mv0">
         Know Your Data
         </h3>
         <p class="f5 f4-ns lh-copy measure mb4" style="text-align: justify;font-family: Sans Serif">
          Before implementing your machine learning model, it is important at the initial stage to explore your data.
          It is a good practice to understand the data first and try gather as many insights from it. EDA is all about
          making sense of data in hand,before getting them dirty with it.
         </p>
            """,unsafe_allow_html = True)
        global eda_button

        # Customize Button
        button = st.markdown("""
        <style>
        div.stButton > button{
        background-color: #0178e4;
        color:#ffffff;
        box-shadow: #094c66 4px 4px 0px;
        border-radius:8px 8px 8px 8px;
        transition : transform 200ms,
        box-shadow 200ms;
        }

         div.stButton > button:focus{
        background-color: #0178e4;
        color:#ffffff;
        box-shadow: #094c66 4px 4px 0px;
        border-radius:8px 8px 8px 8px;
        transition : transform 200ms,
        box-shadow 200ms;
        }


        div.stButton > button:active {

                transform : translateY(4px) translateX(4px);
                box-shadow : #0178e4 0px 0px 0px;

            }
        </style>""", unsafe_allow_html=True)
        # Display Button
        eda_button= st.button("Explore Your Data")


    # Second Column - Display EDA Animation
    with col5:
        st_lottie(lottie_eda, key = "eda",height = 300, width = 800)

    # User Clicks on Button, then profile report of the uplaoded or existing dataframe will be displayed
    if eda_button:
        profile(df1)

# Calculate the length of each bar (frequency of each type of structure)
bar_lengths = df['Type_of_St'].value_counts()

# Sort the bar lengths in descending order
bar_lengths = bar_lengths.sort_values(ascending=True)

# Create a horizontal bar chart with the Plotly Express default color palette
fig1 = px.bar(x=bar_lengths.values, y=bar_lengths.index, orientation='h',
             labels={'x':'Frequency', 'y':'Type of Structure'},
             title='Frequency of Each Type of Structure')

# Get the count of each category for Chart 2
count_data = df['FINAL_CLAS'].value_counts().reset_index()
count_data.columns = ['FINAL_CLAS', 'count']

# Create a bar chart to visualize the distribution of final damage classifications
fig2 = px.bar(count_data, x='FINAL_CLAS', y='count', title='Distribution of Final Damage Classifications',
             category_orders={'FINAL_CLAS': ['D0', 'D1', 'D2', 'D3', 'D4', 'D5']},
             labels={'FINAL_CLAS': 'Final Classification', 'count': 'Count'})

# Create a histogram with Plotly for Chart 3
fig3 = px.histogram(df, x='FINAL_CLAS', color='DIRECT_LIN', barmode='group',
                   title='Histogram of FINAL_CLAS with DIRECT_LIN',
                   labels={'FINAL_CLAS': 'Final Classification'})

# Create a scatter plot of Shape_Leng vs. Shape_Area for Chart 4
fig4 = px.scatter(df, x='Shape_Leng', y='Shape_Area', title='Scatter Plot of Shape_Leng vs. Shape_Area')

# Create subplots
fig = make_subplots(rows=2, cols=2, subplot_titles=("Chart 1", "Chart 2", "Chart 3", "Chart 4"))

# Add traces to subplots
fig.add_trace(fig1.data[0], row=1, col=1)
fig.add_trace(fig2.data[0], row=1, col=2)
fig.add_trace(fig3.data[0], row=2, col=1)
fig.add_trace(fig4.data[0], row=2, col=2)

# Update layout
fig.update_layout(height=600, width=1000, showlegend=False)

if menu_id == "Overview":
    #can apply customisation to almost all the properties of the card, including the progress bar
    theme_buildings= {'bgcolor': '#f6f6f6','title_color': '#2A4657','content_color': '#0178e4','progress_color': '#0178e4','icon_color': '#0178e4', 'icon': 'fa fa-building'}
    theme_damage = {'bgcolor': '#f6f6f6','title_color': '#2A4657','content_color': '#0178e4','progress_color': '#0178e4','icon_color': '#0178e4', 'icon': "fas fa-house-damage"}
    theme_str = {'bgcolor': '#f6f6f6','title_color': '#2A4657','content_color': '#0178e4','progress_color': '#0178e4','icon_color': '#0178e4', 'icon': 'fas fa-gopuram'}
    theme_floors = {'bgcolor': '#f6f6f6','title_color': '#2A4657','content_color': '#0178e4','progress_color': '#0178e4','icon_color': '#0178e4', 'icon': 'fas fa-pencil-ruler'}

    # Set 4 info cards
    info = st.columns(4)

    # First KPI - Number of Buildings
    with info[0]:
        hc.info_card(title='Number of Buildings', content=df.shape[0], bar_value = (df.shape[0]/df.shape[0])*100,sentiment='good', theme_override = theme_buildings)
    # Second KPI - Number of damage categories
    with info[1]:
        hc.info_card(title='Damage Categories', content= unique_categories, bar_value = (df.shape[0]/df.shape[0])*100,sentiment='good', theme_override = theme_damage)

    # Third KPI - Number of Type of structures
    with info[2]:
        hc.info_card(title='# of Types of Structures', content=unique_categories_str, bar_value = (df.shape[0]/df.shape[0])*100,sentiment='good', theme_override = theme_str)
    # Fourth KPI - Average Tenure
    with info[3]:
        hc.info_card(title='Average # of Floors', content= rounded_average_floors, bar_value = (df.shape[0]/df.shape[0])*100,sentiment='good', theme_override = theme_floors)
    st.write(fig)
    # Center the figure or content
    st.write('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
    st.write("This is your centered figure or content")
    st.write('</div>', unsafe_allow_html=True)



if menu_id == "Tableau":
    colll1,colll2,colll3, colll4, colll5 = st.columns(5)
    coll1, coll2, coll3 = st.columns([1,10,1])
    

    
    with coll2:
        def main():

            html_temp = """
        <div class='tableauPlaceholder' id='viz1708333073814' style='position: relative'><noscript><a href='#'><img alt='Dashboard 2 (6) ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Ca&#47;CapstoneProject_17074790736670&#47;Dashboard26&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='CapstoneProject_17074790736670&#47;Dashboard26' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Ca&#47;CapstoneProject_17074790736670&#47;Dashboard26&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1708333073814');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='1300px';vizElement.style.height='4527px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
        """
        
            st.components.v1.html(html_temp,  height=1000, scrolling=True)

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

