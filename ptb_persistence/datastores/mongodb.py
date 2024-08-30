from .base import BaseDataStore

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection
)
from dataclasses import dataclass, field
from typing import (
    Literal,
    Tuple,
    Union
    )

from telegram.ext import PersistenceInput
import ast



@dataclass
class DataType:
    database: AsyncIOMotorDatabase
    collection_input: AsyncIOMotorCollection | str | None = None
    collection: AsyncIOMotorCollection | None = None
    ignore_keys: list[str] = field(default_factory=list)


    def __post_init__(self) -> None:
        self._exist = self.collection_input is not None


    async def post_init(self) -> None:
        self._exist = False

        if self.collection_input is None:
            return
        
        if not isinstance(self.collection_input, AsyncIOMotorCollection):
            self.collection = self.database[self.collection_input]
        else:
            self.collection = self.collection_input
        
        self._exist = True


    def cleanup_new_data(self, data: dict) -> None:
        for item in self.ignore_keys:
            data.pop(item, None)


    def exists(self) -> bool:
        return self._exist



class MongoDBDataStore(BaseDataStore):

    def __init__(self,
            client_or_uri: AsyncIOMotorClient | str,
            database: AsyncIOMotorDatabase | str,
            collection_userdata: AsyncIOMotorCollection | str | None = None,
            collection_chatdata: AsyncIOMotorCollection | str | None = None,
            collection_botdata: AsyncIOMotorCollection | str | None = None,
            collection_conversationsdata: AsyncIOMotorCollection | str | None = None,
            ignore_general_keys: list[str] = None,
            ignore_user_keys: list[str] = None,
            ignore_chat_keys: list[str] = None,
            ignore_bot_keys: list[str] = None,
            ignore_conversations_keys: list[str] = None,
            ) -> None:
        """
        A data store implementation for MongoDB.


        :param client_or_uri: Client instance or connection uri
        :param database: Database instance or name

        :param collection_userdata: Collection instance or name
                (If None, data will not be persisted)
        :param collection_chatdata: Collection instance or name
                (If None, data will not be persisted)
        :param collection_botdata: Collection instance or name
                (If None, data will not be persisted)
        :param collection_conversationsdata: Collection instance or name
                (If None, data will not be persisted)

        :param ignore_general_keys: A list of keys to not persist in the data store.
                Ex: ['_cache', 'ignored-key'] (Will be applied to all)
        :param ignore_user_keys: A list of keys to not persist in the user data store
        :param ignore_chat_keys: A list of keys to not persist in the chat data store
        :param ignore_bot_keys: A list of keys to not persist in the bot data store
        :param ignore_conversations_keys: A list of keys to not persist in the conversation data store
        """
        
        if not isinstance(client_or_uri, AsyncIOMotorClient):
            self._client = AsyncIOMotorClient(client_or_uri)
            self._close_client = True
        else:
            self._client = client_or_uri
            self._close_client = False

        if not isinstance(database, AsyncIOMotorDatabase):
            self._database = AsyncIOMotorDatabase(
                self._client,
                database
                )
        else:
            self._database = database


        ignore_general_keys = ignore_general_keys or []
        ignore_user_keys = ignore_user_keys or []
        ignore_chat_keys = ignore_chat_keys or []
        ignore_bot_keys = ignore_bot_keys or []
        ignore_conversations_keys = ignore_conversations_keys or []

        self._user_data = DataType(
            database=self._database,
            collection_input=collection_userdata,
            ignore_keys=ignore_general_keys + ignore_user_keys,
        )

        self._chat_data = DataType(
            database=self._database,
            collection_input=collection_chatdata,
            ignore_keys=ignore_general_keys + ignore_chat_keys,
        )

        self._bot_data = DataType(
            database=self._database,
            collection_input=collection_botdata,
            ignore_keys=ignore_general_keys + ignore_bot_keys,
        )

        self._conversations_data = DataType(
            database=self._database,
            collection_input=collection_conversationsdata,
            ignore_keys=ignore_general_keys + ignore_conversations_keys,
        )

        super().__init__()


    async def post_init(self) -> None:
        if self._inited:
            return
        
        await self._user_data.post_init()
        await self._chat_data.post_init()
        await self._bot_data.post_init()
        await self._conversations_data.post_init()
        
        return await super().post_init()
    

    async def get_data(self, data_type, data_id: int | None = None) -> dict:
        await self.post_init()

        data: dict = {}

        data_type = self._get_data_type(data_type)
        if not data_type.exists():
            return data
        

        cursor = data_type.collection.find(
            filter=({'_id': data_id} if data_id is not None else {}),
            batch_size=10000,
            allow_disk_use=True
        )

        doc: dict
        for doc in await cursor.to_list(length=None):
            _id = doc.pop("_id")
            data[_id] = doc
        
        return data


    async def update_data(self, data_type, data_id: int, new_data: dict) -> None:
        await self.post_init()

        data_type = self._get_data_type(data_type)
        if not data_type.exists():
            return
        
        data_type.cleanup_new_data(new_data)

        await data_type.collection.replace_one(
            {"_id": data_id},
            new_data,
            upsert=True
            )


    async def refresh_data(self, data_type, data_id: int, local_data: dict) -> None:

        data = await self.get_data(
            data_type=data_type,
            data_id=data_id
        )
        single_data = data.get(data_id, {})

        if single_data:
            local_data.update(single_data)


    async def drop_data(self, data_type, data_id: int) -> None:
        await self.post_init()

        data_type = self._get_data_type(data_type)
        if not data_type.exists():
            return

        await data_type.collection.delete_one({
            "_id": data_id}
            )


    async def get_conversations(self, name: str) -> dict:
        await self.post_init()

        data_type = self._get_data_type(
            data_type='conversations'
        )
        if not data_type.exists():
            return

        data: dict = {}

        if doc := await data_type.collection.find_one({"_id": name}):
            doc: dict
            doc.pop('_id')
            data[name] = {
                ast.literal_eval(key_str): value
                for key_str, value in doc.items()
            }
        else:
            data[name] = {}

        return data


    async def update_conversation(self,
            name: str,
            key: Tuple[Union[int, str], ...],
            new_state: object | None
            ) -> None:
        await self.post_init()

        data_type = self._get_data_type(
            data_type='conversations'
        )
        if not data_type.exists():
            return
        
        await data_type.collection.replace_one(
            {'_id': name},
            {str(key): new_state},
            upsert=True
        )


    def build_persistence_input(self) -> PersistenceInput:
        persistence_input = PersistenceInput(
            bot_data=self._bot_data.exists(),
            chat_data=self._chat_data.exists(),
            user_data=self._user_data.exists(),
            callback_data=False
        )
        return persistence_input


    async def flush(self) -> None:
        if self._close_client:
            self._client.close()


    def _get_data_type(self,
            data_type: Literal['user', 'chat', 'bot', 'conversations']
            ) -> DataType:
        
        if data_type == 'user':
            return self._user_data
        
        elif data_type == 'chat':
            return self._chat_data
        
        elif data_type == 'bot':
            return self._bot_data
        
        elif data_type == 'conversations':
            return self._conversations_data

        raise ValueError(f'Invalid Data Type: {data_type}')
