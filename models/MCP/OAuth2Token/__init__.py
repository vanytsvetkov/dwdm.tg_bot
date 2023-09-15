from pydantic import BaseModel
from datetime import datetime


class LoginDetail(BaseModel):
    ipAddress: str
    sessionId: str
    sessionType: str
    time: datetime
    userAgent: str


class OAuth2Token(BaseModel):
    accessToken:	str
    createdTime:	datetime
    expirationTime:	datetime
    # Token expires in timeout seconds from created time
    expiresIn:	int

    failedLoginAttempts:	int
    inactiveExpirationTime:	datetime | None
    # Deprecated. Only successfull logins are stored.
    isSuccessful:	bool

    lastSuccessIpAddress:	str
    lastSuccessLogin:	datetime
    loginDetail:	LoginDetail
    # Represents the Access-Challenge State attribute
    radiusState:	str

    tokenType:	str
    user:	str
    userTenantUuid:	str
