from db.model import *
from db.session import *


def dump():
    country = Countries(name='Turkey')
    session.add(country)

    country_1 = Countries(name='Russia')
    session.add(country_1)

    city_1 = Cities(name='Moscow')
    session.add(city_1)
    country_1.cities.append(city_1)

    city_2 = Cities(name='Saint P')
    session.add(city_2)
    country_1.cities.append(city_2)

    city = Cities(name='Kas')
    session.add(city)
    country.cities.append(city)

    currency = Currencies(
        name="RUB-USDT",
        city=city,
    )
    session.add(currency)

    slot = Slots(
        name="8th april 8am",
        date="april 6pm",
        currency=currency)
    session.add(slot)

    slot_1 = Slots(
        name="9th April 2 pm",
        date="april 6pm",
        currency=currency)
    session.add(slot_1)

    session.commit()


if __name__ == '__main__':
    dump()
