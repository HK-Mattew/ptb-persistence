from typing import (
    Union,
    Tuple,
    Dict,
    Any
    )
import functools
from .abc import DataStore
from ._types import ConversationDict
from logging import getLogger, Logger
from telegram.ext import BasePersistence

import time



def log_method(method):
    method_name: str = method.__name__

    @functools.wraps(method)
    async def wrapper(self: 'PTBPersistence', *args, **kwargs):
        self._logger.debug(
            f'PTBPersistence: Calling {method_name!r} method. Args: {args=} Kwargs: {kwargs=}'
            )
        start_time = time.time()
        result = await method(self, *args, **kwargs)
        elapsed_time = time.time() - start_time
        self._logger.debug(
            f'PTBPersistence: Result of {method_name!r} method: {result!r} (Elapsed Time: {elapsed_time:.4f} seconds)'
            )
        return result

    return wrapper



class PTBPersistence(BasePersistence):
    
    def __init__(
            self,
            data_store: DataStore,
            update_interval: float = 60,
            logger: Logger | None = None
            ) -> None:
        """
        Persistent data class for PTB.


        :param data_store (:obj:`DataStore`): The data store where data will be persisted
            
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

        :param logger (:obj: `Logger`): A logger for logs. If None, it will be using getLogger(__name__)
        """

        self._inited: bool = False
        self._data_store = data_store
        self._logger = logger or getLogger(__name__)

        self.store_data = self._data_store.build_persistence_input()
        super().__init__(
            store_data=self.store_data,
            update_interval=update_interval,
        )

    
    async def _post_init(self) -> None:
        if self._inited:
            return
        
        await self._data_store.post_init(
            logger=self._logger
        )
        self._inited = True


    # User methods
    @log_method
    async def get_user_data(self) -> Dict[int, Any]:
        await self._post_init()
        return await self._data_store.get_data(
            data_type='user'
        )


    @log_method
    async def update_user_data(self, user_id: int, data: dict) -> None:
        await self._post_init()
        return await self._data_store.update_data(
            data_type='user',
            data_id=user_id,
            local_data=data
        )


    @log_method
    async def refresh_user_data(self, user_id: int, user_data: dict) -> None:
        await self._post_init()
        return await self._data_store.refresh_data(
            data_type='user',
            data_id=user_id,
            local_data=user_data
        )


    @log_method
    async def drop_user_data(self, user_id: int) -> None:
        await self._post_init()
        return await self._data_store.drop_data(
            data_type='user',
            data_id=user_id
        )


    @log_method
    # Chat methods
    async def get_chat_data(self) -> Dict[int, Any]:
        await self._post_init()
        return await self._data_store.get_data(
            data_type='chat'
        )
    

    @log_method
    async def update_chat_data(self, chat_id: int, data: dict) -> None:
        await self._post_init()
        return await self._data_store.update_data(
            data_type='chat',
            data_id=chat_id,
            local_data=data
        )


    @log_method
    async def refresh_chat_data(self, chat_id: int, chat_data: dict) -> None:
        await self._post_init()
        return await self._data_store.refresh_data(
            data_type='chat',
            data_id=chat_id,
            local_data=chat_data
        )


    @log_method
    async def drop_chat_data(self, chat_id: int) -> None:
        await self._post_init()
        return await self._data_store.drop_data(
            data_type='chat',
            data_id=chat_id
        )
    

    # Bot methods
    @log_method
    async def get_bot_data(self) -> Dict[int, Any]:
        await self._post_init()
        return await self._data_store.get_data(
            data_type='bot'
        )
    

    @log_method
    async def update_bot_data(self, data: dict) -> None:
        await self._post_init()
        return await self._data_store.update_data(
            data_type='bot',
            data_id=self.bot.id,
            local_data=data
        )


    @log_method
    async def refresh_bot_data(self, bot_data: dict) -> None:
        await self._post_init()
        return await self._data_store.refresh_data(
            data_type='bot',
            data_id=self.bot.id,
            local_data=bot_data
        )
    

    # Conversation methods
    @log_method
    async def get_conversations(self, name: str) -> dict:
        await self._post_init()
        return await self._data_store.get_conversations(
            name=name
        )


    @log_method
    async def refresh_conversation(
        self,
        name: str,
        conversations_data: ConversationDict,
        key: Tuple[Union[int, str], ...] | None = None,
        ) -> None:
        await self._post_init()
        return await self._data_store.refresh_conversation(
            name=name,
            local_data=conversations_data,
            key=key
        )


    @log_method
    async def update_conversation(self,
            name: str,
            key: Tuple[int | str, ...],
            new_state: object | None
            ) -> None:
        await self._post_init()
        return await self._data_store.update_conversation(
            name=name,
            key=key,
            local_state=new_state
        )
    

    # Callback methods
    @log_method
    async def get_callback_data(self) -> tuple | None:
        # TODO: Develop method
        await self._post_init()
        return await super().get_callback_data()


    @log_method
    async def update_callback_data(self, data: tuple) -> None:
        # TODO: Develop method
        await self._post_init()
        return await super().update_callback_data(data)


    # Flush methods
    @log_method
    async def flush(self) -> None:
        await self._post_init()
        return await self._data_store.flush()

