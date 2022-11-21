from fastapi import APIRouter

from skill_management.controller import test, plan, skill

api_router: APIRouter = APIRouter()
# api_router.include_router(test.test_router)
api_router.include_router(plan.plan_router)
api_router.include_router(skill.skill_router)