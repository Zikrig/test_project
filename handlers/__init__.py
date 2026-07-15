from aiogram import Router

from handlers.registration import router as registration_router
from handlers.start import router as start_router

router = Router()
router.include_router(start_router)
router.include_router(registration_router)
