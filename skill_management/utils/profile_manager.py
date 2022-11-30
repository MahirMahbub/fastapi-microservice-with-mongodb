from beanie import Document
from fastapi import Request

from skill_management.repositories.profile import ProfileRepository


async def get_profile(request: Request, user_id: str) -> Document | None:
    user_auth_data = await request.app.state.redis_connection.hgetall(user_id)

    if user_auth_data:
        email = user_auth_data['email']
        if email is None:
            return None
        profile_data = await ProfileRepository().get_by_query({"user_id": email})
        return profile_data
    return None
