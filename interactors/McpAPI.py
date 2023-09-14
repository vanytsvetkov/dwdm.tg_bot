import json
import requests
from models.Credits import Credits


class McpAPI:
    def __init__(self, credits: Credits, **kwargs):
        self.url = credits.mcp.url
        self.username = credits.mcp.username
        self.password = credits.mcp.password

        if self.url:
            self.requestsSession = requests.session()
            self.requestsSession.verify = kwargs.get('verify', True)

            self.requestsSession.headers = {
                'accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
                }

        else:
            self.requestsSession = None

    def request(self, method: str, endpoint: str, headers: dict = None, params: dict = None, data: dict = None, **kwargs) -> dict:
        self.requestsSession.headers.update('Authorization', f'Bearer: {self.get_token()}')

        if self.requestsSession:
            response = self.requestsSession.request(method, f'https://{self.url}/{endpoint}', headers=headers, params=params, json=data, **kwargs)
            match response.status_code:
                # 200 – OK | 201 – Created
                case 200 | 201:
                    return {**response.json(), 'success': response.ok, 'status_code': response.status_code}
                # 204 – No Content
                case 204:
                    return {'message': response.text, 'success': response.ok, 'status_code': response.status_code}
                case _:
                    return {'errors': ['API Error'], 'message': response.text, 'success': response.ok, 'status_code': response.status_code}
        else:
            return {'errors': ['Wrong URL'], 'message': 'Please specify the correct MCP\'s url or pass one via kwargs.'}

    def get_token(self) -> str:
        # TODO: to get token from redis db
        # if not (token := redis.get('dwdm.tg_bot.mcp.token')):
        if not (token := None):
            token = self.gen_token()

        return token

    def gen_token(self) -> str:
        data = {
            'username': self.username,
            'password': self.password,
            'grant_type': 'password'
            }

        tokens = self.request('POST', 'tron/api/v1/oauth2/tokens', data=data)

        print(json.dumps(tokens, indent=2))

        token = '1234'
        # TODO: save token to redis db to 30 min
        # redis.set('dwdm.tg_bot.mcp.token', token)
        # redis.expire('dwdm.tg_bot.mcp.token', timedelta(30))

        return token
