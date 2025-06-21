from datetime import datetime
from fastapi import APIRouter

router = APIRouter()
bootup_time = datetime.now()


@router.get("/health")
async def health_check():
    uptime = datetime.now() - bootup_time
    return {"status": "Healthy", "uptime": f"{uptime}"}
