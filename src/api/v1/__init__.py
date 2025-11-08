from fastapi import APIRouter
from .products import router as products_router

router = APIRouter()
router.include_router(products_router)

__all__ = ["router"]
