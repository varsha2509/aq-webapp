import streamlit as st
import pandas as pd 
import geopandas as gpd

import folium 
from folium import Marker
from folium.plugins import MarkerCluster

from geopy.geocoders import Nominatim

from scipy import spatial


import requests
from io import StringIO
from io import BytesIO


import json


# Get the data from url and request it as json file

@st.cache_data
### This function reads a csv file which contains a list of concentrations by latitude and longitude
def load_data():
	original_url = "https://drive.google.com/file/d/1keCA9T8f_wIxjtdgjzQY9kzYX9bppCqs/view?usp=sharing"
	file_id = original_url.split('/')[-2]
	dwn_url='https://drive.google.com/uc?export=download&id=' + file_id
	url = requests.get(dwn_url).text
	path = StringIO(url)
	df = pd.read_csv(path)
	return df

# This function loads a geoJSON file with Oakland city boundary.
def load_oakl_data():
	original_url_oakl = "https://drive.google.com/file/d/1I008pOw0Qz0ARNVC8eBqhEt325DDU_yq/view?usp=sharing"
	file_id_oakl = original_url_oakl.split('/')[-2]
	dwn_url_oakl = 'https://drive.google.com/uc?export=download&id=' + file_id_oakl
	url_oakl = requests.get(dwn_url_oakl).content
	return url_oakl

	#path_oakl = BytesIO(url_oakl) 
	#oakl_geo = gpd.read_file(path_oakl, driver = 'GeoJSON',encoding="utf-8")


def convert_address(address):
	#Here we use Nominatin to convert address to a latitude/longitude coordinates"
	geolocator = Nominatim(user_agent="my_app") #using open street map API 
	Geo_Coordinate = geolocator.geocode(address)
	lat = Geo_Coordinate.latitude
	lon = Geo_Coordinate.longitude
	#Convert the lat long into a list and store is as point
	point = [lat, lon]
	return point


def display_map(point, df, oakl_geojson):
	m = folium.Map(point, tiles='OpenStreetMap', zoom_start=11)

	# Add polygon boundary to folium map
	folium.GeoJson(oakl_geojson, style_function = lambda x: {'color': 'blue','weight': 2.5,'fillOpacity': 0},
	name='Oakland').add_to(m)


    # Add marker for Location
	folium.Marker(location=point,
    popup="""
                  <i>BC Concentration: </i> <br> <b>{}</b> ug/m3 <br> <hr>
                  <i>NO<sub>2</sub> Concentration: </i><b><br>{}</b> ppb <br>
                  """.format(
                    round(df.loc[spatial.KDTree(df[['Latitude', 'Longitude']]).query(point)[1]]['BC_Predicted_XGB'],2), 
                    round(df.loc[spatial.KDTree(df[['Latitude', 'Longitude']]).query(point)[1]]['NO2_Predicted_XGB'],2)),
                  icon=folium.Icon()).add_to(m)
	
	return st.markdown(m._repr_html_(), unsafe_allow_html=True)

## Adding a background to streamlit page
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)



def main():
	#Load csv data
	df_data = load_data()
	
	#Load geoJSON file using json.loadas
	oakl_json = load_oakl_data()
	oakl_json = oakl_json.decode("utf-8")
	oakl_geojson = json.loads(oakl_json)

	#For the page display, create headers and subheader, and get an input address from the user
	local_css("style.css")
	st.header("Predicting Air Quality in Oakland, California")
	st.text("")
	st.markdown('<p class="big-font">This web-app reports annual average concentrations of Black Carbon and Nitrogen Dioxide in Oakland. Concentrations are based on a machine learning model built to make predictions at any location in Oakland using publicly available data on major sources of emissions in Oakland and neighbouring cities, number of traffic intersections, proximity to highways, and local meteorological data.</p>', unsafe_allow_html=True)
	st.text("")
	st.markdown('<p class="big-font"> <b> Enter an address below and click on the marker to know the air quality at your place of interest. </b> </p>', unsafe_allow_html=True)

	address = st.text_input("  ", "900 Fallon St, Oakland, CA 94607")

	# Use the convert_address function to convert address to coordinates
	coordinates = convert_address(address)
	
	#Call the display_map function by passing coordinates, dataframe and geoJSON file	
	st.text("")
	display_map(coordinates, df_data, oakl_geojson)


	st.text("")
	tdslink = """ <a href ="https://towardsdatascience.com/hyperlocal-air-quality-prediction-using-machine-learning-ed3a661b9a71/">@Towards Data Science</a> """
	st.markdown('<p> Check out this blog to learn more about how the machine learning models were developed. </p>', unsafe_allow_html = True)
	st.markdown(tdslink, unsafe_allow_html=True)
	st.text("")
	linkedinlink = """ <a href="https://www.linkedin.com/in/varshagopalakrishnan/">@LinkedIn</a> """
	st.markdown('<p class = "small-font">  Created by - Varsha Gopalakrishnan </p>', unsafe_allow_html=True)
	st.markdown(linkedinlink, unsafe_allow_html=True)

  
if __name__ == "__main__":
    main()
