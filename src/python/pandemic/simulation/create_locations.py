import urllib.request
import json
import urllib.parse

cities = [
    "Algiers",
    "Atlanta",
    "Baghdad",
    "Bangkok",
    "Beijing",
    "Bogota",
    "Buenos Aries",
    "Cairo",
    "Chennai",
    "Chicago",
    "Delhi",
    "Essen",
    "Ho Chi Minh City",
    "Hong Kong",
    "Istanbul",
    "Jakarta",
    "Johannesburg",
    "Karachi",
    "Khartoum",
    "Kinshasa",
    "Kolkata",
    "Lagos",
    "Lima",
    "London",
    "Los Angeles",
    "Madrid",
    "Manila",
    "Mexico City",
    "Miami",
    "Milan",
    "Montreal",
    "Moscow",
    "Mumbai",
    "New York",
    "Osaka",
    "Paris",
    "Riyadh",
    "San Francisco",
    "Santiago",
    "Sao Paulo",
    "Seoul",
    "Shanghai",
    "St. Petersburg",
    "Sydney",
    "Taipei",
    "Tehran",
    "Tokyo",
    "Washington",
]
API_KEY = "..."

"https://api.opencagedata.com/geocode/v1/json?q=PLACENAME&key=YOUR-API-KEY"

for city in cities:
    r = urllib.request.urlopen(
        f"https://api.opencagedata.com/geocode/v1/json?q={urllib.parse.quote(city)}&key={API_KEY}"
    )
    r_dict = json.loads(r.read())
    dms = r_dict["results"][0]["geometry"]
    lat = dms["lat"]
    lon = dms["lng"]
    city_id = city.replace(".", "").replace(" ", "_").lower()
    res = f'"{city_id}": Location("{city}", {lat}, {lon}, Virus.BLUE),'
    print(res)
