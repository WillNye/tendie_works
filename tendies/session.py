import json
import os
import sys
from datetime import datetime as dt, timedelta
from time import sleep

import requests
from double_click import echo, User, UserSession

from tendies.config import TW_TOKEN_DIR, TW_URL


class TastyUser(User):

    @classmethod
    def login(cls, username: str = None, password: str = None, **kwargs):
        tasty_user = cls(username=username, password=password, **kwargs)

        if os.path.exists(TW_TOKEN_DIR):
            min_age = dt.now() - timedelta(minutes=5)
            filetime = dt.fromtimestamp(os.path.getmtime(TW_TOKEN_DIR))
            try:
                with open(TW_TOKEN_DIR) as config:
                    credentials = json.loads(config.read())
                    if filetime > min_age:
                        for key, value in credentials.items():
                            setattr(tasty_user, key, value)
                    else:
                        tasty_user.authenticate()
            except json.decoder.JSONDecodeError:
                echo(f'Profile format invalid. Defaulting to {username}')
                tasty_user.authenticate()
                return tasty_user
        else:
            tasty_user.authenticate()

        return tasty_user

    @staticmethod
    def get_user(username: str, password: str) -> dict:
        response = requests.post(url=f'{TW_URL}/sessions', json=dict(login=username, password=password))
        if response.status_code == 201:
            data = response.json()['data']
            data['user']['session-token'] = data['session-token']
            return data['user']
        else:
            echo(response)
            sys.exit(1)

    def authenticate(self):
        """Setup local config and options for source and artifact classifications
        :return:
        """
        if self.username and self.password:
            credentials = self.get_user(self.username, self.password)
            try:
                with open(TW_TOKEN_DIR, 'w') as f:
                    f.write(json.dumps(credentials, indent=2))

                for key, value in credentials.items():
                    setattr(self, key, value)
            except json.decoder.JSONDecodeError:
                sleep(.1)
                min_age = dt.now() - timedelta(minutes=5)
                filetime = dt.fromtimestamp(os.path.getmtime(TW_TOKEN_DIR))
                if filetime > min_age:
                    self.authenticate()

            return {'Authorization': self.get("session-token")}


class TastySession(UserSession):
    user: TastyUser = TastyUser.login()
    max_concurrency = 50
