from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlmodel import select, and_, desc, func
from decimal import Decimal

from app.core.database import get_session, AsyncSession
from app.modules.bots.models import CreditTransaction, CreditTransactionManager
from app.modules.organizations.models import Organization
from app.modules.projects.models import Project
from app.modules.users.models import User
from app.modules.users.dependencies import get_current_user

router = APIRouter(prefix="/credits", tags=["credits"])


class CreditTransactionResponse(BaseModel):
    """Response schema for CreditTransaction"""

    id: str
    object_id: str
    organization_id: str
    bot_id: Optional[str] = None
    centicredits_before: int
    centicredits_after: int
    centicredits_delta: int
    credits_delta: float
    description: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    transaction_type: str
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, transaction: CreditTransaction):
        """Create response from CreditTransaction model"""
        return cls(
            id=transaction.id,
            object_id=transaction.object_id,
            organization_id=transaction.organization_id,
            bot_id=transaction.bot_id,
            centicredits_before=transaction.centicredits_before,
            centicredits_after=transaction.centicredits_after,
            centicredits_delta=transaction.centicredits_delta,
            credits_delta=transaction.credits_delta(),
            description=transaction.description,
            stripe_payment_intent_id=transaction.stripe_payment_intent_id,
            transaction_type=transaction.get_transaction_type(),
            created_at=transaction.created_at,
        )


class AddCreditsRequest(BaseModel):
    """Request schema for adding credits"""

    amount: float = Field(..., gt=0, description="Amount of credits to add")
    description: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None


@router.get("/balance")
async def get_credit_balance(
    organization_id: str = Query(..., description="Organization ID"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get current credit balance for organization"""

    # Get organization
    result = await session.exec(
        select(Organization).where(Organization.id == organization_id)
    )
    organization = result.first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    # Get usage stats
    stats = organization.get_credit_usage_stats()

    return {
        "organization_id": organization.object_id,
        "current_balance": organization.credits(),
        "current_balance_centicredits": organization.centicredits,
        "formatted_balance": organization.format_credit_balance(),
        "is_low_credits": organization.is_low_on_credits(),
        "stats": stats,
    }


@router.get("/transactions", response_model=List[CreditTransactionResponse])
async def list_credit_transactions(
    organization_id: str = Query(..., description="Organization ID"),
    transaction_type: Optional[str] = Query(
        None, description="Filter by transaction type"
    ),
    limit: int = Query(
        50, ge=1, le=100, description="Number of transactions to return"
    ),
    offset: int = Query(0, ge=0, description="Number of transactions to skip"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List credit transactions for organization"""

    # Build query
    query = select(CreditTransaction).where(
        CreditTransaction.organization_id == organization_id
    )

    # Filter by transaction type if specified
    if transaction_type:
        if transaction_type == "payment":
            query = query.where(CreditTransaction.stripe_payment_intent_id.isnot(None))
        elif transaction_type == "usage":
            query = query.where(CreditTransaction.bot_id.isnot(None))
        elif transaction_type == "addition":
            query = query.where(CreditTransaction.centicredits_delta > 0)
        elif transaction_type == "deduction":
            query = query.where(CreditTransaction.centicredits_delta < 0)

    # Order by created_at desc and apply pagination
    query = query.order_by(desc(CreditTransaction.created_at))
    query = query.offset(offset).limit(limit)

    # Execute query
    result = await session.exec(query)
    transactions = result.all()

    return [CreditTransactionResponse.from_orm(t) for t in transactions]


@router.post("/add")
async def add_credits(
    organization_id: str = Query(..., description="Organization ID"),
    request: AddCreditsRequest = Body(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Add credits to organization (admin only)"""

    # Get organization
    result = await session.exec(
        select(Organization).where(Organization.id == organization_id)
    )
    organization = result.first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    # Create credit transaction
    transaction = CreditTransactionManager.create_transaction(
        organization=organization,
        centicredits_delta=int(request.amount * 100),
        description=request.description or f"Credits added: {request.amount}",
        stripe_payment_intent_id=request.stripe_payment_intent_id,
    )

    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)

    return {
        "message": f"Successfully added {request.amount} credits",
        "transaction": CreditTransactionResponse.from_orm(transaction),
        "new_balance": organization.credits(),
    }


@router.get("/usage-stats")
async def get_credit_usage_stats(
    organization_id: str = Query(..., description="Organization ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get detailed credit usage statistics"""

    # Get organization
    result = await session.exec(
        select(Organization).where(Organization.id == organization_id)
    )
    organization = result.first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    # Calculate date range
    from datetime import datetime, timedelta

    start_date = datetime.utcnow() - timedelta(days=days)

    # Get transactions in date range
    transactions_query = select(CreditTransaction).where(
        and_(
            CreditTransaction.organization_id == organization_id,
            CreditTransaction.created_at >= start_date,
        )
    )

    transactions_result = await session.exec(transactions_query)
    transactions = transactions_result.all()

    # Analyze transactions
    total_added = (
        sum(t.centicredits_delta for t in transactions if t.centicredits_delta > 0)
        / 100
    )
    total_used = (
        abs(sum(t.centicredits_delta for t in transactions if t.centicredits_delta < 0))
        / 100
    )

    # Count by type
    payment_transactions = [t for t in transactions if t.is_stripe_payment()]
    usage_transactions = [t for t in transactions if t.is_bot_usage()]

    # Usage by bot
    usage_by_bot = {}
    for t in usage_transactions:
        if t.bot_id:
            bot_usage = abs(t.centicredits_delta) / 100
            if t.bot_id not in usage_by_bot:
                usage_by_bot[t.bot_id] = 0
            usage_by_bot[t.bot_id] += bot_usage

    return {
        "organization_id": organization.object_id,
        "period_days": days,
        "current_balance": organization.credits(),
        "total_added": total_added,
        "total_used": total_used,
        "net_change": total_added - total_used,
        "transaction_counts": {
            "total": len(transactions),
            "payments": len(payment_transactions),
            "usage": len(usage_transactions),
        },
        "usage_by_bot": usage_by_bot,
        "daily_average_usage": total_used / days if days > 0 else 0,
    }


@router.get("/transactions/{transaction_id}", response_model=CreditTransactionResponse)
async def get_credit_transaction(
    transaction_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get specific credit transaction by ID"""

    result = await session.exec(
        select(CreditTransaction).where(CreditTransaction.id == transaction_id)
    )
    transaction = result.first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Credit transaction not found"
        )

    return CreditTransactionResponse.from_orm(transaction)


@router.get("/estimates")
async def get_usage_estimates(
    organization_id: str = Query(..., description="Organization ID"),
    hours: float = Query(..., gt=0, description="Estimated hours of bot usage"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get estimated credit cost for bot usage"""

    # Get organization
    result = await session.exec(
        select(Organization).where(Organization.id == organization_id)
    )
    organization = result.first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    # Calculate estimates (1 credit per hour rate)
    estimated_credits = hours * 1.0  # 1 credit per hour
    can_afford = organization.has_sufficient_credits(estimated_credits)

    return {
        "estimated_hours": hours,
        "estimated_credits": estimated_credits,
        "current_balance": organization.credits(),
        "can_afford": can_afford,
        "remaining_after": (
            organization.credits() - estimated_credits if can_afford else 0
        ),
        "credits_needed": max(0, estimated_credits - organization.credits()),
    }
