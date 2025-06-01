# from datetime import datetime, timedelta
# from models import Appointment
# from database import get_async_db  # Import asynchronous get_db function
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
# from apscheduler.triggers.date import DateTrigger
# import logging
# import ast
import os
from pytz import timezone
# from config import app_settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
# from sqlalchemy.ext.asyncio import AsyncSession
from database import engine
from datetime import datetime, timedelta
from models import Appointment  # Assume this is your SQLAlchemy model
from database import AsyncSessionLocal  # Updated to use async session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
import logging
import ast
from pytz import timezone
from zoneinfo import ZoneInfo
import httpx
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# import asyncio
# from config import app_settings

# Configure WAT timezone
WAT = ZoneInfo("Africa/Lagos")
WAT_timezone = timezone('Africa/Lagos')

# Global scheduler instance (for access without passing as argument)
scheduler = None

# Constants
WHATSAPP_TOKEN = "EAAMzcBIJtngBOyFZBiMZBH0GnacrALWRADQmZCkso9XIwaSJHQhg8J68CNKxB5v8OHZBWs7WEpriZBPSMRbbwvCEioxDRIfJTIxGPO7a8TktBCl3ZC4uUdYqiCa0d9jcjxz4U6TZB0017DPcixW8xhiqQoZAEC1V7gg0vcnZCvaSuadT4I46G4K285ZBeiVHXbj9NfnQZDZD"
ASSEMBLYAI_API_KEY = "f16b132ff9384d2b9d546aeffe1ea5e1"


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


async def schedule_appointment_reminder(appointment: Appointment, scheduler: AsyncIOScheduler):
    """Schedule a reminder for a new appointment in WAT."""
    try:
        # Parse appointment date and time in WAT
        appointment_date = datetime.strptime(
            appointment.appointment_date,
            "%Y-%m-%d"
        ).date()

        # Parse time tuple string "(11, 23)" -> (hour, minute)
        try:
            time_tuple = ast.literal_eval(appointment.appointment_time)
            if not isinstance(time_tuple, tuple) or len(time_tuple) != 2:
                raise ValueError
            hour, minute = time_tuple
        except (ValueError, SyntaxError):
            logger.error(
                f"Invalid time format for appointment {appointment.id}")
            return

        # Create WAT-aware datetime
        appointment_dt = WAT_timezone.localize(
            datetime.combine(
                appointment_date,
                datetime.min.time().replace(hour=hour, minute=minute)
            )
        )

        # Calculate reminder time (6 hours before in WAT)
        # reminder_time = appointment_dt - timedelta(hours=4)
        reminder_time = appointment_dt - timedelta(minutes=1)
        current_time = datetime.now(WAT)

        if reminder_time <= current_time:
            logger.info(
                f"Appointment {appointment.id} is within 4 hours, no reminder scheduled")
            return

        # Create unique job ID
        job_id = f"reminder_{appointment.id}"

        # Add job to scheduler with WAT time, passing appointment ID
        scheduler.add_job(
            send_reminder_notification,
            trigger=DateTrigger(run_date=reminder_time),
            # Pass ID instead of object for serialization
            args=[appointment.id],
            id=job_id,
            replace_existing=True,
            timezone=WAT
        )
        logger.info(f"Scheduled reminder for {appointment.id} at "
                    f"{reminder_time.strftime('%Y-%m-%d %H:%M %Z')}")
        job = scheduler.get_job(job_id)
        if job:
            logger.info(
                f"Job {job_id} confirmed in scheduler: next run at {job.next_run_time}")
        else:
            logger.error(
                f"Job {job_id} not found in scheduler after scheduling")
    except Exception as e:
        logger.error(f"Failed to schedule reminder: {str(e)}")


async def send_whatsapp_message(phone_number: str, name: str, appointment_date, appointment_time):
    media_metadata_url = f"https://graph.facebook.com/v22.0/634136199777636/messages"
    headers = {"Authorization": f"Bearer EAAMzcBIJtngBOyFZBiMZBH0GnacrALWRADQmZCkso9XIwaSJHQhg8J68CNKxB5v8OHZBWs7WEpriZBPSMRbbwvCEioxDRIfJTIxGPO7a8TktBCl3ZC4uUdYqiCa0d9jcjxz4U6TZB0017DPcixW8xhiqQoZAEC1V7gg0vcnZCvaSuadT4I46G4K285ZBeiVHXbj9NfnQZDZD",
               "Content-Type": "application/json"}

    data = {"messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": str(phone_number),
            "type": "template",
            "template": {
                "name": "appointment_reminder",
                "language": {
                    "code": "en_US"
                },
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "location",
                                "location": {
                                    "latitude": "9.0764",
                                    "longitude": "7.4669",
                                    "name": "Apostle Uche's office",
                                    "address": "TEFCON Mall, Lokogoma Rd, beside Wuse Within, Lokogoma, Abuja 900001, Federal Capital Territory"
                                }
                            }
                        ]
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "parameter_name": "name",
                                "text": str(name)
                            },
                            {
                                "type": "text",
                                "parameter_name": "apostle",
                                "text": "Apostle Uche Raymond"
                            },
                            {
                                "type": "text",
                                "parameter_name": "date_and_time",
                                "text": f"{str(appointment_date)} at {str(appointment_time)}"
                            }
                        ]
                    }
                ]}}
    async with httpx.AsyncClient() as client:
        metadata_response = await client.post(media_metadata_url, headers=headers, json=data)
        metadata_response.raise_for_status()
        metadata = metadata_response.json()
        try:
            reply = metadata.get("messages")
            reply_status = reply[0]['message_status']
            logging.info("Accepted appoitment message Succesfully sent")
        except BaseException as e:
            logging.info(f"This went wrong woth accepted appointment {e}")


async def send_reminder_notification(appointment_id: int):
    """Send reminder in WAT time context using async database session."""
    async with AsyncSession(engine) as db:
        try:
            # Query appointment asynchronously
            result = await db.execute(
                select(Appointment).filter(Appointment.id == appointment_id)
            )
            appointment = result.scalars().first()
            if not appointment:
                logger.warning(f"Appointment {appointment_id} not found")
                return

            # Format time in WAT
            try:
                hour, minute = ast.literal_eval(appointment.appointment_time)
                wat_time = f"{hour:02d}:{minute:02d} WAT"
                appointment_date = datetime.strptime(
                    appointment.appointment_date,
                    "%Y-%m-%d"
                ).strftime('%d %b %Y')
            except (ValueError, SyntaxError):
                wat_time = "Invalid Time"
                appointment_date = "Unknown Date"

            # Placeholder for async WhatsApp message sending
            await send_whatsapp_message(appointment.phone_number, appointment.user_name, appointment_date, wat_time)
            logger.info(
                f"Sent reminder for {appointment_id} to {appointment.phone_number}")

        except Exception as e:
            logger.error(f"Reminder failed for {appointment_id}: {str(e)}")


# async def test_delete_old_appointments():
#     scheduler = setup_scheduler()
#     await delete_old_appointments(scheduler)


# asyncio.run(test_delete_old_appointments())


# # Configure WAT timezone
# WAT = timezone('Africa/Lagos')  # Covers West Africa Time (UTC+1)
# logger = logging.getLogger(__name__)


# def setup_scheduler():
#     jobstores = {
#         'default': SQLAlchemyJobStore(url="postgresql+asyncpg://postgres:boywithuke@localhost:5432/NTIEM_BOT")
#     }
#     return AsyncIOScheduler(jobstores=jobstores, timezone=WAT)


# async def schedule_appointment_reminder(appointment, scheduler=AsyncIOScheduler):
#     """Schedule a reminder for a new appointment in WAT"""
#     try:
#         # Parse appointment date and time in WAT
#         appointment_date = datetime.strptime(
#             appointment.appointment_date,
#             "%Y-%m-%d"
#         ).date()

#         # Parse time tuple string "(11, 23)" -> (hour, minute)
#         try:
#             time_tuple = ast.literal_eval(appointment.appointment_time)
#             if not isinstance(time_tuple, tuple) or len(time_tuple) != 2:
#                 raise ValueError
#             hour, minute = time_tuple
#         except (ValueError, SyntaxError):
#             logger.error(
#                 f"Invalid time format for appointment {appointment.id}")
#             return

#         # Create WAT-aware datetime
#         appointment_dt = WAT.localize(
#             datetime.combine(
#                 appointment_date,
#                 datetime.min.time().replace(hour=hour, minute=minute)
#             )
#         )

#         # Calculate reminder time (6 hours before in WAT)
#         reminder_time = appointment_dt - timedelta(hours=6)
#         current_time = datetime.now(WAT)

#         if reminder_time <= current_time:
#             logger.info(
#                 f"Appointment {appointment.id} is within 6 hours, no reminder scheduled")
#             return

#         # Create unique job ID
#         job_id = f"reminder_{appointment.id}"

#         # Add job to scheduler with WAT time
#         scheduler.add_job(
#             send_reminder_notification,
#             trigger=DateTrigger(run_date=reminder_time),
#             args=[appointment],
#             id=job_id,
#             replace_existing=True,
#             timezone=WAT
#         )
#         logger.info(
#             f"Scheduled reminder for {appointment.id} at {reminder_time.strftime('%Y-%m-%d %H:%M %Z')}")

#     except Exception as e:
#         logger.error(f"Failed to schedule reminder: {str(e)}")


# async def send_reminder_notification(appointment):
#     """Send reminder in WAT time context"""
#     async for db in get_async_db():  # get async db
#         try:
#             appointment_id = appointment.id
#             if not appointment_id:
#                 logger.warning(f"Appointment {appointment_id} not found")
#                 return

#             # Format time in WAT
#             try:
#                 hour, minute = ast.literal_eval(appointment.appointment_time)
#                 wat_time = f"{hour:02d}:{minute:02d} WAT"
#                 appointment_date = datetime.strptime(
#                     appointment.appointment_date,
#                     "%Y-%m-%d"
#                 ).strftime('%d %b %Y')
#             except:
#                 wat_time = "Invalid Time"
#                 appointment_date = "Unknown Date"

#             logger.info(f"Sending WAT reminder for {appointment_id}")
#             logger.info(
#                 f"Recipient: {appointment.user_name} ({appointment.phone_number})")
#             logger.info(f"Scheduled: {appointment_date} at {wat_time}")

#             # Include function that will send message to the specified whatsapp user
#             # Remember that this reminder message should be using your created whatsapp utility template
#             # As this might exceed the 24 hour open window

#         except Exception as e:
#             logger.error(f"Reminder failed: {str(e)}")
#         finally:
#             await db.close()  # close the async db session.

##########################################################################################

# from datetime import datetime, timedelta
# from models import Appointment
# from database import get_db
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
# from apscheduler.triggers.date import DateTrigger
# import logging
# import ast
# import os
# from pytz import timezone
# from config import app_settings

# # Configure WAT timezone
# WAT = timezone('Africa/Lagos')  # Covers West Africa Time (UTC+1)
# logger = logging.getLogger(__name__)


# def setup_scheduler():
#     jobstores = {
#         'default': SQLAlchemyJobStore(url=f"postgresql://{app_settings.database_username}:{
#             app_settings.database_password}@{app_settings.database_hostname}:{app_settings.database_port}/{app_settings.database_name}")
#     }
#     return AsyncIOScheduler(jobstores=jobstores, timezone=WAT)


# async def schedule_appointment_reminder(appointment, scheduler=AsyncIOScheduler):
#     """Schedule a reminder for a new appointment in WAT"""
#     try:
#         # Parse appointment date and time in WAT
#         appointment_date = datetime.strptime(
#             appointment.appointment_date,
#             "%Y-%m-%d"
#         ).date()

#         # Parse time tuple string "(11, 23)" -> (hour, minute)
#         try:
#             time_tuple = ast.literal_eval(appointment.appointment_time)
#             if not isinstance(time_tuple, tuple) or len(time_tuple) != 2:
#                 raise ValueError
#             hour, minute = time_tuple
#         except (ValueError, SyntaxError):
#             logger.error(f"Invalid time format for appointment {
#                          appointment.id}")
#             return

#         # Create WAT-aware datetime
#         appointment_dt = WAT.localize(
#             datetime.combine(
#                 appointment_date,
#                 datetime.min.time().replace(hour=hour, minute=minute)
#             )
#         )

#         # Calculate reminder time (6 hours before in WAT)
#         reminder_time = appointment_dt - timedelta(hours=6)
#         current_time = datetime.now(WAT)

#         if reminder_time <= current_time:
#             logger.info(f"Appointment {
#                         appointment.id} is within 6 hours, no reminder scheduled")
#             return

#         # Create unique job ID
#         job_id = f"reminder_{appointment.id}"

#         # Add job to scheduler with WAT time
#         scheduler.add_job(
#             send_reminder_notification,
#             trigger=DateTrigger(run_date=reminder_time),
#             args=[appointment],
#             id=job_id,
#             replace_existing=True,
#             timezone=WAT
#         )
#         logger.info(f"Scheduled reminder for {appointment.id} at {
#                     reminder_time.strftime('%Y-%m-%d %H:%M %Z')}")

#     except Exception as e:
#         logger.error(f"Failed to schedule reminder: {str(e)}")


# async def send_reminder_notification(appointment):
#     """Send reminder in WAT time context"""
#     db = next(get_db())
#     try:
#         appointment_id = appointment.id
#         if not appointment_id:
#             logger.warning(f"Appointment {appointment_id} not found")
#             return

#         # Format time in WAT
#         try:
#             hour, minute = ast.literal_eval(appointment.appointment_time)
#             wat_time = f"{hour:02d}:{minute:02d} WAT"
#             appointment_date = datetime.strptime(
#                 appointment.appointment_date,
#                 "%Y-%m-%d"
#             ).strftime('%d %b %Y')
#         except:
#             wat_time = "Invalid Time"
#             appointment_date = "Unknown Date"

#         logger.info(f"Sending WAT reminder for {appointment_id}")
#         logger.info(f"Recipient: {appointment.user_name} ({
#                     appointment.phone_number})")
#         logger.info(f"Scheduled: {appointment_date} at {wat_time}")

#         # Include function that will send message to the specifies whatsapp user
#         # Remember that this reminder message should be using your created whatsapp utlilty template
#         # As this might excede the 24 hour open window

#     except Exception as e:
#         logger.error(f"Reminder failed: {str(e)}")
#     finally:
#         db.close()
