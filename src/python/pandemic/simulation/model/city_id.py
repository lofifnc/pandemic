
class Card:
    pass

    CITY = 1
    EVENT = 2
    EPIDEMIC = 3

    @staticmethod
    def card_type(card: int):
        if 0 < card <= 48:
           return Card.CITY
        elif card <= 54:
           return Card.EPIDEMIC
        elif card <= 59:
           return Card.EVENT
        raise ValueError


class City(Card):
    ALGIERS = 1
    ATLANTA = 2
    BAGHDAD = 3
    BANGKOK = 4
    BEIJING = 5
    BOGOTA = 6
    BUENOS_ARIES = 7
    CAIRO = 8
    CHENNAI = 9
    CHICAGO = 10
    DELHI = 11
    ESSEN = 12
    HO_CHI_MINH_CITY = 13
    HONG_KONG = 14
    ISTANBUL = 15
    JAKARTA = 16
    JOHANNESBURG = 17
    KARACHI = 18
    KHARTOUM = 19
    KINSHASA = 20
    KOLKATA = 21
    LAGOS = 22
    LIMA = 23
    LONDON = 24
    LOS_ANGELES = 25
    MADRID = 26
    MANILA = 27
    MEXICO_CITY = 28
    MIAMI = 29
    MILAN = 30
    MONTREAL = 31
    MOSCOW = 32
    MUMBAI = 33
    NEW_YORK = 34
    OSAKA = 35
    PARIS = 36
    RIYADH = 37
    SAN_FRANCISCO = 38
    SANTIAGO = 39
    SAO_PAULO = 40
    SEOUL = 41
    SHANGHAI = 42
    ST_PETERSBURG = 43
    SYDNEY = 44
    TAIPEI = 45
    TEHRAN = 46
    TOKYO = 47
    WASHINGTON = 48

    __members__ = range(1, 49)


class EpidemicCard(Card):
    EPIDEMIC_CARD_1 = 49
    EPIDEMIC_CARD_2 = 50
    EPIDEMIC_CARD_3 = 51
    EPIDEMIC_CARD_4 = 52
    EPIDEMIC_CARD_5 = 53
    EPIDEMIC_CARD_6 = 54

    __members__ = range(49, 55)


class EventCard(Card):

    RESILIENT_POPULATION = 55
    ONE_QUIET_NIGHT = 56
    AIRLIFT = 57
    GOVERNMENT_GRANT = 58
    FORECAST = 59

    __members__ = range(55, 60)
