from geopy.geocoders import DataBC, BANFrance, GeocodeEarth, IGNFrance, ArcGIS, Geolake,  MapTiler,  PickPoint, Photon, What3WordsV3
import requests
import geocoder
import csv


def arcgis_geocoding(placename):
    arcgis_geolocator = ArcGIS()
    arcgis_location = arcgis_geolocator.geocode(placename)
    print("\nArcGIS API:")
    arcgis_DD1 = (arcgis_location.latitude, arcgis_location.longitude)
    arcgis_CRS = "World Geodetic System 1984 (WGS84)"
    print(arcgis_location.latitude, arcgis_location.longitude)
    print("CRS：World Geodetic System 1984 (WGS84)")
    return arcgis_DD1, arcgis_CRS


def baidu_geocoding(placename, baidu_api_key):
    location = geocoder.baidu(placename, key=baidu_api_key)
    print("\nBaidu API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        baidu_DD1 = location.latlng
        baidu_CRS = "bd09II"
        print(latitude, longitude)
        print("CRS：bd09II")
        return baidu_DD1, baidu_CRS
    else:
        print("Error:", location.status)


def banfrance_geocoding(placename):
    banfrance_geolocator = BANFrance()
    banfrance_location = banfrance_geolocator.geocode(placename)
    print("\nBANFrance API:")
    banfrance_DD1 = (banfrance_location.latitude, banfrance_location.longitude)
    banfrance_CRS = "World Geodetic System 1984 (WGS84)"
    print(banfrance_location.latitude, banfrance_location.longitude)
    print("CRS：World Geodetic System 1984 (WGS84)")
    return banfrance_DD1, banfrance_CRS


def bing_geocoding(placename,bing_api_key):
    location = geocoder.bing(placename, key=bing_api_key)
    print("\nBing API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        bing_DD1 = location.latlng
        bing_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return bing_DD1, bing_CRS
    else:
        print("Error:", location.status)


def canadapost_geocoding(placename,canadapost_api_key):
    location = geocoder.canadapost(placename, key=canadapost_api_key)
    print("\nCanadaPost API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        canadapost_DD1 = location.latlng
        canadapost_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return canadapost_DD1, canadapost_CRS
    else:
        print("Error:", location.status)


def databc_geocoding(placename):
    databc_geolocator = DataBC()
    databc_location = databc_geolocator.geocode(placename)
    print("\nDataBC API:")
    databc_DD1 = (databc_location.latitude, databc_location.longitude)
    databc_CRS = "World Geodetic System 1984 (WGS84)"
    print(databc_location.latitude, databc_location.longitude)
    print("CRS：World Geodetic System 1984 (WGS84)")
    return databc_DD1, databc_CRS


def geocodeearth_geocoding(placename,geocodeearth_api_key):
    geocodeearth_geolocator = GeocodeEarth(api_key=geocodeearth_api_key)
    geocodeearth_location = geocodeearth_geolocator.geocode(placename)
    print("\nGeocodeEarth API:")
    geocodeearth_DD1 = (geocodeearth_location.latitude, geocodeearth_location.longitude)
    geocodeearth_CRS = "World Geodetic System 1984 (WGS84)"
    print(geocodeearth_location.latitude, geocodeearth_location.longitude)
    print("CRS：World Geodetic System 1984 (WGS84)")
    return geocodeearth_DD1, geocodeearth_CRS


def geocodefarm_geocoding(placename,geocodefarm_api_key):
    location = geocoder.geocodefarm(placename, key=geocodefarm_api_key)
    print("\nGeocodeFarm API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        geocodefarm_DD1 = location.latlng
        geocodefarm_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return geocodefarm_DD1, geocodefarm_CRS
    else:
        print("Error:", location.status)


def gaode_geocoding(placename,gaode_api_key):
    location = geocoder.gaode(placename, key=gaode_api_key)
    print("\nGaode API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        gaode_DD1 = location.latlng
        gaode_CRS = "GCJ-02"
        print(latitude, longitude)
        print("CRS：GCJ-02")
        return gaode_DD1, gaode_CRS
    else:
        print("Error:", location.status)


def geolake_geocoding(placename,geolake_api_key):
    geolake_geolocator = Geolake(api_key=geolake_api_key)
    geolake_location = geolake_geolocator.geocode(placename)
    print("\nGeolake API:")
    geolake_DD1 = (geolake_location.latitude, geolake_location.longitude)
    geolake_CRS = "World Geodetic System 1984 (WGS84)"
    print(geolake_location.latitude, geolake_location.longitude)
    print("CRS：World Geodetic System 1984 (WGS84)")
    return geolake_DD1, geolake_CRS


def geonames_geocoding(placename,geonames_api_key):
    location = geocoder.geonames(placename, key=geonames_api_key)
    print("\nGeoNames API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        geonames_DD1 = location.latlng
        geonames_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return geonames_DD1, geonames_CRS
    else:
        print("Error:", location.status)
    return None


def geoottawa_geocoding(placename):
    location = geocoder.ottawa(placename)
    print("\nGeoOttawa API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        geoottawa_DD1 = location.latlng
        geoottawa_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return geoottawa_DD1, geoottawa_CRS
    else:
        print("Error:", location.status)


def gisgraphy_geocoding(placename):
    location = geocoder.gisgraphy(placename)
    print("\nGisgraphy API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        gisgraphy_DD1 = location.latlng
        gisgraphy_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return gisgraphy_DD1, gisgraphy_CRS
    else:
        print("Error:", location.status)


def google_geocoding(placename):
    location = geocoder.google(placename)
    print("\nGoogle API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        google_DD1 = location.latlng
        google_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return google_DD1, google_CRS
    else:
        print("Error:", location.status)


def here_geocoding(placename,here_api_key):
    base_url = "https://geocode.search.hereapi.com/v1/geocode"
    params = {
        "q": placename,
        "apiKey": here_api_key
    }

    response = requests.get(base_url, params=params)
    print("\nHERE API:")
    if response.status_code == 200:
        data = response.json()
        if data.get('items'):
            location = data['items'][0]['position']
            latitude = location['lat']
            longitude = location['lng']
            here_DD1 = (latitude, longitude)
            here_CRS = "World Geodetic System 1984 (WGS84)"
            print(latitude, longitude)
            print("CRS：World Geodetic System 1984 (WGS84)")
            return here_DD1, here_CRS
        else:
            print("Address not found.")
    else:
        print("Error:", response.status_code)


def ignfrance_geocoding(placename):
    ignfrance_geolocator = IGNFrance()
    ignfrance_location = ignfrance_geolocator.geocode(placename)
    print("\nIGNFrance API:")
    ignfrance_DD1 = (ignfrance_location.latitude, ignfrance_location.longitude)
    ignfrance_CRS = "World Geodetic System 1984 (WGS84)"
    print(ignfrance_location.latitude, ignfrance_location.longitude)
    print("CRS：World Geodetic System 1984 (WGS84)")
    return ignfrance_DD1, ignfrance_CRS


def locationiq_geocoding(placename,locationiq_api_key):
    location = geocoder.locationiq(placename, key=locationiq_api_key)
    print("\nLocationIQ API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        locationiq_DD1 = location.latlng
        locationiq_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return locationiq_DD1, locationiq_CRS
    else:
        print("Error:", location.status)


def mapbox_geocoding(placename,mapbox_api_key):
    location = geocoder.mapbox(placename, key=mapbox_api_key)
    print("\nMapbox API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        mapbox_DD1 = location.latlng
        mapbox_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return mapbox_DD1, mapbox_CRS
    else:
        print("Error:", location.status)


def mapquest_geocoding(placename,mapquest_api_key):
    location = geocoder.mapquest(placename, key=mapquest_api_key)
    print("\nMapQuest API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        mapquest_DD1 = location.latlng
        mapquest_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return mapquest_DD1, mapquest_CRS
    else:
        print("Error:", location.status)


def maptiler_geocoding(placename,maptiler_api_key):
    maptiler_geolocator = MapTiler(api_key=maptiler_api_key)
    maptiler_location = maptiler_geolocator.geocode(placename)
    print("\nMapTiler API:")
    maptiler_DD1 = (maptiler_location.latitude, maptiler_location.longitude)
    maptiler_CRS = "World Geodetic System 1984 (WGS84)"
    print(maptiler_location.latitude, maptiler_location.longitude)
    print("CRS：World Geodetic System 1984 (WGS84)")
    return maptiler_DD1, maptiler_CRS


def opencage_geocoding(placename,opencage_api_key):
    location = geocoder.opencage(placename, key=opencage_api_key)
    print("\nOpenCage API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        opencage_DD1 = location.latlng
        opencage_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return opencage_DD1, opencage_CRS
    else:
        print("Error:", location.status)


def openstreetmap_geocoding(placename):
    location = geocoder.osm(placename)
    print("\nOpenStreetMap API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        osm_DD1 = location.latlng
        osm_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return osm_DD1, osm_CRS
    else:
        print("Error:", location.status)


def photon_geocoding(placename):
    photon_geolocator = Photon()
    photon_location = photon_geolocator.geocode(placename)
    print("\nPhoton API:")
    photon_DD1 = (photon_location.latitude, photon_location.longitude)
    photon_CRS = "World Geodetic System 1984 (WGS84)"
    print(photon_location.latitude, photon_location.longitude)
    print("CRS：World Geodetic System 1984 (WGS84)")
    return photon_DD1, photon_CRS


def pickpoint_geocoding(placename,pickpoint_api_key):
    pickpoint_geolocator = PickPoint(api_key=pickpoint_api_key)
    pickpoint_location = pickpoint_geolocator.geocode(placename)
    print("\nPickPoint API:")
    pickpoint_DD1 = (pickpoint_location.latitude, pickpoint_location.longitude)
    pickpoint_CRS = "World Geodetic System 1984 (WGS84)"
    print(pickpoint_location.latitude, pickpoint_location.longitude)
    print("CRS：World Geodetic System 1984 (WGS84)")
    return pickpoint_DD1, pickpoint_CRS


def uscensus_geocoding(placename):
    location = geocoder.uscensus(placename)
    print("\nOpenStreetMap API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        uscensus_DD1 = location.latlng
        uscensus_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return uscensus_DD1, uscensus_CRS
    else:
        print("Error:", location.status)


def yahoo_geocoding(placename):
    location = geocoder.yahoo(placename)
    print("\nYahoo API:")
    if location.ok:
        latitude = location.latlng[0]
        longitude = location.latlng[1]
        yahoo_DD1 = location.latlng
        yahoo_CRS = "World Geodetic System 1984 (WGS84)"
        print(latitude, longitude)
        print("CRS：World Geodetic System 1984 (WGS84)")
        return yahoo_DD1, yahoo_CRS
    else:
        print("Error:", location.status)


# def all_geocoding():
#     arcgis_gecoding(placename)
#     baidu_gecoding(placename, baidu_api_key)
#     #banfrance_gecoding(placename)
#     bing_gecoding(placename, bing_api_key)
#     canadapost_gecoding(placename, canadapost_api_key)
#     databc_gecoding(placename)
#     geocodeearth_gecoding(placename, geocodeearth_api_key)
#     geocodefarm_gecoding(placename, geocodefarm_api_key)
#     #gaode_gecoding(placename, gaode_api_key)
#     geolake_gecoding(placename, geolake_api_key)
#     geonames_gecoding(placename, geonames_api_key)
#     geoottawa_gecoding(placename)
#     gisgraphy_gecoding(placename)
#     google_gecoding(placename)
#     here_gecoding(placename, here_api_key)
#     #ignfrance_gecoding(placename)
#     locationiq_gecoding(placename, locationiq_api_key)
#     mapbox_gecoding(placename, mapbox_api_key)
#     mapquest_gecoding(placename, mapquest_api_key)
#     maptiler_gecoding(placename, maptiler_api_key)
#     opencage_gecoding(placename, opencage_api_key)
#     openstreetmap_gecoding(placename)
#     photon_gecoding(placename)
#     pickpoint_gecoding(placename, pickpoint_api_key)
#     uscensus_gecoding(placename)
#     yahoo_gecoding(placename)

def batch_geocode_from_csv(file_path, geocode_function):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if row:
                place_name = row[0]
                print(f"\nProcessing: {place_name}")

                geocode_function(place_name)

# if __name__ == "__main__":
#     #placename = "Addis Ababa"
#     #placename = "Lege Tafo"
#     #placename = "Adi Abun"
#     #placename = "Adwa"
#     #placename = "Ambalage"
#     #placename = "Inda Baguna"
#     #placename = "Atsbi Inda Silase"
#     #placename = "May Mekdan"
#     #placename = "Bizet"
#     #placename = "Senkata"
#
#     # baidu_api_key = ""
#     # bing_api_key = ""
#     # canadapost_api_key = ""
#     # gaode_api_key = ""
#     # geocodeearth_api_key = ""
#     # geocodefarm_api_key = ""
#     # geolake_api_key = ""
#     # geonames_api_key = ''
#     # here_api_key = ""
#     # locationiq_api_key = ""
#     # mapbox_api_key = ""
#     # mapquest_api_key = ""
#     # maptiler_api_key = ""
#     # opencage_api_key = ""
#     # pickpoint_api_key = ""
#     # what3words_api_key = ""
#
#     # arcgis_gecoding(placename)
#     # baidu_gecoding(placename, baidu_api_key)
#     # banfrance_gecoding(placename)
#     # bing_gecoding(placename, bing_api_key)
#     # canadapost_gecoding(placename, canadapost_api_key)
#     # databc_gecoding(placename)
#     # geocodeearth_gecoding(placename, geocodeearth_api_key)
#     # geocodefarm_gecoding(placename, geocodefarm_api_key)
#     # gaode_gecoding(placename, gaode_api_key)
#     # geolake_gecoding(placename, geolake_api_key)
#     # geonames_gecoding(placename, geonames_api_key)
#     # geoottawa_gecoding(placename)
#     # gisgraphy_gecoding(placename)
#     # google_gecoding(placename)
#     # here_gecoding(placename, here_api_key)
#     # ignfrance_gecoding(placename)
#     # locationiq_gecoding(placename, locationiq_api_key)
#     # mapbox_gecoding(placename, mapbox_api_key)
#     # mapquest_gecoding(placename, mapquest_api_key)
#     # maptiler_gecoding(placename, maptiler_api_key)
#     # opencage_gecoding(placename, opencage_api_key)
#     # openstreetmap_gecoding(placename)
#     # photon_gecoding(placename)
#     # pickpoint_gecoding(placename, pickpoint_api_key)
#     # uscensus_gecoding(placename)
#     # yahoo_gecoding(placename)
#
#     placename_list = ["Addis Ababa","Lege Tafo","Adi Abun","Adwa","Ambalage",
#                       "Inda Baguna","Atsbi Inda Silase","May Mekdan","Bizet","Senkata"]
#     for placename in placename_list:
#         arcgis_gecoding(placename)
#         baidu_gecoding(placename, baidu_api_key)
#         banfrance_gecoding(placename)
#         bing_gecoding(placename, bing_api_key)
#         canadapost_gecoding(placename, canadapost_api_key)
#         databc_gecoding(placename)
#         geocodeearth_gecoding(placename, geocodeearth_api_key)
#         geocodefarm_gecoding(placename, geocodefarm_api_key)
#         gaode_gecoding(placename, gaode_api_key)
#         geolake_gecoding(placename, geolake_api_key)
#         geonames_gecoding(placename, geonames_api_key)
#         geoottawa_gecoding(placename)
#         gisgraphy_gecoding(placename)
#         google_gecoding(placename)
#         here_gecoding(placename, here_api_key)
#         ignfrance_gecoding(placename)
#         locationiq_gecoding(placename, locationiq_api_key)
#         mapbox_gecoding(placename, mapbox_api_key)
#         mapquest_gecoding(placename, mapquest_api_key)
#         maptiler_gecoding(placename, maptiler_api_key)
#         opencage_gecoding(placename, opencage_api_key)
#         openstreetmap_gecoding(placename)
#         photon_gecoding(placename)
#         pickpoint_gecoding(placename, pickpoint_api_key)
#         uscensus_gecoding(placename)
#         yahoo_gecoding(placename)
#
#     # file_path = input("Please enter the CSV file path：")
#     # chosen_geocode_function = arcgis_gecoding
#     # batch_geocode_from_csv(file_path, chosen_geocode_function)
#
#
#     #all_gecoding()
