import asyncio
import json
import logging

import httpx
from sqlmodel import select

from app.core.base_enums import (
    BotStates,
)
from app.core.database import get_session_context
from app.jobs.celery_app import celery_app
from app.modules.bots.models import (
    Bot,
    CreditTransactionManager,
    Utterance,
    WebhookDeliveryAttempt,
)

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_utterance_task(self, utterance_id: str, transcription_provider: str = "deepgram"):
    """
    Process utterance transcription using specified provider

    Args:
        utterance_id: ID of utterance to process
        transcription_provider: Provider to use (deepgram, openai, etc.)
    """
    try:

        async def _process():
            async with get_session_context() as session:
                # Get utterance
                result = await session.exec(select(Utterance).where(Utterance.id == utterance_id))
                utterance = result.first()

                if not utterance:
                    logger.error(f"Utterance {utterance_id} not found")
                    return {"status": "error", "message": "Utterance not found"}

                if not utterance.has_audio():
                    logger.warning(f"Utterance {utterance_id} has no audio data")
                    return {"status": "skipped", "message": "No audio data"}

                if utterance.has_transcription():
                    logger.info(f"Utterance {utterance_id} already transcribed")
                    return {"status": "skipped", "message": "Already transcribed"}

                # Increment attempt count
                utterance.increment_attempt_count()

                try:
                    # Get recording and project for credentials
                    recording = utterance.recording
                    project = recording.bot.project

                    # Get credentials for provider
                    credentials = project.get_credentials_by_type(transcription_provider)
                    if not credentials:
                        error_msg = f"No {transcription_provider} credentials found for project {project.id}"
                        utterance.mark_transcription_failed(error_msg)
                        await session.commit()
                        return {"status": "error", "message": error_msg}

                    # TODO: Implement actual transcription providers
                    # For now, simulate transcription
                    import time

                    time.sleep(1)  # Simulate API call

                    # Mock transcription result
                    mock_transcript = f"Mock transcription for utterance {utterance.object_id}"
                    confidence = 0.85

                    # Set transcription
                    utterance.set_transcription(transcript=mock_transcript, confidence=confidence)

                    # Clear audio blob to save space
                    utterance.clear_audio_blob()

                    await session.commit()

                    logger.info(f"Successfully transcribed utterance {utterance_id}")
                    return {
                        "status": "success",
                        "utterance_id": utterance_id,
                        "transcript": mock_transcript,
                        "confidence": confidence,
                    }

                except Exception as e:
                    error_msg = f"Transcription failed: {str(e)}"
                    utterance.mark_transcription_failed(error_msg)
                    await session.commit()
                    raise

        return asyncio.run(_process())

    except Exception as e:
        logger.error(f"Error processing utterance {utterance_id}: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(countdown=60 * (2**self.request.retries), exc=e)


@celery_app.task(bind=True, max_retries=5)
def deliver_webhook_task(self, delivery_attempt_id: str):
    """
    Deliver webhook with retry logic

    Args:
        delivery_attempt_id: ID of webhook delivery attempt
    """
    try:

        async def _deliver():
            async with get_session_context() as session:
                # Get delivery attempt
                result = await session.exec(select(WebhookDeliveryAttempt).where(WebhookDeliveryAttempt.id == delivery_attempt_id))
                attempt = result.first()

                if not attempt:
                    logger.error(f"Delivery attempt {delivery_attempt_id} not found")
                    return {"status": "error", "message": "Delivery attempt not found"}

                subscription = attempt.webhook_subscription
                webhook_secret = subscription.webhook_secret

                # Mark as pending
                attempt.mark_pending()
                await session.commit()

                try:
                    # Prepare payload
                    payload = attempt.payload
                    payload_json = json.dumps(payload, separators=(",", ":"))
                    payload_bytes = payload_json.encode("utf-8")

                    # Generate signature
                    signature = webhook_secret.generate_signature(payload_bytes)

                    # Prepare headers
                    headers = {
                        "Content-Type": "application/json",
                        "X-Webhook-Signature": f"sha256={signature}",
                        "X-Webhook-Event": attempt.webhook_trigger_type.name,
                        "User-Agent": "Attendee-Webhook/1.0",
                    }

                    # Send webhook
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.post(subscription.url, content=payload_bytes, headers=headers)

                    # Check if successful (2xx status codes)
                    if 200 <= response.status_code < 300:
                        attempt.mark_successful(
                            http_status=response.status_code,
                            response_body=response.text[:10000],  # Limit size
                        )
                        await session.commit()

                        logger.info(f"Webhook delivered successfully: {delivery_attempt_id}")
                        return {
                            "status": "success",
                            "status_code": response.status_code,
                            "attempt_id": delivery_attempt_id,
                        }
                    else:
                        # Mark as failed
                        error_msg = f"HTTP {response.status_code}"
                        attempt.mark_failed(
                            error_message=error_msg,
                            http_status=response.status_code,
                            response_body=response.text[:10000],
                        )
                        await session.commit()

                        # Schedule retry if possible
                        if attempt.can_retry():
                            retry_attempt = attempt.create_retry_attempt()
                            session.add(retry_attempt)
                            await session.commit()

                            # Schedule retry task
                            deliver_webhook_task.apply_async(
                                args=[retry_attempt.id],
                                countdown=60 * (2**attempt.attempt_number),
                            )

                        return {
                            "status": "failed",
                            "status_code": response.status_code,
                            "error": error_msg,
                        }

                except Exception as e:
                    error_msg = f"Request failed: {str(e)}"
                    attempt.mark_failed(error_message=error_msg)
                    await session.commit()

                    # Schedule retry if possible
                    if attempt.can_retry():
                        retry_attempt = attempt.create_retry_attempt()
                        session.add(retry_attempt)
                        await session.commit()

                        # Schedule retry task
                        deliver_webhook_task.apply_async(
                            args=[retry_attempt.id],
                            countdown=60 * (2**attempt.attempt_number),
                        )

                    raise

        return asyncio.run(_deliver())

    except Exception as e:
        logger.error(f"Error delivering webhook {delivery_attempt_id}: {str(e)}")
        # Don't retry on task level since we handle retries in business logic
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True)
def launch_scheduled_bot_task(self, bot_id: str):
    """
    Launch a scheduled bot

    Args:
        bot_id: ID of bot to launch
    """
    try:

        async def _launch():
            async with get_session_context() as session:
                # Get bot
                result = await session.exec(select(Bot).where(Bot.id == bot_id))
                bot = result.first()

                if not bot:
                    logger.error(f"Bot {bot_id} not found")
                    return {"status": "error", "message": "Bot not found"}

                if bot.state != BotStates.SCHEDULED:
                    logger.warning(f"Bot {bot_id} is not in scheduled state: {bot.state}")
                    return {"status": "skipped", "message": "Bot not scheduled"}

                # Check organization credits
                organization = bot.project.organization
                if not organization.has_sufficient_credits(1.0):  # Minimum 1 credit needed
                    bot.set_error()
                    await session.commit()

                    error_msg = "Insufficient credits"
                    logger.error(f"Cannot launch bot {bot_id}: {error_msg}")
                    return {"status": "error", "message": error_msg}

                # Set bot to ready state
                bot.state = BotStates.READY
                await session.commit()

                # TODO: Implement actual bot launching (Kubernetes pod creation)
                # For now, simulate the launch
                logger.info(f"Launching bot {bot_id} for meeting: {bot.meeting_url}")

                # Start the bot
                run_bot_task.delay(bot_id)

                return {
                    "status": "success",
                    "bot_id": bot_id,
                    "message": "Bot launch initiated",
                }

        return asyncio.run(_launch())

    except Exception as e:
        logger.error(f"Error launching scheduled bot {bot_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True)
def run_bot_task(self, bot_id: str):
    """
    Main bot execution task

    Args:
        bot_id: ID of bot to run
    """
    try:

        async def _run():
            async with get_session_context() as session:
                # Get bot
                result = await session.exec(select(Bot).where(Bot.id == bot_id))
                bot = result.first()

                if not bot:
                    logger.error(f"Bot {bot_id} not found")
                    return {"status": "error", "message": "Bot not found"}

                if not bot.can_join_meeting():
                    logger.warning(f"Bot {bot_id} cannot join meeting")
                    return {"status": "skipped", "message": "Bot cannot join meeting"}

                try:
                    # Start joining
                    bot.start_joining()
                    await session.commit()

                    # TODO: Implement actual bot automation
                    # This would involve:
                    # 1. Chrome/Selenium automation
                    # 2. Meeting platform integration (Zoom/Google Meet/Teams)
                    # 3. Audio/video recording
                    # 4. Real-time transcription
                    # 5. Participant tracking

                    # For now, simulate bot lifecycle
                    import time

                    # Simulate joining
                    logger.info(f"Bot {bot_id} joining meeting: {bot.meeting_url}")
                    time.sleep(2)

                    # Mark as joined and recording
                    bot.join_meeting(recording=True)
                    bot.update_heartbeat()
                    await session.commit()

                    # Simulate meeting duration
                    logger.info(f"Bot {bot_id} recording meeting...")
                    time.sleep(5)

                    # End meeting
                    bot.end_meeting()
                    await session.commit()

                    # Create credit transaction for usage
                    credits_consumed = bot.centicredits_consumed()
                    if credits_consumed > 0:
                        CreditTransactionManager.create_transaction(
                            organization=bot.project.organization,
                            centicredits_delta=-credits_consumed,
                            bot=bot,
                            description=f"Bot usage for meeting: {bot.name}",
                        )
                        await session.commit()

                    logger.info(f"Bot {bot_id} completed meeting")
                    return {
                        "status": "success",
                        "bot_id": bot_id,
                        "credits_consumed": credits_consumed / 100.0,
                    }

                except Exception:
                    # Mark bot as error
                    bot.set_error()
                    await session.commit()
                    raise

        return asyncio.run(_run())

    except Exception as e:
        logger.error(f"Error running bot {bot_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True)
def restart_bot_pod_task(self, bot_id: str):
    """
    Restart Kubernetes pod for bot

    Args:
        bot_id: ID of bot whose pod to restart
    """
    try:

        async def _restart():
            async with get_session_context() as session:
                # Get bot
                result = await session.exec(select(Bot).where(Bot.id == bot_id))
                bot = result.first()

                if not bot:
                    logger.error(f"Bot {bot_id} not found")
                    return {"status": "error", "message": "Bot not found"}

                pod_name = bot.k8s_pod_name()

                # TODO: Implement actual Kubernetes pod restart
                # This would involve using kubernetes Python client

                logger.info(f"Restarting pod {pod_name} for bot {bot_id}")

                # Simulate restart
                import time

                time.sleep(2)

                return {
                    "status": "success",
                    "bot_id": bot_id,
                    "pod_name": pod_name,
                    "message": "Pod restart completed",
                }

        return asyncio.run(_restart())

    except Exception as e:
        logger.error(f"Error restarting pod for bot {bot_id}: {str(e)}")
        return {"status": "error", "message": str(e)}


# Legacy task for backward compatibility
@celery_app.task
def add_numbers(x: int, y: int) -> int:
    """Simple test task for Celery"""
    return x + y
