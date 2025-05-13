"""
API routes package.
"""

from fastapi import APIRouter

from arkos.api.routes.auth import router as auth_router
from arkos.api.routes.auth_2fa import router as auth_2fa_router
from arkos.api.routes.cameras import router as cameras_router
from arkos.api.routes.config import router as config_router
from arkos.api.routes.events import router as events_router
from arkos.api.routes.notifications import router as notifications_router
from arkos.api.routes.recordings import router as recordings_router
from arkos.api.routes.stats import router as stats_router
from arkos.api.routes.system import router as system_router
from arkos.api.routes.users import router as users_router

# Create the main router
router = APIRouter()

# Include all routers
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(auth_2fa_router, prefix="/2fa", tags=["auth"])
router.include_router(cameras_router, prefix="/cameras", tags=["cameras"])
router.include_router(config_router, prefix="/config", tags=["config"])
router.include_router(events_router, prefix="/events", tags=["events"])
router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
router.include_router(recordings_router, prefix="/recordings", tags=["recordings"])
router.include_router(stats_router, prefix="/stats", tags=["stats"])
router.include_router(system_router, prefix="/system", tags=["system"])
router.include_router(users_router, prefix="/users", tags=["users"])
