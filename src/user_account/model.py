from datetime import datetime
from typing import Mapping

from pydantic import UUID4, BaseModel, ConfigDict


class UserAccount(BaseModel):
    model_config = ConfigDict(revalidate_instances='always')

    guid: UUID4
    email: str
    password: str
    f_name: str
    l_name: str | None = None
    c_at: datetime

    @classmethod
    def from_db_item(cls, item: Mapping):
        return UserAccount.model_validate(item)
