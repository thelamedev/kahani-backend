from datetime import datetime
from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

router = APIRouter(tags=["Root"])
bootup_time = datetime.now()


router.mount("/public", StaticFiles(directory="public"), name="public")


@router.get("/health")
async def health_check():
    uptime = datetime.now() - bootup_time
    return {"status": "Healthy", "uptime": f"{uptime}"}
