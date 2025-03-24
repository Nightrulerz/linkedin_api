from pydantic import BaseModel


class AuthModel(BaseModel):
    api_key: str


class ProfileModel(AuthModel):
    username: str
    password: str


class ConnectionsModel(ProfileModel):
    pagination_id: str = None