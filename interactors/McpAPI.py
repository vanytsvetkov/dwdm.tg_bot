# import json
import redis as r
import requests
import models.MCP
# from datetime import timedelta
from models.Credits import Credits
from models.MCP.Response import ProcessResponse


class McpAPI:
    def __init__(self, credits: Credits, use_db=False, **kwargs):
        self.url = credits.mcp.url
        self.username = credits.mcp.username
        self.password = credits.mcp.password

        self.use_db = use_db
        if self.use_db:
            self.redis = r.Redis(host=credits.redis.host, port=credits.redis.port, db=credits.redis.db)

        self.token = None
        self.response = None
        if self.url:
            self.requestsSession = requests.session()
            self.requestsSession.verify = kwargs.get('verify', True)

            self.requestsSession.headers = {
                'accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
                }
        else:
            self.requestsSession = None

    def request(self, method: str, endpoint: str, headers: dict = None, params: dict = None, data: dict = None, token_free: bool = False, **kwargs) -> dict:
        if not token_free:
            self.requestsSession.headers.setdefault('Authorization', f'Bearer {self.get_token()}')

        if self.requestsSession:
            self.response = self.requestsSession.request(method, f'https://{self.url}/{endpoint}', headers=headers, params=params, data=data, **kwargs)
            match self.response.status_code:
                # 200 – OK | 201 – Created
                case 200 | 201:
                    return {'response': self.response.json(), 'success': self.response.ok, 'status_code': self.response.status_code}
                # 204 – No Content
                case 204:
                    return {'message': self.response.text, 'success': self.response.ok, 'status_code': self.response.status_code}
                case _:
                    return {'errors': ['API Error'], 'message': self.response.text, 'success': self.response.ok, 'status_code': self.response.status_code}
        else:
            return {'errors': ['Wrong URL'], 'message': 'Please specify the correct MCP\'s url or pass one via kwargs.'}

    def get_token(self) -> str:
        if self.use_db:
            self.token = self.redis.get('dwdm.tg_bot.mcp.token')

        if not self.token:
            self.token = self.gen_token()

        return self.token

    def gen_token(self) -> str:
        data = {
            'username': self.username,
            'password': self.password,
            'grant_type': 'password'
            }

        response = ProcessResponse(
            self.request('POST', 'tron/api/v1/oauth2/tokens', data=data, token_free=True),
            model='OAuth2Token'
            ).response

        self.token = response.accessToken
        if self.use_db:
            self.redis.set('dwdm.tg_bot.mcp.token', self.token)
            # self.redis.expire('dwdm.tg_bot.mcp.token', timedelta(minutes=30))
            self.redis.expire('dwdm.tg_bot.mcp.token', response.expiresIn)

        return self.token

    def get_networkConstructs(self, params: dict = None, **kwargs) -> models.MCP.networkConstructs:
        return ProcessResponse(
            self.request('GET', 'nsi/api/search/networkConstructs', params=params, **kwargs),
            model='networkConstructs'
            )

    def get_Ciena6500(self) -> models.MCP.networkConstructs:
        params = {
            'resourceType': '6500',
            'limit': '10',
        }
        return self.get_networkConstructs(params=params)
