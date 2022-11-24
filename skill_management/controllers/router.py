from fastapi import APIRouter

from skill_management.controllers import test, plan, skill, profile, experience, education, file, designation

api_router: APIRouter = APIRouter()
api_router.include_router(test.test_router)
api_router.include_router(plan.plan_router)
api_router.include_router(skill.skill_router)
api_router.include_router(profile.profile_router)
api_router.include_router(experience.experience_router)
api_router.include_router(education.education_router)
api_router.include_router(file.file_router)
api_router.include_router(designation.designation_router)