import streamlit as st
import pandas as pd 

import geopandas as gpd

import folium 
from folium import Marker
from folium.plugins import MarkerCluster

import seaborn as sns

from geopy.geocoders import Nominatim

from scipy import spatial


import requests
from io import StringIO
from io import BytesIO

# Get the data from url and request it as json file
#path = 'https://drive.google.com/uc?export=download&id='+URL.split('/')[-2]

#@st.cache(persist=True, suppress_st_warning=True)
@st.cache
def load_data():
	original_url = "https://drive.google.com/file/d/1keCA9T8f_wIxjtdgjzQY9kzYX9bppCqs/view?usp=sharing"
	file_id = original_url.split('/')[-2]
	dwn_url='https://drive.google.com/uc?export=download&id=' + file_id
	url = requests.get(dwn_url).text
	path = StringIO(url)
	df = pd.read_csv(path)
	return df


def load_oakl_data():
	original_url_oakl = "https://drive.google.com/file/d/1POYKv96TGerxDQ7n4PwRQu3DaftIf8Mf/view?usp=sharing"
	file_id_oakl = original_url_oakl.split('/')[-2]
	dwn_url_oakl = 'https://drive.google.com/uc?export=download&id=' + file_id_oakl
	url_oakl = requests.get(dwn_url_oakl).content
	path_oakl = BytesIO(url_oakl) 
	print(path_oakl)
	oakl_geo = gpd.read_file(path_oakl, driver = 'GeoJSON',encoding="utf-8")
	return oakl_geo

def convert_address(address):

	#Here we use openstreetmap's Nominatin to convert address to a latitude/longitude coordinates"
	geolocator = Nominatim(user_agent="my_app") #using open street map API 
	Geo_Coordinate = geolocator.geocode(address)
	lat = Geo_Coordinate.latitude
	lon = Geo_Coordinate.longitude
	#Convert the lat long into a list and store is as points
	point = [lat, lon]
	return point


def display_map(point, df, oakl_geo):
	m = folium.Map(point, tiles='OpenStreetMap', zoom_start=12)

	# Add polygon boundary to folium map
	folium.GeoJson(load_oakl_data, style_function = lambda x: {'color': 'black','weight': 2.5,'fillOpacity': 0},
    name='Oakland').add_to(m)


    # Add marker for Location
	folium.Marker(location=point,
    popup="""
                  <i>BC Concentration: </i> <br> <b>{}</b> ug/m3 <br> 
                  <i>NO2 Concentration: </i><b><br>{}</b> ppb <br>
                  """.format(
                    round(df.loc[spatial.KDTree(df[['Latitude', 'Longitude']]).query(point)[1]]['BC_Predicted_XGB'],2), 
                    round(df.loc[spatial.KDTree(df[['Latitude', 'Longitude']]).query(point)[1]]['NO2_Predicted_XGB'],2)),
                  icon=folium.Icon()).add_to(m)
	
	return st.markdown(m._repr_html_(), unsafe_allow_html=True)

def main():
	df_data = load_data()
	oak_data = load_oakl_data()
	st.header("Black Carbon and Nitrogen Dioxide Concentration")
	st.subheader("Oakland and San Leandro")
	address = st.text_input("Enter an address", "900 Fallon St, Oakland, CA 94607")

	# if st.checkbox("show first rows of the data & shape of the data"):
	# 	st.write(df_data.head(10))
	# 	st.write(df_data.shape)
	
	coordinates = convert_address(address)
		
	display_map(coordinates, df_data, oak_data)
  
if __name__ == "__main__":
    main()
