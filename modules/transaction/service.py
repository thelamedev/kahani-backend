from fastapi import HTTPException, status
from sqlalchemy import select
from uuid import UUID

from modules.transaction.dto import CreateTransactionRequest
from shared.database import AsyncSession
from shared.models.transaction import Transaction
from shared.models.user import Subscription
from shared.pagination import Pagination


async def list_paginated_transactions(
    db: AsyncSession,
    pagination: Pagination,
    current_uid: UUID,
):
    query = (
        select(Transaction)
        .where(Transaction.user_id == current_uid)
        .order_by(Transaction.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.limit)
    )

    result = await db.execute(query)

    txns = [x.tuple()[0] for x in result.all()]

    return txns


async def add_transaction(
    db: AsyncSession,
    new_txn: CreateTransactionRequest,
):
    txn = Transaction(
        user_id=new_txn.user_id,
        amount=new_txn.amount,
        remarks=new_txn.remarks,
        transaction_ref=new_txn.transaction_ref,
    )

    db.add(txn)
    await db.commit()

    return txn


async def get_available_credits(db: AsyncSession, user_id: UUID):
    query = select(Subscription.credits).where(Subscription.user_id == user_id).limit(1)
    result = await db.execute(query)
    credits = result.scalar_one_or_none()
    if credits is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"could not find subscription for user {user_id}",
        )

    return credits


async def update_credits_with_transaction(
    db: AsyncSession,
    new_txn: CreateTransactionRequest,
):
    txn = Transaction(
        user_id=new_txn.user_id,
        amount=new_txn.amount,
        remarks=new_txn.remarks,
        transaction_ref=new_txn.transaction_ref,
    )

    sub_query = select(Subscription).where(Subscription.user_id == new_txn.user_id)
    user_sub_result = await db.execute(sub_query)
    user_sub = user_sub_result.scalar_one_or_none()
    if user_sub is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "User subscription does not exist",
        )

    user_sub.credits += new_txn.amount
    db.add(txn)

    await db.commit()

    return txn
