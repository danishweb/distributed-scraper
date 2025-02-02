from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProxyBase(BaseModel):
    url: str
    is_active: bool = Field(default=True)
    blacklisted: bool = Field(default=False)
    failures: int = Field(default=0)
    last_checked: datetime = Field(default_factory=datetime.now)
    last_failure: Optional[datetime] = Field(default=None)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

class ProxyCreate(ProxyBase):
    pass

class ProxyUpdate(BaseModel):
    is_active: Optional[bool] = None
    blacklisted: Optional[bool] = None
    failures: Optional[int] = None
    last_checked: Optional[datetime] = None
    last_failure: Optional[datetime] = None

class ProxyInDB(ProxyBase):
    id: str = Field(alias="_id")