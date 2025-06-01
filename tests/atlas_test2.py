from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from datetime import datetime, UTC
import asyncio

# MongoDB connection setup
uri = "mongodb+srv://Akachi:godwin2007@myatlasclusteredu.mqq6x.mongodb.net/?retryWrites=true&w=majority&appName=myAtlasClusterEDU"
client = AsyncIOMotorClient(uri, server_api=ServerApi(
    version='1', strict=True, deprecation_errors=True))

# Select database and collection
db = client['chat_app']
chat_history = db['chat_history']


async def update_chat_history(user_id, user_message, bot_response):
    """
    Update user's chat history, keeping only the last 20 messages.
    Uses $slice to automatically remove oldest messages as needed.

    :param user_id: Unique identifier for the user
    :param user_message: The user's message content
    :param bot_response: The bot's response content
    """
    # New messages to add
    user_msg = {
        "sender": user_id,
        "content": user_message,
        "timestamp": datetime.now(UTC)
    }
    bot_msg = {
        "sender": "bot",
        "content": bot_response,
        "timestamp": datetime.now(UTC)
    }

    # Append new messages and cap at 20 using $slice
    result = await chat_history.update_one(
        {"_id": user_id},
        {
            "$push": {
                "messages": {
                    "$each": [user_msg, bot_msg],  # Add both messages
                    "$slice": -4                # Keep only the last 4 messages
                }
            }
        },
        upsert=True
    )

    # Estimate new count (for logging purposes)
    user_doc = await chat_history.find_one({"_id": user_id})
    new_count = len(user_doc["messages"]
                    ) if user_doc and "messages" in user_doc else 0
    print(f"Chat history updated for {user_id}. New count: {new_count}")


async def get_chat_history(user_id):
    """
    Retrieve the chat history for a given user.

    :param user_id: Unique identifier for the user
    :return: List of messages or an empty list if user not found or no messages exist
    """
    user_doc = await chat_history.find_one({"_id": user_id})
    if user_doc and "messages" in user_doc:
        return user_doc["messages"]
    return []


async def main():
    user_id = "user123"
    try:
        # Simulate adding messages to reach 6
        for i in range(2):  # Add 10 pairs (6 messages total)
            await update_chat_history(user_id, f"User msg {i}", f"Bot response {i}")

        # Add one more pair, which should keep it at 6 due to pruning
        await update_chat_history(user_id, "New user message", "New bot response")

        # Retrieve and print history
        history = await get_chat_history(user_id)
        print(f"Chat history for {user_id} (length: {len(history)}):")
        for msg in history:
            print(f"[{msg['timestamp']}] {msg['sender']}: {msg['content']}")

    except BaseException as e:
        print(e)

    finally:
        client.close()
        print("MongoDB client closed.")

if __name__ == "__main__":
    asyncio.run(main())
