from enum import Enum, auto, unique


class Card(Enum):
    pass


@unique
class City(Card):
    ALGIERS = auto()
    ATLANTA = auto()
    BAGHDAD = auto()
    BANGKOK = auto()
    BEIJING = auto()
    BOGOTA = auto()
    BUENOS_ARIES = auto()
    CAIRO = auto()
    CHENNAI = auto()
    CHICAGO = auto()
    DELHI = auto()
    ESSEN = auto()
    HO_CHI_MINH_CITY = auto()
    HONG_KONG = auto()
    ISTANBUL = auto()
    JAKARTA = auto()
    JOHANNESBURG = auto()
    KARACHI = auto()
    KHARTOUM = auto()
    KINSHASA = auto()
    KOLKATA = auto()
    LAGOS = auto()
    LIMA = auto()
    LONDON = auto()
    LOS_ANGELES = auto()
    MADRID = auto()
    MANILA = auto()
    MEXICO_CITY = auto()
    MIAMI = auto()
    MILAN = auto()
    MONTREAL = auto()
    MOSCOW = auto()
    MUMBAI = auto()
    NEW_YORK = auto()
    OSAKA = auto()
    PARIS = auto()
    RIYADH = auto()
    SAN_FRANCISCO = auto()
    SANTIAGO = auto()
    SAO_PAULO = auto()
    SEOUL = auto()
    SHANGHAI = auto()
    ST_PETERSBURG = auto()
    SYDNEY = auto()
    TAIPEI = auto()
    TEHRAN = auto()
    TOKYO = auto()
    WASHINGTON = auto()


class EpidemicCard(Card):
    EPIDEMIC_CARD_1 = 1
    EPIDEMIC_CARD_2 = 2
    EPIDEMIC_CARD_3 = 3
    EPIDEMIC_CARD_4 = 4
    EPIDEMIC_CARD_5 = 5
    EPIDEMIC_CARD_6 = 6


class EventCard(Card):
    def __init__(self, _, command):
        self.command = command

    RESILIENT_POPULATION = (auto(), "r")
    ONE_QUIET_NIGHT = (auto(), "q")
    AIRLIFT = (auto(), "a")
    GOVERNMENT_GRANT = (auto(), "g")
    FORECAST = (auto(), "f")
