import sys

from double_click import echo

from tendies import TASTY_SESSION, TW_URL
from tendies.utils import dict_as_snake


class Stock:
    option_expirations = []

    def __init__(self, symbol):
        response = TASTY_SESSION.get(f'{TW_URL}/market-metrics', params=dict(symbols=symbol))
        if response.status_code != 200:
            echo(response)
            sys.exit(1)

        content = response.json()['data']['items']
        if len(content) == 0:
            echo(f'#{symbol} does not exist')
            sys.exit(1)

        for key, value in dict_as_snake(content[0]).items():
            if key == 'option_expiration_implied_volatilities':
                key = 'option_expirations'
                value = [dict_as_snake(exp_day) for exp_day in value[:25]]  # Not putting options dated a year out

            setattr(self, key, value)

    @property
    def best_expiration_ivs(self):
        """Returns Dates where a sharp declined from the prior or following day.
        It's arbitrary but get date if IV is lower than the following day.
        :return:
        """
        # Lot of room for improvement here
        res = []
        oeiv_len = len(self.option_expirations)
        for i in range(oeiv_len):
            iv = self.option_expirations[i].get('implied_volatility')
            if not iv:
                continue

            iv = float(iv)
            next_day_iv = self.option_expirations[i+1].get('implied_volatility') if i != (oeiv_len - 1) else None

            if next_day_iv and iv/float(next_day_iv) < 1:
                res.append(self.option_expirations[i])

        return res

