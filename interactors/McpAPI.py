import vars
import redis as r
import requests
from datetime import timedelta
from models.Creds import Creds
from models.MCP.Response import ResponseType, ProcessResponse


class McpAPI:
    def __init__(self, creds: Creds, use_db=True, **kwargs):
        self.url = creds.mcp.url
        self.username = creds.mcp.username
        self.password = creds.mcp.password

        self.use_db = use_db
        if self.use_db:
            self.redis = r.Redis(
                host=creds.redis.host,
                port=creds.redis.port,
                db=creds.redis.db,
                decode_responses=True,
                charset='utf-8'
                )

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

    def request(self, method: str, endpoint: str, headers: dict = None, params: dict = None, data: dict = None, json: dict = None, token_free: bool = False, **kwargs) -> dict:
        self.requestsSession.headers.pop('Authorization', None)
        if not token_free:
            self.requestsSession.headers.setdefault('Authorization', f'Bearer {self.get_token()}')

        if self.requestsSession:
            self.response = self.requestsSession.request(method, f'https://{self.url}/{endpoint}', headers=headers, params=params, data=data, json=json, **kwargs)
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
            self.token = self.redis.get(f'{vars.PROJECT_NAME}.mcp.token')

        if not self.token:
            self.token = self.gen_token()

        return self.token

    def gen_token(self) -> str:
        data = {
            'username': self.username,
            'password': self.password,
            'grant_type': 'password'
            }

        post = ProcessResponse(
            self.request('POST', 'tron/api/v1/oauth2/tokens', data=data, token_free=True),
            model='OAuth2Token'
            )

        if not post.success:
            return str()

        self.token = post.response.accessToken
        if self.use_db:
            self.redis.set(f'{vars.PROJECT_NAME}.mcp.token', self.token)
            self.redis.expire(f'{vars.PROJECT_NAME}.mcp.token', timedelta(minutes=30))

        return self.token

    def get_networkConstructs(self, params: dict = None, **kwargs) -> ResponseType:
        return ProcessResponse(
            self.request('GET', 'nsi/api/search/networkConstructs', params=params, **kwargs),
            model='networkConstructs'
            )

    def get_Ciena6500(self) -> ResponseType:
        params = {
            'typeGroup': 'Ciena6500',
            'limit': '1000',
            }
        return self.get_networkConstructs(params=params)

    def get_CienaWS(self) -> ResponseType:
        params = {
            'typeGroup': 'CienaWaveserver',
            'limit': '1000',
            }
        return self.get_networkConstructs(params=params)

    def get_fres(self, displayName: str = None, serviceClass: list = None, limit: int = 1, **kwargs) -> ResponseType:
        if serviceClass is None:
            serviceClass = ['Transport Client', 'Photonic']

        params = {
            'resourceState': 'discovered',
            'serviceClass': ', '.join(serviceClass),
            'limit': limit
            }

        if displayName:
            params.update(
                {
                    'searchText': displayName,
                    'searchFields': 'data.attributes.displayData.displayName',
                    'searchType': 'match',
                    }
                )

        return ProcessResponse(
            self.request('GET', 'nsi/api/search/fres', params=params, **kwargs),
            model='fres'
            )

    def patch_fre(self, id_: str, customerName: str = None, **kwargs) -> ResponseType:
        headers = {
            'accept': 'application/json-patch+json',
            'Content-Type': 'application/json',
            }
        json_data = {}
        if customerName:
            json_data = {
                'operations': [
                        {
                            'op': 'replace',
                            'attributes': {
                                'customerName': customerName,
                                },
                            },
                        ],
                }
        return ProcessResponse(
            self.request('PATCH', f'nsi/api/fres/{id_}', headers=headers, json=json_data, **kwargs),
            model='fres'
            )

    def get_serviceTopology(self, id_: str, **kwargs) -> ResponseType:
        params = {
            'unidirectional': 'true',
            'include': 'tpes'
            }
        return ProcessResponse(
            self.request('GET', f'revell/api/v3/serviceTopology/{id_}', params=params, **kwargs),
            model='serviceTopologies'
            )

    def get_tpes(self, networkConstructId: str = None, **kwargs) -> ResponseType:
        params = {
                'limit': '1000',
            }
        if networkConstructId:
            params.setdefault('networkConstruct.id', networkConstructId)

        return ProcessResponse(
            self.request('GET', 'nsi/api/tpes', params=params, **kwargs),
            model='tpes'
            )

    def get_supported_fres(self, tpeId: str = None, **kwargs) -> ResponseType:
        params = {'limit': '1000'}
        if tpeId:
            params.setdefault('tpeId', tpeId)

        return ProcessResponse(
            self.request('GET', 'nsi/api/fres', params=params, **kwargs),
            model='fres'
            )
