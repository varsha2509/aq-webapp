import json
from io import BytesIO, StringIO
import typing as ta

import folium
from folium import Marker
from folium.plugins import MarkerCluster
import geopandas as gpd
from geopy.geocoders import Nominatim
import pandas as pd
import requests
from scipy import spatial
import streamlit as st


def main() -> None:

    aq_data = load_aq_data()
    oakl_geojson = json.loads(load_oakl_data())

    configure_page_ui()

    address = st.text_input(" ", "900 Fallon St, Oakland, CA 94607")
    coordinates = convert_address(address)

    st.text("")
    display_map(coordinates, aq_data, oakl_geojson)

    display_footer()


def configure_page_ui() -> None:
    local_css("style.css")
    st.header("Predicting Air Quality in Oakland, California")
    st.text("")
    st.markdown(
        '<p class="big-font">This web-app reports annual average concentrations of Black Carbon and Nitrogen Dioxide in Oakland. Concentrations are based on a machine learning model built to make predictions at any location in Oakland using publicly available data on major sources of emissions in Oakland and neighbouring cities, number of traffic intersections, proximity to highways, and local meteorological data.</p>',
        unsafe_allow_html=True,
    )
    st.text("")
    st.markdown(
        '<p class="big-font"> <b> Enter an address below and click on the marker to know the air quality at your place of interest. </b> </p>',
        unsafe_allow_html=True,
    )


def display_footer() -> None:
    st.text("")
    tdslink = """ <a href ="https://towardsdatascience.com/hyperlocal-air-quality-prediction-using-machine-learning-ed3a661b9a71/">@Towards Data Science</a> """
    st.markdown(
        "<p> Check out this blog to learn more about how the machine learning models were developed. </p>",
        unsafe_allow_html=True,
    )
    st.markdown(tdslink, unsafe_allow_html=True)
    st.text("")
    linkedinlink = """ <a href="https://www.linkedin.com/in/varshagopalakrishnan/">@LinkedIn</a> """
    st.markdown(
        '<p class = "small-font">  Created by - Varsha Gopalakrishnan </p>',
        unsafe_allow_html=True,
    )
    st.markdown(linkedinlink, unsafe_allow_html=True)


def display_map(
    point: ta.Tuple[float, float], df: pd.DataFrame, oakl_geojson: ta.Dict[str, ta.Any]
):
    m = folium.Map(point, tiles="OpenStreetMap", zoom_start=11)

    # Add polygon boundary to folium map
    folium.GeoJson(
        oakl_geojson,
        style_function=lambda x: {"color": "blue", "weight": 2.5, "fillOpacity": 0},
        name="Oakland",
    ).add_to(m)

    # Add marker for Location
    folium.Marker(
        location=point,
        popup=""" <i>BC Concentration: </i> <br> <b>{}</b> ug/m3 <br> <hr> <i>NO<sub>2</sub> Concentration: </i><b><br>{}</b> ppb <br> """.format(
            round(
                df.loc[spatial.KDTree(df[["Latitude", "Longitude"]]).query(point)[1]][
                    "BC_Predicted_XGB"
                ],
                2,
            ),
            round(
                df.loc[spatial.KDTree(df[["Latitude", "Longitude"]]).query(point)[1]][
                    "NO2_Predicted_XGB"
                ],
                2,
            ),
        ),
        icon=folium.Icon(),
    ).add_to(m)

    return st.markdown(m._repr_html_(), unsafe_allow_html=True)


def convert_address(address: str) -> ta.Tuple[float, float]:
    geolocator = Nominatim(user_agent="my_app")  # using open street map API
    geo_coordinate = geolocator.geocode(address)
    if geo_coordinate is None:
        st.error("Address not found. Please try another one.")
        st.stop()
    return geo_coordinate.latitude, geo_coordinate.longitude


@st.cache_data
# AQ concentration
def load_aq_data() -> pd.DataFrame:
    download_url = "https://drive.google.com/uc?export=download&id=1keCA9T8f_wIxjtdgjzQY9kzYX9bppCqs"
    response = requests.get(download_url)
    df = pd.read_csv(StringIO(response.text))
    return df


# oakland map geojson
def load_oakl_data() -> str:
    download_url_oakl = "https://drive.google.com/uc?export=download&id=1I008pOw0Qz0ARNVC8eBqhEt325DDU_yq"
    oakl_data = requests.get(download_url_oakl).content
    oakl_json = oakl_data.decode("utf-8")

    return oakl_json


## Adding a background to streamlit page
def local_css(file_name: str):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
