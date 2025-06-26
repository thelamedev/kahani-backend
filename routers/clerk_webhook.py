from datetime import datetime
import os
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import select

from shared.database import AsyncSession, get_db
from shared.models.user import User

router = APIRouter(prefix="/clerk")

CLERK_WEBHOOK_SECRET = os.getenv("CLERK_WEBHOOK_SECRET")
if not CLERK_WEBHOOK_SECRET:
    raise Exception("'CLERK_WEBHOOK_SECRET' not set in the environemt")


@router.post("/webhook")
async def clerk_auth_webhook(
    req: Request,
    res: Response,
    db: AsyncSession = Depends(get_db),
):
    body = await req.json()
    print("Clerk Webhook\n", body)

    event_type = body["type"]
    event_data = body["data"]

    match event_type:
        case "user.created":
            # TODO: add the created user in the databae without a password, set the source to clerk.
            primary_email_id = event_data["primary_email_address_id"]
            primary_email = list(
                filter(
                    lambda x: x["id"] == primary_email_id,
                    event_data["email_addresses"],
                )
            )[0]["email_address"]
            new_user_doc = User(
                first_name=event_data["first_name"],
                last_name=event_data["last_name"],
                email=primary_email,
                password_hash="",
                source="clerk",
                source_id=event_data["id"],
            )

            db.add(new_user_doc)
        case "user.updated":
            # TODO: update the user based on the email and
            primary_email_id = event_data["primary_email_address_id"]
            primary_email = list(
                filter(
                    lambda x: x["id"] == primary_email_id,
                    event_data["email_addresses"],
                )
            )[0]["email_address"]

            user_query = select(User).where(User.email == primary_email)
            result = await db.execute(user_query)
            user_doc = result.scalar_one_or_none()
            if user_doc:
                user_doc.first_name = event_data["first_name"]
                user_doc.last_name = event_data["last_name"]
                user_doc.email = primary_email
                user_doc.source_id = event_data["id"]

            print("User Updated", user_doc, event_data)
        case "user.deleted":
            # TODO: add the created user in the databae without a password, set the source to clerk.
            deleted = event_data["deleted"]

            user_query = select(User).where(User.source_id == event_data["id"])
            result = await db.execute(user_query)
            user_doc = result.scalar_one_or_none()
            if user_doc and deleted:
                user_doc.deleted_at = datetime.now()

            print("User Deleted", user_doc, event_data)
            pass

    await db.commit()
    res.status_code = status.HTTP_200_OK
    return res
