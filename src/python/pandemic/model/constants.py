from typing import Dict

from pandemic.model.city_id import City
from pandemic.model.enums import Virus
from pandemic.model.citystate import CityState


def create_cities_init_state() -> Dict[City, CityState] :
    return {
        City.ALGIERS: CityState("Algiers", 36.7753606, 3.0601882, Virus.BLUE),
        City.ATLANTA: CityState("Atlanta", 33.7490987, -84.3901849, Virus.BLUE, research_station=True),
        City.BAGHDAD: CityState("Baghdad", 33.3024309, 44.3787992, Virus.BLACK),
        City.BANGKOK: CityState("Bangkok", 13.7542529, 100.493087, Virus.RED, text_alignment="right"),
        City.BEIJING: CityState("Beijing", 39.906217, 116.3912757, Virus.RED, text_alignment="right"),
        City.BOGOTA: CityState("Bogota", 4.59808, -74.0760439, Virus.YELLOW),
        City.BUENOS_ARIES: CityState("Buenos Aries", -34.6546138, -58.4155345, Virus.YELLOW),
        City.CAIRO: CityState("Cairo", 30.048819, 31.243666, Virus.BLACK),
        City.CHENNAI: CityState("Chennai", 13.0801721, 80.2838331, Virus.BLACK, text_alignment="right"),
        City.CHICAGO: CityState("Chicago", 41.8755616, -87.6244212, Virus.BLUE),
        City.DELHI: CityState("Delhi", 28.6517178, 77.2219388, Virus.BLACK),
        City.ESSEN: CityState("Essen", 51.4582235, 7.0158171, Virus.BLUE),
        City.HO_CHI_MINH_CITY: CityState("Ho Chi Minh City", 10.6497452, 106.7619794, Virus.RED),
        City.HONG_KONG: CityState("Hong Kong", 22.2793278, 114.1628131, Virus.RED),
        City.ISTANBUL: CityState("Istanbul", 41.0096334, 28.9651646, Virus.BLACK),
        City.JAKARTA: CityState("Jakarta", -6.1753942, 106.827183, Virus.RED),
        City.JOHANNESBURG: CityState("Johannesburg", -26.205, 28.049722, Virus.YELLOW),
        City.KARACHI: CityState("Karachi", 24.8667795, 67.0311286, Virus.BLACK),
        City.KHARTOUM: CityState("Khartoum", 15.593325, 32.53565, Virus.YELLOW),
        City.KINSHASA: CityState("Kinshasa", -4.3217055, 15.3125974, Virus.YELLOW),
        City.KOLKATA: CityState("Kolkata", 22.5677459, 88.3476023, Virus.BLACK),
        City.LAGOS: CityState("Lagos", 6.4550575, 3.3941795, Virus.YELLOW),
        City.LIMA: CityState("Lima", -12.0621065, -77.0365256, Virus.YELLOW),
        City.LONDON: CityState("London", 51.5073219, -0.1276474, Virus.BLUE, text_alignment="right"),
        City.LOS_ANGELES: CityState("Los Angeles", 34.0536909, -118.2427666, Virus.YELLOW),
        City.MADRID: CityState("Madrid", 40.4167047, -3.7035825, Virus.BLUE),
        City.MANILA: CityState("Manila", 14.5906216, 120.9799696, Virus.RED),
        City.MEXICO_CITY: CityState("Mexico City", 19.4326296, -99.1331785, Virus.YELLOW),
        City.MIAMI: CityState("Miami", 25.7742658, -80.1936589, Virus.YELLOW),
        City.MILAN: CityState("Milan", 45.4668, 9.1905, Virus.BLUE),
        City.MONTREAL: CityState("Montreal", 45.4972159, -73.6103642, Virus.BLUE),
        City.MOSCOW: CityState("Moscow", 55.7504461, 37.6174943, Virus.BLACK),
        City.MUMBAI: CityState("Mumbai", 18.9387711, 72.8353355, Virus.BLACK, text_alignment="right"),
        City.NEW_YORK: CityState("New York", 40.7127281, -74.0060152, Virus.BLUE),
        City.OSAKA: CityState("Osaka", 34.6198813, 135.490357, Virus.RED, text_alignment="right"),
        City.PARIS: CityState("Paris", 48.8566969, 2.3514616, Virus.BLUE),
        City.RIYADH: CityState("Riyadh", 24.6319692, 46.7150648, Virus.BLACK),
        City.SAN_FRANCISCO: CityState("San Francisco", 37.7790262, -122.4199061, Virus.BLUE),
        City.SANTIAGO: CityState("Santiago", -33.45, -70.666667, Virus.YELLOW),
        City.SAO_PAULO: CityState("Sao Paulo", -23.5506507, -46.6333824, Virus.YELLOW),
        City.SEOUL: CityState("Seoul", 37.5649826, 126.9392108, Virus.RED, text_alignment="right"),
        City.SHANGHAI: CityState("Shanghai", 31.2252985, 121.4890497, Virus.RED, text_alignment="right"),
        City.ST_PETERSBURG: CityState("St. Petersburg", 59.938732, 30.316229, Virus.BLUE),
        City.SYDNEY: CityState("Sydney", -33.8548157, 151.2164539, Virus.RED),
        City.TAIPEI: CityState("Taipei", 25.0375198, 121.5636796, Virus.RED),
        City.TEHRAN: CityState("Tehran", 35.7006177, 51.4013785, Virus.BLACK),
        City.TOKYO: CityState("Tokyo", 35.6828387, 139.7594549, Virus.RED),
        City.WASHINGTON: CityState("Washington", 38.8948932, -77.0365529, Virus.BLUE),
    }

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

EPIDEMIC_CARDS = 5

INFECTIONS_RATES = [2, 2, 2, 3, 3, 4, 4]

COUNT_CUBES = 24
