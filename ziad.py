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
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

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
lottie_ml = load_lottieurl("https://assets7.lottiefiles.com/packages/lf20_q5qeoo3q.json")

# Load css library
remote_css("https://unpkg.com/tachyons@4.12.0/css/tachyons.min.css")
# Load css style
local_css('style.css')

menu_data = [
    {'label': "Overview", 'icon': 'bi bi-bar-chart-line'},
    {'label':"EDA", 'icon': "bi bi-graph-up-arrow"},
    {'label': 'Tableau', 'icon': 'bi bi-clipboard-data'},
    {'label':"Application", 'icon':'fa fa-brain'}]

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
df['FINAL_CONS'] = df['FINAL_CONS'].str.strip()
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
    df1 = df.drop(['FID','ParcelID','PID','F__id','Source','ObjectID'],axis=1)
    

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
          making sense of data in hand, before diving deep into it.
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

    bar_lengths = df['Type_of_St'].value_counts()

    # Sort the bar lengths in descending order
    bar_lengths = bar_lengths.sort_values(ascending=True)

    # Define a custom color scale with darker blue for the longest bar and lighter blue for the others
    max_length = bar_lengths.max()
    colors = [f'rgba(64, 114, 255, {0.5 + 0.5 * (length / max_length)})' for length in bar_lengths]

    # Create a horizontal bar chart with custom colors
    fig1 = px.bar(x=bar_lengths.values, y=bar_lengths.index, orientation='h',
              color=bar_lengths.values, color_continuous_scale=colors,
              labels={'x':'Frequency', 'y':'Type of Structure'},
              title='Frequency of Each Type of Structure')

    fig1.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, showlegend=False)
    fig1.update_traces(text=bar_lengths.values, textposition='outside')
    fig1.update_layout(xaxis_showticklabels=False, showlegend=False, xaxis_visible=False)

    # Get the count of each category
    count_data = df['FINAL_CLAS'].value_counts().reset_index()
    count_data.columns = ['FINAL_CLAS', 'count']

    # Find the index of the row with the highest count
    max_count_index = count_data['count'].idxmax()

    # Create a list of colors where the color for the highest count bar is different
    colors = ['rgba(64, 114, 255, 0.5)' if i != max_count_index else 'rgba(255, 0, 0, 0.5)' for i in range(len(count_data))]

    # Create a bar chart to visualize the distribution of final damage classifications
    fig2 = px.bar(count_data, x='FINAL_CLAS', y='count', title='Distribution of Final Damage Classifications',
              category_orders={'FINAL_CLAS': ['D0', 'D1', 'D2', 'D3', 'D4', 'D5']},
              labels={'FINAL_CLAS': 'Final Classification', 'count': 'Count'},
              color=count_data['FINAL_CLAS'], color_discrete_sequence=colors)

    # Update layout to hide y-axis and place numbers outside of the bars
    fig2.update_layout(showlegend=False)
    fig2.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)

    # Create a histogram with Plotly
    fig3 = px.histogram(df, x='FINAL_CLAS', color='DIRECT_LIN', barmode='group',
                    title='Histogram of Final Damage Classification with Direct Line of Sight',
                    labels={'FINAL_CLAS': 'Final Classification'})
    fig3.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)

    # Create a scatter plot of Shape_Leng vs. Shape_Area
    fig4 = px.scatter(df, x='Shape_Leng', y='Shape_Area', title='Scatter Plot of Building Lenght vs. Building Area')
    fig4.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)

    # Use streamlit columns for layout
    co1, co2 = st.columns(2)

    # Display charts in columns
    with co1:
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)

    with co2:
        st.plotly_chart(fig3, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)

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

# Predication Application Page

if menu_id == "Application":

    col = st.columns(2)

    # Article
    with col[0]:
        st.markdown("""
        <h3 class="f2 f1-m f-headline-l measure-narrow lh-title mv0">
        Know The Risk of Damage
         </h3>
         <p class="f5 f4-ns lh-copy measure mb4" style="text-align: justify;font-family: Sans Serif">
         Now, it's time to Predict whether any existing or upcoming Building has a risk to be damaged.
         Fill out the building's features and information to see the result.
         </p>
            """,unsafe_allow_html = True)

    # Lottie Animation
    with col[1]:
        st_lottie(lottie_ml, key = "Machine Learning", height = 300, width = 800)
    # Create a list of columns to keep
    columns_to_keep = ["FINAL_CLAS", "NoofFloor", "Type_of_St", "DISTANCE_F", "FINAL_CONS", "Shape_Leng", "Shape_Area", "DIRECT_LIN"]
    # differentiate only between not impacted and impacted regardless of the degree of destruction
    df['FINAL_CLAS'].replace(['D2', 'D3', 'D4', 'D5'], "D1", inplace=True)
    #df['FINAL_CLAS'].replace(['D0'], 0, inplace=True)
    # Keep only the specified columns
    df = df[columns_to_keep]
    # Split the data into features (X) and the target variable (y)
    X = df.drop('FINAL_CLAS', axis=1)  # Features
    y = df['FINAL_CLAS']  # Target variable

    # Encode categorical variables using Label Encoding
    label_encoders = {}
    categorical_columns = ['Type_of_St','FINAL_CONS']
    for col in categorical_columns:
        label_encoders[col] = LabelEncoder()
        X[col] = label_encoders[col].fit_transform(X[col])

    # Split the data into training and testing sets (e.g., 80% training, 20% testing)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train a Random Forest Classifier (you can choose a different classifier)
    classifier = RandomForestClassifier(random_state=42)
    classifier.fit(X_train, y_train)

    def user_report():

        # Building information input
        st.title('Building Information Input')
        cols2 = st.columns(4)

        with cols2[0]:
            num_floor = st.number_input("Number of Floors",value = 5, min_value = 0)


        with cols2[1]:
            type_structure = st.selectbox("Type of Structure",("RC","SM","Steel","RC+SM (EVOLVED)", "RC+Steel"))

        with cols2[2]:
            distance_from = st.number_input("Distance from Beirut Explosion",value = 100, min_value = 0)

        with cols2[3]:
            finl_con = st.selectbox("Final Year of Construction", ("Pre1935", "1935-1955", "1956-1971", "1972-1990", "Post1990"))

        cols3 = st.columns(3)

        with cols3[1]:
            shape_area = st.number_input("Shape Area",value = 35, min_value = 0)

        with cols3[0]:
            shape_length = st.number_input("Shape Lenght",value = 35, min_value = 0)
        
        with cols3[2]:
            ditrct_line = st.selectbox("Direct Line of Sight to Port Explosion",(0,1))
        
        user_report_data = {
        'NoofFloor': num_floor,
        'Type_of_St': type_structure,
        'DISTANCE_F': distance_from,
        'FINAL_CONS': finl_con,
        'Shape_Leng': shape_length,
        'Shape_Area': shape_area,
        'DIRECT_LIN' : ditrct_line,
        }
        report_data =pd.DataFrame(user_report_data, index = [0])
        return report_data
    
    user_data = user_report()
    st.write("")
    st.write("")
    st.write("")
    #Button style
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
    predict = st.button('Predict')
    # Show the Outcome of the Model
    if predict:
        st.header('Data Input by User')
        st.table(user_data)
        categorical_columns_user = ['Type_of_St','FINAL_CONS']
        for col in categorical_columns_user:
            label_encoders[col] = LabelEncoder()
            user_data[col] = label_encoders[col].fit_transform(user_data[col])
        # Predict the result
        prediction = classifier.predict(user_data)
        st.subheader('The Building is more likely to: ')
        if prediction == "D0":
            st.subheader("not to be impacted or damaged")
        else:
            st.subheader("to be impacted or damaged")


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

