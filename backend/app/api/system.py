from fastapi import APIRouter


router = APIRouter(prefix="/api", tags=["System"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "Ausome Seals API"}


@router.get("/products")
def products():
    return [{
        "id": 1,
        "name": "Rolling Mill Seals",
        "category": "Steel rolling mill sealing products",
        "description": (
            "Heavy-duty oil seals, water seals, fabric-reinforced seals, split seals, "
            "and custom sealing products for steel rolling mill equipment."
        ),
    }]
