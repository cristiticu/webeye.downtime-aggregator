from datetime import datetime
from typing import Mapping
from pydantic import UUID4, BaseModel


class MonitoredWebpage(BaseModel):
    guid: UUID4
    u_guid: UUID4
    url: str
    screenshot_m_at: datetime | None = None
    c_at: datetime

    @classmethod
    def from_db_item(cls, item: Mapping):
        return MonitoredWebpage.model_validate(item)
