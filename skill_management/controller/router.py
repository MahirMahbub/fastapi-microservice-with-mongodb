from fastapi import APIRouter

from skill_management.controller import test

api_router: APIRouter = APIRouter()
api_router.include_router(test.test_router)
