# from pymongo import MongoClient
# from pymongo.errors import ConnectionFailure, ConfigurationError
# # Your connection string
# uri = "mongodb+srv://raymondakachi2007:nBh3iayDKbSzKfN7@ntiembotcluster.kcbsw.mongodb.net/?retryWrites=true&w=majority&appName=NTIEMbotcluster"
# client = MongoClient(uri)

# # Test the connection with a ping

# try:
#     # Test connection with a ping
#     client.admin.command("ping")
#     print("Connected to MongoDB Atlas successfully!")

#     # Optional: List databases to confirm access
#     print("Databases:", client.list_database_names())
# except ConnectionFailure as e:
#     print(f"Connection failed: {e}")
# except ConfigurationError as e:
#     print(f"Configuration error: {e}")
# except Exception as e:
#     print(f"Unexpected error: {e}")
# finally:
#     client.close()


# from pymongo.mongo_client import MongoClient
# from motor.motor_asyncio import AsyncIOMotorClient
# from pymongo.server_api import ServerApi

# uri = "mongodb+srv://raymondakachi:godwin2007@ntiembotcluster.kcbsw.mongodb.net/?retryWrites=true&w=majority&appName=NTIEMbotcluster"

# # Create a new client and connect to the server
# client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)


# from langgraph.checkpoint.base import BaseCheckpointSaver, CheckpointTuple
# from pymongo import MongoClient
# from typing import Dict, Optional, Any, List, Tuple, AsyncGenerator

# class MongoDBCheckpointSaver(BaseCheckpointSaver):
#     def __init__(self, uri: str, db_name: str = "chat_db", collection_name: str = "chat_history", max_history: int = 10):
#         try:
#             self.client = MongoClient(uri, connectTimeoutMS=30000, socketTimeoutMS=30000)
#             # Test connection
#             self.client.admin.command("ping")
#             print("Connected to MongoDB Atlas successfully")
#         except Exception as e:
#             raise ConnectionError(f"Failed to connect to MongoDB: {e}")
#         self.db = self.client[db_name]
#         self.collection = self.db[collection_name]
#         self.max_history = max_history

#     def get_tuple(self, config: Dict[str, Any]) -> Optional[CheckpointTuple]:
#         user_id = config["configurable"]["user_id"]
#         doc = self.collection.find_one({"user_id": user_id})
#         if doc:
#             checkpoint = {"messages": doc.get("messages", [])}
#             metadata = doc.get("metadata", {})
#             return CheckpointTuple(config=config, checkpoint=checkpoint, metadata=metadata)
#         return None

#     async def aget_tuple(self, config: Dict[str, Any]) -> Optional[CheckpointTuple]:
#         return self.get_tuple(config)

#     def put(self, config: Dict[str, Any], checkpoint: Dict[str, Any], metadata: Dict[str, Any]) -> None:
#         user_id = config["configurable"]["user_id"]
#         messages = checkpoint.get("messages", [])[-self.max_history:]
#         doc = {"user_id": user_id, "messages": messages, "metadata": metadata}
#         self.collection.replace_one({"user_id": user_id}, doc, upsert=True)

#     async def aput(self, config: Dict[str, Any], checkpoint: Dict[str, Any], metadata: Dict[str, Any]) -> None:
#         self.put(config, checkpoint, metadata)

#     def put_writes(self, config: Dict[str, Any], writes: List[Tuple[str, Any]], task_id: str) -> None:
#         pass

#     async def aput_writes(self, config: Dict[str, Any], writes: List[Tuple[str, Any]], task_id: str) -> None:
#         pass

#     def list(self, config: Dict[str, Any]) -> List[CheckpointTuple]:
#         return []

#     async def alist(self, config: Dict[str, Any]) -> AsyncGenerator[CheckpointTuple, None]:
#         return []

# # Test it
# uri = "mongodb+srv://raymondakachi:godwin2007@ntiembotcluster.kcbsw.mongodb.net/?retryWrites=true&w=majority&appName=NTIEMbotcluster"  # Replace with your URI
# checkpointer = MongoDBCheckpointSaver(uri)


#####################################################################

# # from pymongo import MongoClient
# from motor.motor_asyncio import AsyncIOMotorClient
# from pymongo.server_api import ServerApi
# from datetime import datetime, UTC
# import asyncio

# # MongoDB connection setup
# uri = "mongodb+srv://Akachi:godwin2007@myatlasclusteredu.mqq6x.mongodb.net/?retryWrites=true&w=majority&appName=myAtlasClusterEDU"
# client = AsyncIOMotorClient(uri, server_api=ServerApi(version='1', strict=True, deprecation_errors=True))

# # Select database and collection
# db = client['chat_app']
# chat_history = db['chat_history']

# async def update_chat_history(user_id, user_message, bot_response):
#     """
#     Update user's chat history, keeping only the last 20 messages.
#     Uses $slice to automatically remove oldest messages as needed.

#     :param user_id: Unique identifier for the user
#     :param user_message: The user's message content
#     :param bot_response: The bot's response content
#     """
#     # New messages to add
#     user_msg = {
#         "sender": user_id,
#         "content": user_message,
#         "timestamp": datetime.now(UTC)
#     }
#     bot_msg = {
#         "sender": "bot",
#         "content": bot_response,
#         "timestamp": datetime.now(UTC)
#         #correct timestamp implementation: "timesamp": datetime.now(datetime.UTC)
#     }

#     # Append new messages and cap at 20 using $slice
#     result = await chat_history.update_one(
#         {"_id": user_id},
#         {
#             "$push": {
#                 "messages": {
#                     "$each": [user_msg, bot_msg],  # Add both messages
#                     "$slice": -20                  # Keep only the last 20 messages
#                 }
#             }
#         },
#         upsert=True
#     )

#     # Estimate new count (for logging purposes)
#     user_doc = await chat_history.find_one({"_id": user_id})
#     new_count = len(user_doc["messages"]) if user_doc and "messages" in user_doc else 0
#     print(f"Chat history updated for {user_id}. New count: {new_count}")

# async def get_chat_history(user_id):
#     """
#     Retrieve the chat history for a given user.

#     :param user_id: Unique identifier for the user
#     :return: List of messages or None if user not found
#     """
#     user_doc = await chat_history.find_one({"_id": user_id})
#     if user_doc and "messages" in user_doc:
#         return user_doc["messages"]
#     return []

# # Example usage
# try:
#     user_id = "user123"

#     # Simulate adding messages to reach 20
#     for i in range(10):  # Add 10 pairs (20 messages total)
#         asyncio.run(update_chat_history(user_id, f"User msg {i}", f"Bot response {i}"))

#     # # Now add one more pair, triggering prune of 10
#     asyncio.run(update_chat_history(user_id, "New user message", "New bot response"))

#     # # Retrieve and print history
#     history = asyncio.run(get_chat_history(user_id))
#     print(f"Chat history for {user_id} (length: {len(history)}):")
#     for msg in history:
#         print(f"[{msg['timestamp']}] {msg['sender']}: {msg['content']}")

# finally:
#     client.close()


# from motor.motor_asyncio import AsyncIOMotorClient
# from pymongo.server_api import ServerApi
# from datetime import datetime, UTC

# async def ping_server():
#   # Replace the placeholder with your Atlas connection string
#   uri = "mongodb+srv://Akachi:godwin2007@myatlasclusteredu.mqq6x.mongodb.net/?retryWrites=true&w=majority&appName=myAtlasClusterEDU"

#   # Set the Stable API version when creating a new client
#   client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))

#   # Send a ping to confirm a successful connection
#   try:
#       await client.admin.command('ping')
#       print("Pinged your deployment. You successfully connected to MongoDB!")
#   except Exception as e:
#       print(e)

# asyncio.run(ping_server())

x = "Akachi_mp4.mp4"
print(x.split('.'))
