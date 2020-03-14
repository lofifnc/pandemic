from typing import Dict

from pandemic.model.city_id import CityId
from pandemic.model.enums import Virus
from pandemic.model.city import City


CITIES: Dict[CityId, City] = {
    "algiers": City("Algiers", 36.7753606, 3.0601882, Virus.BLUE),
    "atlanta": City(
        "Atlanta", 33.7490987, -84.3901849, Virus.BLUE, research_station=True
    ),
    "baghdad": City("Baghdad", 33.3024309, 44.3787992, Virus.BLACK),
    "bangkok": City(
        "Bangkok", 13.7542529, 100.493087, Virus.RED, text_alignment="right"
    ),
    "beijing": City(
        "Beijing", 39.906217, 116.3912757, Virus.RED, text_alignment="right"
    ),
    "bogota": City("Bogota", 4.59808, -74.0760439, Virus.YELLOW),
    "buenos_aries": City("Buenos Aries", -34.6546138, -58.4155345, Virus.YELLOW),
    "cairo": City("Cairo", 30.048819, 31.243666, Virus.BLACK),
    "chennai": City(
        "Chennai", 13.0801721, 80.2838331, Virus.BLACK, text_alignment="right"
    ),
    "chicago": City("Chicago", 41.8755616, -87.6244212, Virus.BLUE),
    "delhi": City("Delhi", 28.6517178, 77.2219388, Virus.BLACK),
    "essen": City("Essen", 51.4582235, 7.0158171, Virus.BLUE),
    "ho_chi_minh_city": City("Ho Chi Minh City", 10.6497452, 106.7619794, Virus.RED),
    "hong_kong": City("Hong Kong", 22.2793278, 114.1628131, Virus.RED),
    "istanbul": City("Istanbul", 41.0096334, 28.9651646, Virus.BLACK),
    "jakarta": City("Jakarta", -6.1753942, 106.827183, Virus.RED),
    "johannesburg": City("Johannesburg", -26.205, 28.049722, Virus.YELLOW),
    "karachi": City("Karachi", 24.8667795, 67.0311286, Virus.BLACK),
    "khartoum": City("Khartoum", 15.593325, 32.53565, Virus.YELLOW),
    "kinshasa": City("Kinshasa", -4.3217055, 15.3125974, Virus.YELLOW),
    "kolkata": City("Kolkata", 22.5677459, 88.3476023, Virus.BLACK),
    "lagos": City("Lagos", 6.4550575, 3.3941795, Virus.YELLOW),
    "lima": City("Lima", -12.0621065, -77.0365256, Virus.YELLOW),
    "london": City(
        "London", 51.5073219, -0.1276474, Virus.BLUE, text_alignment="right"
    ),
    "los_angeles": City("Los Angeles", 34.0536909, -118.2427666, Virus.YELLOW),
    "madrid": City("Madrid", 40.4167047, -3.7035825, Virus.BLUE),
    "manila": City("Manila", 14.5906216, 120.9799696, Virus.RED),
    "mexico_city": City("Mexico City", 19.4326296, -99.1331785, Virus.YELLOW),
    "miami": City("Miami", 25.7742658, -80.1936589, Virus.YELLOW),
    "milan": City("Milan", 45.4668, 9.1905, Virus.BLUE),
    "montreal": City("Montreal", 45.4972159, -73.6103642, Virus.BLUE),
    "moscow": City("Moscow", 55.7504461, 37.6174943, Virus.BLACK),
    "mumbai": City(
        "Mumbai", 18.9387711, 72.8353355, Virus.BLACK, text_alignment="right"
    ),
    "new_york": City("New York", 40.7127281, -74.0060152, Virus.BLUE),
    "osaka": City("Osaka", 34.6198813, 135.490357, Virus.RED, text_alignment="right"),
    "paris": City("Paris", 48.8566969, 2.3514616, Virus.BLUE),
    "riyadh": City("Riyadh", 24.6319692, 46.7150648, Virus.BLACK),
    "san_francisco": City("San Francisco", 37.7790262, -122.4199061, Virus.BLUE),
    "santiago": City("Santiago", -33.45, -70.666667, Virus.YELLOW),
    "sao_paulo": City("Sao Paulo", -23.5506507, -46.6333824, Virus.YELLOW),
    "seoul": City("Seoul", 37.5649826, 126.9392108, Virus.RED, text_alignment="right"),
    "shanghai": City(
        "Shanghai", 31.2252985, 121.4890497, Virus.RED, text_alignment="right"
    ),
    "st_petersburg": City("St. Petersburg", 59.938732, 30.316229, Virus.BLUE),
    "sydney": City("Sydney", -33.8548157, 151.2164539, Virus.RED),
    "taipei": City("Taipei", 25.0375198, 121.5636796, Virus.RED),
    "tehran": City("Tehran", 35.7006177, 51.4013785, Virus.BLACK),
    "tokyo": City("Tokyo", 35.6828387, 139.7594549, Virus.RED),
    "washington": City("Washington", 38.8948932, -77.0365529, Virus.BLUE),
}

CONNECTIONS: (CityId, CityId) = [
    ("san_francisco", "tokyo"),
    ("san_francisco", "manila"),
    ("san_francisco", "chicago"),
    ("san_francisco", "los_angeles"),
    ("chicago", "los_angeles"),
    ("chicago", "mexico_city"),
    ("chicago", "atlanta"),
    ("chicago", "montreal"),
    ("los_angeles", "sydney"),
    ("los_angeles", "mexico_city"),
    ("mexico_city", "bogota"),
    ("mexico_city", "miami"),
    ("mexico_city", "lima"),
    ("lima", "bogota"),
    ("lima", "santiago"),
    ("bogota", "buenos_aries"),
    ("bogota", "sao_paulo"),
    ("miami", "bogota"),
    ("miami", "washington"),
    ("miami", "atlanta"),
    ("buenos_aries", "sao_paulo"),
    ("sao_paulo", "lagos"),
    ("sao_paulo", "madrid"),
    ("atlanta", "washington"),
    ("washington", "new_york"),
    ("washington", "montreal"),
    ("new_york", "montreal"),
    ("new_york", "madrid"),
    ("new_york", "london"),
    ("sydney", "jakarta"),
    ("sydney", "manila"),
    ("manila", "ho_chi_minh_city"),
    ("manila", "taipei"),
    ("jakarta", "ho_chi_minh_city"),
    ("jakarta", "bangkok"),
    ("jakarta", "chennai"),
    ("ho_chi_minh_city", "bangkok"),
    ("ho_chi_minh_city", "hong_kong"),
    ("bangkok", "chennai"),
    ("bangkok", "hong_kong"),
    ("bangkok", "kolkata"),
    ("hong_kong", "kolkata"),
    ("hong_kong", "taipei"),
    ("hong_kong", "shanghai"),
    ("taipei", "osaka"),
    ("osaka", "tokyo"),
    ("tokyo", "seoul"),
    ("tokyo", "shanghai"),
    ("seoul", "beijing"),
    ("seoul", "shanghai"),
    ("beijing", "shanghai"),
    ("chennai", "kolkata"),
    ("chennai", "mumbai"),
    ("chennai", "delhi"),
    ("kolkata", "delhi"),
    ("mumbai", "delhi"),
    ("mumbai", "karachi"),
    ("delhi", "karachi"),
    ("delhi", "tehran"),
    ("karachi", "tehran"),
    ("karachi", "baghdad"),
    ("karachi", "riyadh"),
    ("karachi", "riyadh"),
    ("riyadh", "baghdad"),
    ("riyadh", "cairo"),
    ("baghdad", "tehran"),
    ("baghdad", "cairo"),
    ("baghdad", "istanbul"),
    ("tehran", "moscow"),
    ("moscow", "st_petersburg"),
    ("moscow", "istanbul"),
    ("istanbul", "milan"),
    ("istanbul", "st_petersburg"),
    ("istanbul", "algiers"),
    ("istanbul", "cairo"),
    ("cairo", "algiers"),
    ("cairo", "khartoum"),
    ("algiers", "madrid"),
    ("algiers", "paris"),
    ("algiers", "paris"),
    ("madrid", "london"),
    ("madrid", "london"),
    ("paris", "essen"),
    ("paris", "milan"),
    ("paris", "london"),
    ("milan", "essen"),
    ("essen", "st_petersburg"),
    ("essen", "london"),
    ("khartoum", "kinshasa"),
    ("khartoum", "johannesburg"),
    ("khartoum", "lagos"),
    ("kinshasa", "lagos"),
    ("kinshasa", "johannesburg"),
]

PLAYER_COUNT = 4

TOTAL_STARTING_PLAYER_CARDS = 6

PLAYER_START = "atlanta"

EPIDEMIC_CARD = "epidemic"

PLAYER_ACTIONS = 4

INFECTIONS_RATES = [2, 2, 2, 3, 3, 4, 4]
