from fastapi import FastAPI, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
# from database import AsyncSessionLocal
from sqlalchemy.future import select
from main_graph import create_workflow_graph
from qdrant_client import AsyncQdrantClient
# from app_reminder import setup_scheduler, schedule_appointment_reminder
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from polly_tests import VoiceCreation
from pytz import timezone
from validator import TopicValidator
from database import engine
from prayer_embeddings import PrayerRelation
from counselling_embedings import CounsellingRelation
from models import create_tables
from question_rewriters import update_chat_history
from typing import Dict
import httpx
import json
import asyncio
import logging
from sqlalchemy import delete
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
# from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from models import Appointment
from settings import settings
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define timezone (West Africa Time)
WAT = ZoneInfo("Africa/Lagos")
WAT_timezone = timezone('Africa/Lagos')

# Global scheduler instance (for access without passing as argument)
scheduler = None

# Initialize FastAPI app
app = FastAPI()

# Constants
WHATSAPP_API_URL = settings.WHATSAPP_API_URL
WHATSAPP_API_AUTHORIZATION = settings.WHATSAPP_API_AUTHORIZATION
ASSEMBLYAI_API_KEY = settings.ASSEMBLYAI_API_KEY


async def get_async_db():
    """Dependency for async database session."""
    async with AsyncSession(engine) as session:
        yield session


def setup_scheduler():
    """Initialize the scheduler with a SQLAlchemy job store."""
    jobstores = {
        'default': SQLAlchemyJobStore(
            url="postgresql://postgres:boywithuke@localhost:5432/NTIEM_BOT"
        )
    }

    global scheduler
    scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=WAT)
    scheduler.add_job(
        check_and_delete_old_appointments,
        trigger=CronTrigger(day="28-31", hour=23, minute=59, timezone=WAT),
        id="delete_old_appointments",
        replace_existing=True,
        args=[]  # Pass database session factory
    )

    return scheduler


async def delete_old_appointments(db: AsyncSession):
    """Delete appointments older than 30 days and remove associated scheduler jobs."""
    try:
        cutoff_date = datetime.now(WAT_timezone).date() - timedelta(days=30)
        result = await db.execute(
            select(Appointment).filter(
                Appointment.appointment_date < cutoff_date.strftime("%Y-%m-%d")
            )
        )
        old_appointments = result.scalars().all()
        if not old_appointments:
            logger.info("No appointments older than one month found.")
            return

        for appointment in old_appointments:
            await db.execute(
                delete(Appointment).filter(Appointment.id == appointment.id)
            )
            job_id = f"reminder_{appointment.id}"
            if scheduler and scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
                logger.info(
                    f"Removed scheduler job for appointment {appointment.id}")
        await db.commit()
        logger.info(
            f"Deleted {len(old_appointments)} appointments older than {cutoff_date}")
    except Exception as e:
        logger.error(f"Failed to delete old appointments: {str(e)}")
        await db.rollback()


async def check_and_delete_old_appointments():
    async with AsyncSession(engine) as db:
        """Check if today is the last day of the month and run delete_old_appointments."""
        today = datetime.now(WAT).date()
        # Check if tomorrow is the 1st of the next month
        tomorrow = today + timedelta(days=1)
        if tomorrow.day == 1:
            logger.info("Running end-of-month appointment cleanup")
            await delete_old_appointments(db)
        else:
            logger.debug(
                f"Skipping cleanup; today ({today}) is not the last day of the month")

# Initialize scheduler
scheduler = setup_scheduler()


@app.on_event("startup")
async def startup_event():
    scheduler.start()
    await create_tables()
    app.state.validators = {
        "rag": TopicValidator(),
        "prayer": PrayerRelation(),
        "counselling": CounsellingRelation()
    }
    logger.info("Scheduler started and validators initialized")
    logger.info("Validators initilaized")


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    for validator in app.state.validators.values():
        if hasattr(validator, 'client') and isinstance(validator.client, AsyncQdrantClient):
            await validator.client.close()
    logger.info("Closed Qdrant clients")
    logger.info("Scheduler stopped")


def get_validators(request: Request) -> dict:
    return request.app.state.validators


@app.get("/health_check")
async def health_check():
    return {
        "status": "healthy" if hasattr(app.state, "validators") and app.state.validators else "starting",
        "validators_initialized": bool(app.state.validators)
    }


@app.api_route("/whatsapp_response", methods=["GET", "POST"])
async def whatsapp_handler(request: Request, validators: dict = Depends(get_validators)) -> Response:
    """Handles incoming messages and status updates from the WhatsApp Cloud API."""

    if request.method == "GET":
        params = request.query_params
        # if params.get("hub.verify_token") == os.getenv("WHATSAPP_VERIFY_TOKEN"):
        if params.get("hub.verify_token") == "12345":
            return Response(content=params.get("hub.challenge"), status_code=200)
        logger.warning("Verification Token Mismatch")
        return Response(content="Verification token mismatch", status_code=403)

    try:
        data = await request.json()
        change_value = data["entry"][0]["changes"][0]["value"]
        # wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        # name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

        if "messages" in change_value:
            message = change_value["messages"][0]
            from_number = message["from"]
            name = change_value["contacts"][0]["profile"]["name"]
            from_voice_note = False
            await message_recieved(from_number)

            # Get user message and handle different message types
            content = ""
            if message["type"] == "audio":
                content = await process_audio_message(message)
                from_voice_note = True

            elif message['type'] == 'text':
                content = message["text"]["body"]

            else:
                content = "Hello"
            # Process user input
            rag = validators['rag']
            prayer_embeddings = validators['prayer']
            counselling_embeddings = validators['counselling']

            graph = create_workflow_graph().compile()
            rag_validator = [rag]
            p_and_c_validators = {
                'validator': prayer_embeddings,
                "counselling_validator": counselling_embeddings
            }
            graph_input = {
                'user_request': content,
                'user_name': name,
                'user_phone_number': from_number,
                'rag_validator': rag_validator,
                'p_and_c_validators': p_and_c_validators,
                'scheduler': [scheduler]
            }
            results = await graph.ainvoke(graph_input)
            output_format = results['output_format']
            response = results['response']
            user_request = results['user_request']
            success = await process_message_response(from_number, response, from_voice_note, output_format, user_request)

            if not success:
                return Response(content="Failed to send message", status_code=500)

            return Response(content=json.dumps(success), status_code=200)
        else:
            Response(content="Recieved webhook event", status_code=200)

    except BaseException as e:
        logger.warning(f"An error has just occured {e}")
        print(traceback.format_tb(e))
        return Response(content="This went wrong {e}", status_code=500)


async def process_message_response(number, response, voice_note, ouput_format, user_input):
    if ouput_format == 'text':
        if voice_note:
            url = VoiceCreation(response).text_to_speech()
            api_response = await audio_response(number, url)
        else:
            api_response = await text_response(number, response)
        await update_chat_history(number, user_message=user_input, bot_response=response)
        return api_response

    if ouput_format == 'video':
        collective_result = ''
        for result in response:
            if result['match_type'] == 'title':
                link = result['s3VideoLink']
                text = f"We found this result based on the title you provided, watch the rest of the sermon here: {result['socialVideoLink']}\n"
            else:
                link = result['s3VideoLink']
                text = f"We found this result based on the date you provided, watch the rest of the sermon here: {result['socialVideoLink']}\n"
            response = await video_response(number, link, text)
            collective_result += text
        await update_chat_history(number, user_message=user_input, bot_response=collective_result)
        return response

    if ouput_format == 'image':
        response = await image_response(number, image_url=response)
        await update_chat_history(number, user_message=user_input, bot_response=f"Here is the link to the image we just created fpr you based on your query: {response}")
        return response


async def process_audio_message(message: Dict) -> str:
    """Download WhatsApp audio, upload to AssemblyAI, and transcribe."""

    audio_id = message["audio"]["id"]
    media_metadata_url = f"https://graph.facebook.com/v22.0/{audio_id}"
    headers = {"Authorization": WHATSAPP_API_AUTHORIZATION}

    # Step 1: Get download URL from WhatsApp
    async with httpx.AsyncClient() as client:
        metadata_response = await client.get(media_metadata_url, headers=headers)
        metadata_response.raise_for_status()
        metadata = metadata_response.json()
        download_url = metadata.get("url")

    # Step 2: Download the audio file from WhatsApp
    async with httpx.AsyncClient() as client:
        audio_response = await client.get(download_url, headers=headers)
        audio_response.raise_for_status()
        audio_data = audio_response.content  # raw bytes of the audio file

    # Step 3: Upload audio file to AssemblyAI
    assembly_headers = {
        "authorization": ASSEMBLYAI_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        upload_response = await client.post(
            "https://api.assemblyai.com/v2/upload",
            headers=assembly_headers,
            content=audio_data
        )
        upload_response.raise_for_status()
        upload_data = upload_response.json()
        # This is what AssemblyAI will transcribe
        upload_url = upload_data["upload_url"]

    # Step 4: Request transcription using the uploaded file
    transcript_request = {
        "audio_url": upload_url
    }

    async with httpx.AsyncClient() as client:
        transcript_response = await client.post(
            "https://api.assemblyai.com/v2/transcript",
            headers={**assembly_headers, "content-type": "application/json"},
            json=transcript_request
        )
        transcript_response.raise_for_status()
        transcript_data = transcript_response.json()
        transcript_id = transcript_data["id"]

    # Step 5: Poll AssemblyAI until transcription is complete
    polling_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

    while True:
        async with httpx.AsyncClient() as client:
            poll_response = await client.get(polling_url, headers=assembly_headers)
            poll_response.raise_for_status()
            poll_data = poll_response.json()

            if poll_data["status"] == "completed":
                return poll_data["text"]
            elif poll_data["status"] == "failed":
                logger.warning(f"Transcription failed: {poll_data}")

        await asyncio.sleep(3)  # Wait a few seconds before polling again


async def text_response(number, text):
    url = WHATSAPP_API_URL
    headers = {
        "Authorization": WHATSAPP_API_AUTHORIZATION,
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(number),
        "type": "text",
        "text": {"body": str(text)}
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url=url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise


async def audio_response(number, audio_url):
    api_url = WHATSAPP_API_URL
    headers = {
        "Authorization": WHATSAPP_API_AUTHORIZATION,
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(number),
        "type": "audio",
        "audio": {
            "link": str(audio_url)
        }
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url=api_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error sending audio: {str(e)}")
            raise


async def video_response(number, video_url, caption):
    api_url = WHATSAPP_API_URL
    headers = {
        "Authorization": WHATSAPP_API_AUTHORIZATION,
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(number),
        "type": "video",
        "video": {
            "link": str(video_url),
            "caption": str(caption)
        }
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url=api_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error sending video: {str(e)}")
            raise


async def image_response(number, image_url):
    caption = "Here is your image"
    api_url = WHATSAPP_API_URL
    headers = {
        "Authorization": WHATSAPP_API_AUTHORIZATION,
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(number),
        "type": "image",
        "image": {
            "link": str(image_url)
        }
    }
    if caption:
        payload["image"]["caption"] = str(caption)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url=api_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error sending image: {str(e)}")
            raise


async def message_recieved(number):
    url = WHATSAPP_API_URL
    headers = {
        "Authorization": WHATSAPP_API_AUTHORIZATION,
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(number),
        "type": "text",
        "text": {"body": "Hello we have recieved your message, please wait while we process it!"}
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url=url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise
