from pydantic import BaseModel

class ServerStatistics(BaseModel):
    active_members: int
    total_members: int
    members_by_status: dict[str, int]