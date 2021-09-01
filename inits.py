import mysql.connector
from geopy.geocoders import Nominatim
from datetime import datetime

geolocator = Nominatim(user_agent="run.py")
now = datetime.now()
NAMES = ['Общая площадь', 'Этаж', 'Материал дома']


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="<password>"
)
mycursor = mydb.cursor()