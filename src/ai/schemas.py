from pydantic import BaseModel


class OptimizaitonRequest(BaseModel):
    description: str
