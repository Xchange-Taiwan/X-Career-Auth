from pydantic import EmailStr, BaseModel

class UpdatePasswordDAO(BaseModel):
    pass_hash: str
    pass_salt: str
    email: EmailStr
