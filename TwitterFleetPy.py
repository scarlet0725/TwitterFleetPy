import base64

import requests
from requests_oauthlib import OAuth1


class TwitterFleetPy:
    def __init__(self):
        # Official API Token of Twitter for Android
        self.ck = '3nVuSoBZnx6U4vzUxf5w'
        self.cs = 'Bcs59EFbbsdF6Sl9Ng71smgStWEGwXXKSjYvPVt7qys'
        self.header_tz = 'Asia/Tokyo'
        self.header_language = 'ja-JP'
        self.twitter_app_ver = '9.0.0-release.00'
        self.client_uuid = 'a3b9d2dc-f148-4f95-8a0f-36ffaf0879c7'
        self.device_id = '801d23384cb5451a'
        self.adid = 'a7e8ab7c-22f4-4ec7-9d79-bf6a1fe9dc8d'
        self.oauth_token_key = ''
        self.oauth_token_secret = ''
        self.kdt = ''
        self.oauth1 = ''
        self.req_header = {
            'user-agent': 'TwitterAndroid/9.0.0-release.00 (29000000-r-0) Android+SDK+built+for+x86/7.1.1 (Google;Android+SDK+built+for+x86;google;sdk_google_phone_x86;0;;1;2013)',
            'accept-encoding': 'gzip, deflate',
            'x-twitter-client-adid': self.adid,
            'timezone': self.header_tz,
            'x-twitter-client-limit-ad-tracking': '0',
            'x-twitter-client': 'TwitterAndroid',
            'x-twitter-client-version': self.twitter_app_ver,
            'x-twitter-client-language': self.header_language,
            'x-twitter-client-deviceid': self.device_id,
            'x-twitter-api-version': '5',
            'optimize-body': 'true',
            'accept': 'application/json',
            'x-b3-traceid': 'f164f5d9a8f19d09',
            'x-twitter-active-user': 'yes'
        }

    def login(self, identifier, password):
        # ログイン処理
        header_auth = self.ck + ':' + self.cs

        header_auth = header_auth.encode()
        header_auth = base64.b64encode(header_auth).decode()

        oauth2_req_header = self.req_header
        s = 'Basic ' + header_auth
        oauth2_req_header['authorization'] = s

        oauth2_endpoint = 'https://api.twitter.com/oauth2/token'
        oauth2_req_param = 'grant_type=client_credentials'
        oauth2_req = requests.post(oauth2_endpoint, headers=oauth2_req_header, params=oauth2_req_param)
        if oauth2_req.status_code != 200:
            raise Exception(oauth2_req.content.decode())
        bearer_token = oauth2_req.json()['access_token']

        activate_endpoint = 'https://api.twitter.com/1.1/guest/activate.json'
        activate_auth_header = 'Bearer ' + bearer_token
        activate_req_header = self.req_header
        activate_req_header['authorization'] = activate_auth_header
        activate_req = requests.post(activate_endpoint, headers=activate_req_header)
        if activate_req.status_code != 200:
            raise Exception(activate_req.content.decode())
        guest_token = activate_req.json()['guest_token']

        xauth_endpoint = 'https://api.twitter.com/auth/1/xauth_password.json'
        xauth_req_header = activate_req_header
        xauth_req_header['x-guest-token'] = guest_token
        xauth_data = {
            'x_auth_identifier': identifier,
            'x_auth_password': password,
            'send_error_codes': 'true',
            'x_auth_login_challenge': '1',
            'x_auth_login_verification': '1',
            'ui_metrics': ''
        }

        xauth_req = requests.post(xauth_endpoint, headers=xauth_req_header, data=xauth_data)
        if xauth_req.status_code != 200:
            raise Exception(xauth_req.content.decode())
        self.oauth_token_key = xauth_req.json()['oauth_token']
        self.oauth_token_secret = xauth_req.json()['oauth_token_secret']
        self.kdt = xauth_req.json()['kdt']
        self.oauth1 = OAuth1(self.ck, self.cs, self.oauth_token_key, self.oauth_token_secret)

    def init_oauth(self, oauth_token, oauth_secret, kdt):
        self.oauth_token_key = oauth_token
        self.oauth_token_secret = oauth_secret
        self.kdt = kdt
        self.oauth1 = OAuth1(self.ck, self.cs, self.oauth_token_key, self.oauth_token_secret)

    def show_OauthToken(self):
        if (self.oauth_token_key or self.oauth_token_secret or self.kdt) is None:
            raise Exception('The Values are not set.')
        print(f'OAuth token is {self.oauth_token_key}.')
        print(f'OAuth token secret is {self.oauth_token_secret}.')
        print(f'kdt is {self.kdt}.')

    def get_fleet(self, screenname):
        fleet_endpoint = 'https://api.twitter.com/fleets/v1/user_fleets/'

        # Convert screen name to id
        search_endpoint = 'https://api.twitter.com/1.1/users/show.json'
        params = {
            'screen_name': screenname,
        }
        req_header = {
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAFXzAwAAAAAAMHCxpeSDG1gLNLghVe8d74hl6k4%3DRUMF4xAQLsbeBhTSRrCiQpJtxoGWeyHrDb5te2jpGskWDFW82F'
        }
        user = requests.get(search_endpoint, params=params, headers=req_header)
        if user.status_code != 200:
            raise Exception(user.content.decode())
        tw_id = user.json()['id_str']

        # Get fleet

        fleet_header = self.req_header

        fleet_params = {
            'user_id': tw_id,
        }
        fleet = requests.get(fleet_endpoint, headers=fleet_header, params=fleet_params, auth=self.oauth1)
        if fleet.status_code != 200:
            raise Exception(fleet.content.decode())

        url_list = []
        fleet_data = fleet.json()['fleet_threads']
        for i in fleet_data:
            for j in i['fleets']:
                url_list.append((j['fleet_id'], j['media_entity']['media_url_https']))

        return url_list
