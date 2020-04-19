from dataclasses import dataclass
from typing import Dict, Set

from pandemic.simulation.model.city_id import City
from pandemic.simulation.model.enums import Virus
from pandemic.simulation.model.citystate import CityState


@dataclass(frozen=True)
class CityData:
    name: str
    lat: float
    lon: float
    color: int
    neighbors: Set[int]
    text_alignment: str = "left"

    @property
    def text_offset(self):
        return 2 if self.text_alignment == "left" else -2


NEIGHBORS = {
    1: {8, 26, 36, 15},
    2: {48, 10, 29},
    3: {37, 8, 46, 15, 18},
    4: {9, 13, 14, 16, 21},
    5: {41, 42},
    6: {7, 40, 23, 28, 29},
    7: {40, 6},
    8: {1, 3, 37, 15, 19},
    9: {33, 4, 11, 16, 21},
    10: {2, 38, 25, 28, 31},
    11: {33, 9, 46, 18, 21},
    12: {24, 43, 36, 30},
    13: {16, 27, 4, 14},
    14: {4, 42, 45, 13, 21},
    15: {32, 1, 3, 8, 43, 30},
    16: {9, 4, 44, 13},
    17: {19, 20},
    18: {33, 3, 37, 11, 46},
    19: {8, 17, 20, 22},
    20: {17, 19, 22},
    21: {9, 11, 4, 14},
    22: {40, 19, 20},
    23: {28, 6, 39},
    24: {34, 26, 36, 12},
    25: {10, 44, 28, 38},
    26: {40, 1, 34, 24},
    27: {45, 44, 13, 38},
    28: {6, 10, 23, 25, 29},
    29: {48, 2, 28, 6},
    30: {36, 12, 15},
    31: {48, 10, 34},
    32: {43, 46, 15},
    33: {9, 18, 11},
    34: {48, 24, 26, 31},
    35: {45, 47},
    36: {24, 1, 12, 30},
    37: {8, 18, 3},
    38: {25, 10, 27, 47},
    39: {23},
    40: {26, 22, 6, 7},
    41: {42, 5, 47},
    42: {41, 5, 14, 47},
    43: {32, 12, 15},
    44: {16, 25, 27},
    45: {35, 27, 14},
    46: {32, 11, 18, 3},
    47: {41, 42, 35, 38},
    48: {2, 34, 29, 31},
}

CITY_DATA = {
    City.ALGIERS: CityData("Algiers", 36.7753606, 3.0601882, Virus.BLUE, neighbors=NEIGHBORS[City.ALGIERS]),
    City.ATLANTA: CityData("Atlanta", 33.7490987, -84.3901849, Virus.BLUE, neighbors=NEIGHBORS[City.ATLANTA]),
    City.BAGHDAD: CityData("Baghdad", 33.3024309, 44.3787992, Virus.BLACK, neighbors=NEIGHBORS[City.BAGHDAD]),
    City.BANGKOK: CityData(
        "Bangkok", 13.7542529, 100.493087, Virus.RED, text_alignment="right", neighbors=NEIGHBORS[City.BANGKOK]
    ),
    City.BEIJING: CityData(
        "Beijing", 39.906217, 116.3912757, Virus.RED, text_alignment="right", neighbors=NEIGHBORS[City.BEIJING]
    ),
    City.BOGOTA: CityData("Bogota", 4.59808, -74.0760439, Virus.YELLOW, neighbors=NEIGHBORS[City.BOGOTA]),
    City.BUENOS_ARIES: CityData(
        "Buenos Aries", -34.6546138, -58.4155345, Virus.YELLOW, neighbors=NEIGHBORS[City.BUENOS_ARIES]
    ),
    City.CAIRO: CityData("Cairo", 30.048819, 31.243666, Virus.BLACK, neighbors=NEIGHBORS[City.CAIRO]),
    City.CHENNAI: CityData(
        "Chennai", 13.0801721, 80.2838331, Virus.BLACK, text_alignment="right", neighbors=NEIGHBORS[City.CHENNAI]
    ),
    City.CHICAGO: CityData("Chicago", 41.8755616, -87.6244212, Virus.BLUE, neighbors=NEIGHBORS[City.CHICAGO]),
    City.DELHI: CityData("Delhi", 28.6517178, 77.2219388, Virus.BLACK, neighbors=NEIGHBORS[City.DELHI]),
    City.ESSEN: CityData("Essen", 51.4582235, 7.0158171, Virus.BLUE, neighbors=NEIGHBORS[City.ESSEN]),
    City.HO_CHI_MINH_CITY: CityData(
        "Ho Chi Minh City", 10.6497452, 106.7619794, Virus.RED, neighbors=NEIGHBORS[City.HO_CHI_MINH_CITY]
    ),
    City.HONG_KONG: CityData("Hong Kong", 22.2793278, 114.1628131, Virus.RED, neighbors=NEIGHBORS[City.HONG_KONG]),
    City.ISTANBUL: CityData("Istanbul", 41.0096334, 28.9651646, Virus.BLACK, neighbors=NEIGHBORS[City.ISTANBUL]),
    City.JAKARTA: CityData("Jakarta", -6.1753942, 106.827183, Virus.RED, neighbors=NEIGHBORS[City.JAKARTA]),
    City.JOHANNESBURG: CityData(
        "Johannesburg", -26.205, 28.049722, Virus.YELLOW, neighbors=NEIGHBORS[City.JOHANNESBURG]
    ),
    City.KARACHI: CityData("Karachi", 24.8667795, 67.0311286, Virus.BLACK, neighbors=NEIGHBORS[City.KARACHI]),
    City.KHARTOUM: CityData("Khartoum", 15.593325, 32.53565, Virus.YELLOW, neighbors=NEIGHBORS[City.KHARTOUM]),
    City.KINSHASA: CityData("Kinshasa", -4.3217055, 15.3125974, Virus.YELLOW, neighbors=NEIGHBORS[City.KINSHASA]),
    City.KOLKATA: CityData("Kolkata", 22.5677459, 88.3476023, Virus.BLACK, neighbors=NEIGHBORS[City.KOLKATA]),
    City.LAGOS: CityData("Lagos", 6.4550575, 3.3941795, Virus.YELLOW, neighbors=NEIGHBORS[City.LAGOS]),
    City.LIMA: CityData("Lima", -12.0621065, -77.0365256, Virus.YELLOW, neighbors=NEIGHBORS[City.LIMA]),
    City.LONDON: CityData(
        "London", 51.5073219, -0.1276474, Virus.BLUE, text_alignment="right", neighbors=NEIGHBORS[City.LONDON]
    ),
    City.LOS_ANGELES: CityData(
        "Los Angeles", 34.0536909, -118.2427666, Virus.YELLOW, neighbors=NEIGHBORS[City.LOS_ANGELES]
    ),
    City.MADRID: CityData("Madrid", 40.4167047, -3.7035825, Virus.BLUE, neighbors=NEIGHBORS[City.MADRID]),
    City.MANILA: CityData("Manila", 14.5906216, 120.9799696, Virus.RED, neighbors=NEIGHBORS[City.MANILA]),
    City.MEXICO_CITY: CityData(
        "Mexico City", 19.4326296, -99.1331785, Virus.YELLOW, neighbors=NEIGHBORS[City.MEXICO_CITY]
    ),
    City.MIAMI: CityData("Miami", 25.7742658, -80.1936589, Virus.YELLOW, neighbors=NEIGHBORS[City.MIAMI]),
    City.MILAN: CityData("Milan", 45.4668, 9.1905, Virus.BLUE, neighbors=NEIGHBORS[City.MILAN]),
    City.MONTREAL: CityData("Montreal", 45.4972159, -73.6103642, Virus.BLUE, neighbors=NEIGHBORS[City.MONTREAL]),
    City.MOSCOW: CityData("Moscow", 55.7504461, 37.6174943, Virus.BLACK, neighbors=NEIGHBORS[City.MOSCOW]),
    City.MUMBAI: CityData(
        "Mumbai", 18.9387711, 72.8353355, Virus.BLACK, text_alignment="right", neighbors=NEIGHBORS[City.MUMBAI]
    ),
    City.NEW_YORK: CityData("New York", 40.7127281, -74.0060152, Virus.BLUE, neighbors=NEIGHBORS[City.NEW_YORK]),
    City.OSAKA: CityData(
        "Osaka", 34.6198813, 135.490357, Virus.RED, text_alignment="right", neighbors=NEIGHBORS[City.OSAKA]
    ),
    City.PARIS: CityData("Paris", 48.8566969, 2.3514616, Virus.BLUE, neighbors=NEIGHBORS[City.PARIS]),
    City.RIYADH: CityData("Riyadh", 24.6319692, 46.7150648, Virus.BLACK, neighbors=NEIGHBORS[City.RIYADH]),
    City.SAN_FRANCISCO: CityData(
        "San Francisco", 37.7790262, -122.4199061, Virus.BLUE, neighbors=NEIGHBORS[City.SAN_FRANCISCO]
    ),
    City.SANTIAGO: CityData("Santiago", -33.45, -70.666667, Virus.YELLOW, neighbors=NEIGHBORS[City.SANTIAGO]),
    City.SAO_PAULO: CityData("Sao Paulo", -23.5506507, -46.6333824, Virus.YELLOW, neighbors=NEIGHBORS[City.SAO_PAULO]),
    City.SEOUL: CityData(
        "Seoul", 37.5649826, 126.9392108, Virus.RED, text_alignment="right", neighbors=NEIGHBORS[City.SEOUL]
    ),
    City.SHANGHAI: CityData(
        "Shanghai", 31.2252985, 121.4890497, Virus.RED, text_alignment="right", neighbors=NEIGHBORS[City.SHANGHAI]
    ),
    City.ST_PETERSBURG: CityData(
        "St. Petersburg", 59.938732, 30.316229, Virus.BLUE, neighbors=NEIGHBORS[City.ST_PETERSBURG]
    ),
    City.SYDNEY: CityData("Sydney", -33.8548157, 151.2164539, Virus.RED, neighbors=NEIGHBORS[City.SYDNEY]),
    City.TAIPEI: CityData("Taipei", 25.0375198, 121.5636796, Virus.RED, neighbors=NEIGHBORS[City.TAIPEI]),
    City.TEHRAN: CityData("Tehran", 35.7006177, 51.4013785, Virus.BLACK, neighbors=NEIGHBORS[City.TEHRAN]),
    City.TOKYO: CityData("Tokyo", 35.6828387, 139.7594549, Virus.RED, neighbors=NEIGHBORS[City.TOKYO]),
    City.WASHINGTON: CityData("Washington", 38.8948932, -77.0365529, Virus.BLUE, neighbors=NEIGHBORS[City.WASHINGTON]),
}


def create_cities_init_state() -> Dict[City, CityState]:
    return {
        City.ALGIERS: CityState(),
        City.ATLANTA: CityState(research_station=True),
        City.BAGHDAD: CityState(),
        City.BANGKOK: CityState(),
        City.BEIJING: CityState(),
        City.BOGOTA: CityState(),
        City.BUENOS_ARIES: CityState(),
        City.CAIRO: CityState(),
        City.CHENNAI: CityState(),
        City.CHICAGO: CityState(),
        City.DELHI: CityState(),
        City.ESSEN: CityState(),
        City.HO_CHI_MINH_CITY: CityState(),
        City.HONG_KONG: CityState(),
        City.ISTANBUL: CityState(),
        City.JAKARTA: CityState(),
        City.JOHANNESBURG: CityState(),
        City.KARACHI: CityState(),
        City.KHARTOUM: CityState(),
        City.KINSHASA: CityState(),
        City.KOLKATA: CityState(),
        City.LAGOS: CityState(),
        City.LIMA: CityState(),
        City.LONDON: CityState(),
        City.LOS_ANGELES: CityState(),
        City.MADRID: CityState(),
        City.MANILA: CityState(),
        City.MEXICO_CITY: CityState(),
        City.MIAMI: CityState(),
        City.MILAN: CityState(),
        City.MONTREAL: CityState(),
        City.MOSCOW: CityState(),
        City.MUMBAI: CityState(),
        City.NEW_YORK: CityState(),
        City.OSAKA: CityState(),
        City.PARIS: CityState(),
        City.RIYADH: CityState(),
        City.SAN_FRANCISCO: CityState(),
        City.SANTIAGO: CityState(),
        City.SAO_PAULO: CityState(),
        City.SEOUL: CityState(),
        City.SHANGHAI: CityState(),
        City.ST_PETERSBURG: CityState(),
        City.SYDNEY: CityState(),
        City.TAIPEI: CityState(),
        City.TEHRAN: CityState(),
        City.TOKYO: CityState(),
        City.WASHINGTON: CityState(),
    }


CITY_COLORS = {id: city.color for id, city in CITY_DATA.items()}

CONNECTIONS: (City, City) = [
    (City.SAN_FRANCISCO, City.TOKYO),
    (City.SAN_FRANCISCO, City.MANILA),
    (City.SAN_FRANCISCO, City.CHICAGO),
    (City.SAN_FRANCISCO, City.LOS_ANGELES),
    (City.CHICAGO, City.LOS_ANGELES),
    (City.CHICAGO, City.MEXICO_CITY),
    (City.CHICAGO, City.ATLANTA),
    (City.CHICAGO, City.MONTREAL),
    (City.LOS_ANGELES, City.SYDNEY),
    (City.LOS_ANGELES, City.MEXICO_CITY),
    (City.MEXICO_CITY, City.BOGOTA),
    (City.MEXICO_CITY, City.MIAMI),
    (City.MEXICO_CITY, City.LIMA),
    (City.LIMA, City.BOGOTA),
    (City.LIMA, City.SANTIAGO),
    (City.BOGOTA, City.BUENOS_ARIES),
    (City.BOGOTA, City.SAO_PAULO),
    (City.MIAMI, City.BOGOTA),
    (City.MIAMI, City.WASHINGTON),
    (City.MIAMI, City.ATLANTA),
    (City.BUENOS_ARIES, City.SAO_PAULO),
    (City.SAO_PAULO, City.LAGOS),
    (City.SAO_PAULO, City.MADRID),
    (City.ATLANTA, City.WASHINGTON),
    (City.WASHINGTON, City.NEW_YORK),
    (City.WASHINGTON, City.MONTREAL),
    (City.NEW_YORK, City.MONTREAL),
    (City.NEW_YORK, City.MADRID),
    (City.NEW_YORK, City.LONDON),
    (City.SYDNEY, City.JAKARTA),
    (City.SYDNEY, City.MANILA),
    (City.MANILA, City.HO_CHI_MINH_CITY),
    (City.MANILA, City.TAIPEI),
    (City.JAKARTA, City.HO_CHI_MINH_CITY),
    (City.JAKARTA, City.BANGKOK),
    (City.JAKARTA, City.CHENNAI),
    (City.HO_CHI_MINH_CITY, City.BANGKOK),
    (City.HO_CHI_MINH_CITY, City.HONG_KONG),
    (City.BANGKOK, City.CHENNAI),
    (City.BANGKOK, City.HONG_KONG),
    (City.BANGKOK, City.KOLKATA),
    (City.HONG_KONG, City.KOLKATA),
    (City.HONG_KONG, City.TAIPEI),
    (City.HONG_KONG, City.SHANGHAI),
    (City.TAIPEI, City.OSAKA),
    (City.OSAKA, City.TOKYO),
    (City.TOKYO, City.SEOUL),
    (City.TOKYO, City.SHANGHAI),
    (City.SEOUL, City.BEIJING),
    (City.SEOUL, City.SHANGHAI),
    (City.BEIJING, City.SHANGHAI),
    (City.CHENNAI, City.KOLKATA),
    (City.CHENNAI, City.MUMBAI),
    (City.CHENNAI, City.DELHI),
    (City.KOLKATA, City.DELHI),
    (City.MUMBAI, City.DELHI),
    (City.MUMBAI, City.KARACHI),
    (City.DELHI, City.KARACHI),
    (City.DELHI, City.TEHRAN),
    (City.KARACHI, City.TEHRAN),
    (City.KARACHI, City.BAGHDAD),
    (City.KARACHI, City.RIYADH),
    (City.KARACHI, City.RIYADH),
    (City.RIYADH, City.BAGHDAD),
    (City.RIYADH, City.CAIRO),
    (City.BAGHDAD, City.TEHRAN),
    (City.BAGHDAD, City.CAIRO),
    (City.BAGHDAD, City.ISTANBUL),
    (City.TEHRAN, City.MOSCOW),
    (City.MOSCOW, City.ST_PETERSBURG),
    (City.MOSCOW, City.ISTANBUL),
    (City.ISTANBUL, City.MILAN),
    (City.ISTANBUL, City.ST_PETERSBURG),
    (City.ISTANBUL, City.ALGIERS),
    (City.ISTANBUL, City.CAIRO),
    (City.CAIRO, City.ALGIERS),
    (City.CAIRO, City.KHARTOUM),
    (City.ALGIERS, City.MADRID),
    (City.ALGIERS, City.PARIS),
    (City.ALGIERS, City.PARIS),
    (City.MADRID, City.LONDON),
    (City.MADRID, City.LONDON),
    (City.PARIS, City.ESSEN),
    (City.PARIS, City.MILAN),
    (City.PARIS, City.LONDON),
    (City.MILAN, City.ESSEN),
    (City.ESSEN, City.ST_PETERSBURG),
    (City.ESSEN, City.LONDON),
    (City.KHARTOUM, City.KINSHASA),
    (City.KHARTOUM, City.JOHANNESBURG),
    (City.KHARTOUM, City.LAGOS),
    (City.KINSHASA, City.LAGOS),
    (City.KINSHASA, City.JOHANNESBURG),
]

PLAYER_COUNT = 4

TOTAL_STARTING_PLAYER_CARDS = 6

PLAYER_START = City.ATLANTA

PLAYER_ACTIONS = 4

INFECTIONS_RATES = [2, 2, 2, 3, 3, 4, 4]

COUNT_CUBES = 24
