from fastapi import APIRouter


router = APIRouter(prefix="/api", tags=["System"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "Ausome Seals API"}


@router.get("/products")
def products():
    return [{
        "id": 1,
        "name": "Oil Seal",
        "category": "Heavy machinery sealing products",
        "description": (
            "Large custom oil seals for rolling mill roll bearing areas and "
            "demanding industrial equipment."
        ),
    }]
