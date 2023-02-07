import datetime as datetime
from dataclasses import dataclass
from typing import Dict

import requests

_EXCHANGE_RATES_NBP_BASE_URL = "https://static.nbp.pl/dane/kursy/xml/"


@dataclass
class NBPExchangeRate:
    name: str
    exchange_rate_x_pln: str
    code: str
    multiplier: int


def get_nbp_exchange_rates(year: int) -> Dict[datetime.datetime, str]:
    lp: int = 1
    out = {}
    for month in range(1, 13):
        for day in range(1, 32):
            try:
                dt = datetime.datetime(year=year, month=month, day=day)
                if dt > datetime.datetime.now():
                    return out
                url = __build_nbp_exchange_rate_urls(dt=dt, lp=lp)
                print(url)
                response = requests.get(url)
                if response.status_code != 404:
                    lp += 1
                    out[dt] = str(response.content)
            except ValueError:
                # who cares
                pass
    return out


def __build_nbp_exchange_rate_urls(dt: datetime.datetime,
                                   lp: int,
                                   table: str = "a",
                                   extension: str = ".xml") -> str:
    return _EXCHANGE_RATES_NBP_BASE_URL + __build_nbp_exchange_rates_filename(dt, lp, table,
                                                                              extension)


def __build_nbp_exchange_rates_filename(dt: datetime.datetime,
                                        lp: int,
                                        table: str = "a",
                                        extension: str = ".xml") -> str:
    # https://static.nbp.pl/dane/kursy/xml/a019z230127.xml
    return f"{table}{__lp_to_nbp_lp(lp, 2)}z" \
           f"{str(dt.year)[2:]}{__lp_to_nbp_lp(dt.month, 1)}{__lp_to_nbp_lp(dt.day, 1)}{extension}"


def __lp_to_nbp_lp(lp: int, how_many_trailing_zeros: int) -> str:
    lp_str = str(lp)
    return ((how_many_trailing_zeros + 1) - len(lp_str)) * "0" + lp_str
