from pydantic import BaseModel, Field

class TodoRequest(BaseModel):
    title : str = Field(min_length=3, max_length=100)
    description : str = Field(min_length=3, max_length=100)
    priority : int = Field(default=1, gt=0, lt=6)
    complete : bool = Field(default=False)

class UserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    firstname: str = Field(min_length=3, max_length=50)
    lastname: str = Field()
    email: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8)
    is_active: bool = Field(default=True)
    role: str = Field(default="user")
    created_at: str = Field(default="CURRENT_TIMESTAMP")
    last_login: str = Field(default=None)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserVerification(BaseModel):
    password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)