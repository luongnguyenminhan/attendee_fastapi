from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlmodel import select, and_

from app.core.database import get_session, AsyncSession
from app.modules.bots.models import (
    WebhookSubscription,
    WebhookDeliveryAttempt,
    WebhookSecret,
    Bot,
    Project,
)
from app.modules.bots.schemas import (
    WebhookSubscriptionResponse,
    WebhookSubscriptionCreateRequest,
    WebhookDeliveryAttemptResponse,
)
from app.modules.users.models import User
from app.modules.users.dependencies import get_current_user
from app.core.base_enums import WebhookTriggerTypes, WebhookDeliveryAttemptStatus

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("/subscriptions", response_model=List[WebhookSubscriptionResponse])
async def list_webhook_subscriptions(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    bot_id: Optional[str] = Query(None, description="Filter by bot ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List webhook subscriptions"""

    query = select(WebhookSubscription)
    conditions = []

    if project_id:
        conditions.append(WebhookSubscription.project_id == project_id)

    if bot_id:
        conditions.append(WebhookSubscription.bot_id == bot_id)

    if is_active is not None:
        conditions.append(WebhookSubscription.is_active == is_active)

    if conditions:
        query = query.where(and_(*conditions))

    result = await session.exec(query)
    subscriptions = result.all()

    return [WebhookSubscriptionResponse.from_orm(sub) for sub in subscriptions]


@router.post("/subscriptions", response_model=WebhookSubscriptionResponse)
async def create_webhook_subscription(
    subscription_data: WebhookSubscriptionCreateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create webhook subscription"""

    # Verify project exists
    project_result = await session.exec(
        select(Project).where(Project.id == subscription_data.project_id)
    )
    project = project_result.first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # Get or create webhook secret for project
    webhook_secret = project.get_webhook_secret()
    if not webhook_secret:
        webhook_secret = project.create_webhook_secret()
        session.add(webhook_secret)
        await session.commit()
        await session.refresh(webhook_secret)

    # Create subscription
    subscription = WebhookSubscription(
        project_id=subscription_data.project_id,
        bot_id=subscription_data.bot_id,
        webhook_secret_id=webhook_secret.id,
        url=subscription_data.url,
        trigger_types=subscription_data.trigger_types,
        is_active=subscription_data.is_active,
    )

    session.add(subscription)
    await session.commit()
    await session.refresh(subscription)

    return WebhookSubscriptionResponse.from_orm(subscription)


@router.get(
    "/subscriptions/{subscription_id}", response_model=WebhookSubscriptionResponse
)
async def get_webhook_subscription(
    subscription_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get webhook subscription by ID"""

    result = await session.exec(
        select(WebhookSubscription).where(WebhookSubscription.id == subscription_id)
    )
    subscription = result.first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found",
        )

    return WebhookSubscriptionResponse.from_orm(subscription)


@router.put(
    "/subscriptions/{subscription_id}", response_model=WebhookSubscriptionResponse
)
async def update_webhook_subscription(
    subscription_id: str,
    update_data: WebhookSubscriptionCreateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update webhook subscription"""

    result = await session.exec(
        select(WebhookSubscription).where(WebhookSubscription.id == subscription_id)
    )
    subscription = result.first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found",
        )

    # Update fields
    subscription.url = update_data.url
    subscription.trigger_types = update_data.trigger_types
    subscription.is_active = update_data.is_active
    subscription.bot_id = update_data.bot_id

    await session.commit()
    await session.refresh(subscription)

    return WebhookSubscriptionResponse.from_orm(subscription)


@router.delete("/subscriptions/{subscription_id}")
async def delete_webhook_subscription(
    subscription_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete webhook subscription"""

    result = await session.exec(
        select(WebhookSubscription).where(WebhookSubscription.id == subscription_id)
    )
    subscription = result.first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found",
        )

    await session.delete(subscription)
    await session.commit()

    return {"message": "Webhook subscription deleted successfully"}


@router.post("/subscriptions/{subscription_id}/test")
async def test_webhook_subscription(
    subscription_id: str,
    test_payload: dict = Body(..., description="Test payload to send"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Test webhook subscription by sending a test payload"""

    result = await session.exec(
        select(WebhookSubscription).where(WebhookSubscription.id == subscription_id)
    )
    subscription = result.first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook subscription not found",
        )

    # Create test delivery attempt
    test_attempt = WebhookDeliveryAttempt(
        webhook_subscription_id=subscription.id,
        webhook_trigger_type=WebhookTriggerTypes.BOT_STATE_CHANGE,  # Default test type
        payload=test_payload,
    )

    session.add(test_attempt)
    await session.commit()
    await session.refresh(test_attempt)

    # Queue for delivery
    from app.jobs.tasks import deliver_webhook_task

    deliver_webhook_task.delay(test_attempt.id)

    return {
        "message": "Test webhook queued for delivery",
        "delivery_attempt_id": test_attempt.object_id,
    }


@router.get("/delivery-attempts", response_model=List[WebhookDeliveryAttemptResponse])
async def list_webhook_delivery_attempts(
    subscription_id: Optional[str] = Query(
        None, description="Filter by subscription ID"
    ),
    status: Optional[WebhookDeliveryAttemptStatus] = Query(
        None, description="Filter by status"
    ),
    limit: int = Query(50, ge=1, le=100, description="Number of attempts to return"),
    offset: int = Query(0, ge=0, description="Number of attempts to skip"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List webhook delivery attempts"""

    query = select(WebhookDeliveryAttempt)
    conditions = []

    if subscription_id:
        conditions.append(
            WebhookDeliveryAttempt.webhook_subscription_id == subscription_id
        )

    if status:
        conditions.append(WebhookDeliveryAttempt.status == status)

    if conditions:
        query = query.where(and_(*conditions))

    # Order by created_at desc
    query = query.order_by(WebhookDeliveryAttempt.created_at.desc())
    query = query.offset(offset).limit(limit)

    result = await session.exec(query)
    attempts = result.all()

    return [WebhookDeliveryAttemptResponse.from_orm(attempt) for attempt in attempts]


@router.get(
    "/delivery-attempts/{attempt_id}", response_model=WebhookDeliveryAttemptResponse
)
async def get_webhook_delivery_attempt(
    attempt_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get webhook delivery attempt by ID"""

    result = await session.exec(
        select(WebhookDeliveryAttempt).where(WebhookDeliveryAttempt.id == attempt_id)
    )
    attempt = result.first()

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook delivery attempt not found",
        )

    return WebhookDeliveryAttemptResponse.from_orm(attempt)


@router.post("/delivery-attempts/{attempt_id}/retry")
async def retry_webhook_delivery(
    attempt_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Manually retry webhook delivery"""

    result = await session.exec(
        select(WebhookDeliveryAttempt).where(WebhookDeliveryAttempt.id == attempt_id)
    )
    attempt = result.first()

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook delivery attempt not found",
        )

    if not attempt.can_retry():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook delivery cannot be retried",
        )

    # Create retry attempt
    retry_attempt = attempt.create_retry_attempt()
    session.add(retry_attempt)
    await session.commit()
    await session.refresh(retry_attempt)

    # Queue for delivery
    from app.jobs.tasks import deliver_webhook_task

    deliver_webhook_task.delay(retry_attempt.id)

    return {
        "message": "Webhook delivery retry queued",
        "retry_attempt_id": retry_attempt.object_id,
    }


@router.get("/stats")
async def get_webhook_stats(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get webhook delivery statistics"""

    # Build base query
    query = select(WebhookDeliveryAttempt)
    if project_id:
        query = query.join(WebhookSubscription).where(
            WebhookSubscription.project_id == project_id
        )

    result = await session.exec(query)
    all_attempts = result.all()

    # Calculate stats
    total_attempts = len(all_attempts)
    successful = len([a for a in all_attempts if a.is_successful()])
    failed = len([a for a in all_attempts if a.is_failed()])
    pending = len([a for a in all_attempts if a.is_pending()])

    success_rate = (successful / total_attempts * 100) if total_attempts > 0 else 0

    return {
        "total_attempts": total_attempts,
        "successful": successful,
        "failed": failed,
        "pending": pending,
        "success_rate": round(success_rate, 2),
    }
