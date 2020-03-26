import os
from pathlib import Path

from double_click import Model

from tendies.config import BASE_DIR
from tendies.utils import dict_as_snake
from tendies import TASTY_SESSION, TW_URL


class TastyAccount(Model):
    _session = TASTY_SESSION
    _url = f'{TW_URL}/customers/me/accounts'  # route to list accounts
    _ttl = 5
    _cache_key = Path(os.path.join(BASE_DIR, 'accounts.json'))
    _obj_identifier = 'account_number'
    account_number = None

    def _api_retrieve(self) -> list:
        response = self._session.get(self._url)
        if response.status_code == 200:
            accounts = response.json().get('data', {}).get('items', [])
            return [dict_as_snake(acc.get('account')) for acc in accounts if acc.get('authority-level') == 'owner']
        else:
            return []

    @property
    def balance(self) -> dict:
        """
        :return: dict(
            cash_balance, long_equity_value, short_equity_value, long_derivative_value,  short_derivative_value,
            long_futures_value, short_futures_value, long_futures_derivative_value,
            short_futures_derivative_value, debit_margin_balance,  long_margineable_value, short_margineable_value,
            margin_equity, equity_buying_power, derivative_buying_power, day_trading_buying_power,
            futures_margin_requirement, available_trading_funds, maintenance_requirement, maintenance_call_value,
            reg_t_call_value, day_trading_call_value, day_equity_call_value, net_liquidating_value,
            cash_available_to_withdraw, day_trade_excess, pending_cash, pending_cash_effect, snapshot_date,
            reg_t_margin_requirement, futures_overnight_margin_requirement, futures_intraday_margin_requirement
        )
        """
        res = self._session.get(f'{TW_URL}/accounts/{self.account_number}/balances')
        return dict_as_snake(res.json()['data']) if res.status_code == 200 else {}

    @property
    def positions(self) -> list:
        """
        :return: [dict(
            symbol, instrument_type, underlying_symbol, quantity, quantity_direction, close_price, average_open_price,
            average_yearly_market_close_price, average_daily_market_close_price, mark, mark_price, multiplier,
            cost_effect, is_suppressed, is_frozen, restricted_quantity, expires_at, realized_day_gain,
            realized_day_gain_effect, realized_day_gain_date, realized_today, realized_today_effect,
            realized_today_date, created_at, updated_at
        )]
        """
        res = self._session.get(f'{TW_URL}/accounts/{self.account_number}/positions')
        return [dict_as_snake(item) for item in res.json()['data']['items']] if res.status_code == 200 else []

    @property
    def live_orders(self) -> list:
        """
        :return: [dict(
            id, time_in_force, order_type, size, underlying_symbol, price, price_effect, status, cancellable, editable,
            edited, ext_exchange_order_number, ext_client_order_id, ext_global_order_number, received_at, updated_at,
            terminal_at, legs
        )]
        """
        res = self._session.get(f'{TW_URL}/accounts/{self.account_number}/orders/live')
        return [dict_as_snake(item) for item in res.json()['data']['items']] if res.status_code == 200 else []

    @property
    def history(self) -> list:
        """
        :return: [dict(
            id, symbol, instrument_type, underlying_symbol, transaction_type, transaction_sub_type, description,
            action, quantity, price, executed_at, transaction_date, value, value_effect, regulatory_fees, order_id,
            regulatory_fees_effect, clearing_fees, clearing_fees_effect, net_value, net_value_effect, commission,
            commission_effect, proprietary_index_option_fees, proprietary_index_option_fees_effect, is_estimated_fee,
            ext_exchange_order_number, ext_global_order_number, ext_group_id, ext_group_fill_id, ext_exec_id, exchange
        )]
        """
        res = self._session.get(f'{TW_URL}/accounts/{self.account_number}/transactions')
        return [dict_as_snake(item) for item in res.json()['data']['items']] if res.status_code == 200 else []
