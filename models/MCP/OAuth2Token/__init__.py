from pydantic import BaseModel
from datetime import datetime


class LoginDetail(BaseModel):
    ipAddress: str = str()
    sessionId: str = str()
    sessionType: str = str()
    time: datetime = datetime.now()
    userAgent: str = str()


class OAuth2Token(BaseModel):
    accessToken:	str = str()
    createdTime:	datetime = datetime.now()
    expirationTime:	datetime = datetime.now()
    # Token expires in timeout seconds from created time
    expiresIn:	int = int()

    failedLoginAttempts:	int = int()
    inactiveExpirationTime:	datetime | None = None
    # Deprecated. Only successfull logins are stored.
    isSuccessful:	bool = bool()

    lastSuccessIpAddress:	str = str()
    lastSuccessLogin:	datetime = datetime.now()
    loginDetail:	LoginDetail = LoginDetail()
    # Represents the Access-Challenge State attribute
    radiusState:	str = str()

    tokenType:	str = str()
    user:	str = str()
    userTenantUuid:	str = str()
