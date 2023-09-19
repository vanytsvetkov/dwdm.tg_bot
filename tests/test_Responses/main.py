from models.MCP.Response import ProcessResponse

response = {
    'response': {
      "failedLoginAttempts": 0,
      "lastSuccessIpAddress": "83.243.69.186",
      "lastSuccessLogin": "2023-09-15 12:22:10.779646+00:00",
      "postLoginMessage": None,
      "user": "1d6a681f-32e2-4790-a3a3-270fa0579d50",
      "loginDetail": {
        "ipAddress": "83.243.69.186",
        "sessionId": "833165ca-2e6f-49d0-a014-40d97b2a1f84",
        "sessionType": "User",
        "time": "2023-09-15T12:23:28.245471Z",
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        },
      "expiresIn": 2592000,
      "accessToken": "f60e6f7dc0fa5d9d5ee4",
      "tokenType": "bearer",
      "createdTime": "2023-09-15T12:23:28.245471Z",
      "expirationTime": "2023-10-15T12:23:28.245471Z",
      "inactiveExpirationTime": None,
      "isSuccessful": True,
      "userTenantUuid": "-1",
      "radiusState": ""
      },
    'success': True,
    'status_code': 200
    }

data_P = ProcessResponse(response=response, model='OAuth2Token')

