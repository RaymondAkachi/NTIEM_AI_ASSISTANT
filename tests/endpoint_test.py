import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def verify_webhook_subscription():
    """Verify and update webhook subscription for messages event."""
    api_url = "https://graph.facebook.com/v20.0/634136199777636/subscriptions"
    headers = {
        "Authorization": "Bearer EAAMzcBIJtngBOyFZBiMZBH0GnacrALWRADQmZCkso9XIwaSJHQhg8J68CNKxB5v8OHZBWs7WEpriZBPSMRbbwvCEioxDRIfJTIxGPO7a8TktBCl3ZC4uUdYqiCa0d9jcjxz4U6TZB0017DPcixW8xhiqQoZAEC1V7gg0vcnZCvaSuadT4I46G4K285ZBeiVHXbj9NfnQZDZD",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            # Check current subscriptions
            response = await client.get(url=api_url, headers=headers)
            response.raise_for_status()
            subscriptions = response.json()
            logger.info(f"Current webhook subscriptions: {subscriptions}")
            subscribed_fields = subscriptions.get(
                "data", [{}])[0].get("subscribed_fields", [])
            # Ensure 'messages' is subscribed
            if "messages" not in subscribed_fields:
                # Update subscription to include 'messages'
                payload = {
                    "object": "whatsapp_business_account",
                    "subscribed_fields": ["messages"],
                    "callback_url": "https://your-ec2-public-ip.ngrok-free.app/message",
                    "verify_token": "YOUR_VERIFY_TOKEN"
                }
                response = await client.post(url=api_url, headers=headers, json=payload)
                response.raise_for_status()
                logger.info(
                    "Updated webhook subscription to include 'messages'")
            else:
                logger.info("Webhook already subscribed to 'messages'")
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error verifying subscription: {str(e)}")
            raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(verify_webhook_subscription())
