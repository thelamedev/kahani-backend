import os
from datetime import datetime, timedelta
from uuid import UUID
import uuid
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import select

from modules.transaction.dto import CreateTransactionRequest
from shared.database import AsyncSession, get_db
from shared.models.user import Subscription, User
from shared.discord_webhook import send_discord_webhook_message
from modules.transaction.service import add_transaction

router = APIRouter(prefix="/clerk", tags=["Webhook"])

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

    webhook_message = ""

    match event_type:
        case "user.created":
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

            new_user_subscription = Subscription(
                user_id=new_user_doc.id,
                display_name="Early Adopter",
                expires_at=datetime.now() + timedelta(days=120),
                credits=0,
            )

            db.add_all([new_user_doc, new_user_subscription])

            user_uid = uuid.UUID(hex=str(new_user_doc.id))
            await add_transaction(
                db,
                CreateTransactionRequest(
                    user_id=user_uid,
                    amount=25,
                    remarks="Welcome credits!",
                ),
            )

            webhook_message = f"User Created with email `{new_user_doc.email}` and user_id `{event_data['id']}`"
        case "user.updated":
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
                webhook_message = f"User Updated with email `{user_doc.email}` and user_id `{user_doc.source_id}`"
                print("User Updated", user_doc, event_data)
        case "user.deleted":
            deleted = event_data["deleted"]

            user_query = select(User).where(User.source_id == event_data["id"])
            result = await db.execute(user_query)
            user_doc = result.scalar_one_or_none()
            if user_doc and deleted:
                user_doc.deleted_at = datetime.now()
                webhook_message = f"User Deleted with email `{user_doc.email}` and user_id `{user_doc.source_id}`"
                print("User Deleted", user_doc, event_data)

    await db.commit()

    await send_discord_webhook_message(webhook_message, "Kahani (Clerk)")

    res.status_code = status.HTTP_200_OK
    return res
