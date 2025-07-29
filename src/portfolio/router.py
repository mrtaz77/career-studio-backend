from fastapi import APIRouter
from fastapi.security import HTTPBearer

router = APIRouter(tags=["Portfolio"], prefix="/portfolio")
security = HTTPBearer(auto_error=False, scheme_name="BearerAuth")
