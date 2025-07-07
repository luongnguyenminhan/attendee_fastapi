from typing import Optional, List, Any, Dict
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

from app.core.base_enums import WebhookTriggerTypes, WebhookDeliveryAttemptStatus


class WebhookSubscriptionCreateRequest(BaseModel):
    """Request schema for creating webhook subscription"""

    project_id: str
    bot_id: Optional[str] = None
    url: HttpUrl
    trigger_types: List[WebhookTriggerTypes]
    is_active: bool = True


class WebhookSubscriptionResponse(BaseModel):
    """Response schema for WebhookSubscription"""

    id: str
    object_id: str
    project_id: str
    bot_id: Optional[str] = None
    url: str
    trigger_types: List[WebhookTriggerTypes]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookDeliveryAttemptResponse(BaseModel):
    """Response schema for WebhookDeliveryAttempt"""

    id: str
    object_id: str
    webhook_subscription_id: str
    bot_id: Optional[str] = None
    webhook_trigger_type: WebhookTriggerTypes
    status: WebhookDeliveryAttemptStatus
    http_status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    payload: Dict[str, Any]
    attempted_at: Optional[str] = None
    completed_at: Optional[str] = None
    attempt_number: int
    next_retry_at: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
