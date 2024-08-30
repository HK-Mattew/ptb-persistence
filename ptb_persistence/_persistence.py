from typing import (
    Tuple,
    Dict,
    Any,
    )
from .abc import DataStore
from telegram.ext import BasePersistence




class PTBPersistence(BasePersistence):
    
    def __init__(
            self,
            data_store: DataStore,
            update_interval: float = 60
            ) -> None:
        """
        Persistent data class for PTB.


        :param data_store (:obj:`DataStore`) The data store where data will be persisted
            
            [Example]
            from ptb_persistence import PTBPersistence
            from ptb_persistence.datastores.mongodb import MongoDBDataStore

            ptb_persistence = PTBPersistence(
                data_store=MongoDBDataStore(...)
            )

        :param update_interval (:obj:`int` | :obj:`float`, optional): The
            :class:`~telegram.ext.Application` will update
            the persistence in regular intervals. This parameter specifies the time (in seconds) to
            wait between two consecutive runs of updating the persistence. Defaults to ``60``
            seconds.
        """

        self._data_store = data_store
        self.store_data = self._data_store.build_persistence_input()
        super().__init__(
            store_data=self.store_data,
            update_interval=update_interval,
        )


    # User methods
    async def get_user_data(self) -> Dict[int, Any]:
        return await self._data_store.get_data(
            data_type='user'
        )


    async def update_user_data(self, user_id: int, local_data: dict) -> None:
        return await self._data_store.update_data(
            data_type='user',
            data_id=user_id,
            local_data=local_data
        )


    async def refresh_user_data(self, user_id: int, local_data: dict) -> None:
        return await self._data_store.refresh_data(
            data_type='user',
            data_id=user_id,
            local_data=local_data
        )


    async def drop_user_data(self, user_id: int) -> None:
        return await self._data_store.drop_data(
            data_type='user',
            data_id=user_id
        )


    # Chat methods
    async def get_chat_data(self) -> Dict[int, Any]:
        return await self._data_store.get_data(
            data_type='chat'
        )
    

    async def update_chat_data(self, chat_id: int, local_data: dict) -> None:
        return await self._data_store.update_data(
            data_type='chat',
            data_id=chat_id,
            local_data=local_data
        )


    async def refresh_chat_data(self, chat_id: int, local_data: dict) -> None:
        return await self._data_store.refresh_data(
            data_type='chat',
            data_id=chat_id,
            local_data=local_data
        )


    async def drop_chat_data(self, chat_id: int) -> None:
        return await self._data_store.drop_data(
            data_type='chat',
            data_id=chat_id
        )
    

    # Bot methods
    async def get_bot_data(self) -> Dict[int, Any]:
        return await self._data_store.get_data(
            data_type='bot'
        )
    

    async def update_bot_data(self, local_data: dict) -> None:
        return await self._data_store.update_data(
            data_type='bot',
            data_id=self.bot.id,
            local_data=local_data
        )


    async def refresh_bot_data(self, local_data: dict) -> None:
        return await self._data_store.refresh_data(
            data_type='bot',
            data_id=self.bot.id,
            local_data=local_data
        )
    

    # Conversation methods
    async def get_conversations(self, name: str) -> dict:
        return await self._data_store.get_conversations(
            name=name
        )


    async def update_conversation(self,
            name: str,
            key: Tuple[int | str, ...],
            local_state: object | None
            ) -> None:
        return await self._data_store.update_conversation(
            name=name,
            key=key,
            local_state=local_state
        )
    

    # Callback methods
    async def get_callback_data(self) -> tuple | None:
        # TODO: Develop method
        return await super().get_callback_data()


    async def update_callback_data(self, local_data: tuple) -> None:
        # TODO: Develop method
        return await super().update_callback_data(local_data)


    # Flush methods
    async def flush(self) -> None:
        return await self._data_store.flush()

