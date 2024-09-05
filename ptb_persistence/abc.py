from ._types import ConversationDict
from typing import (
    Literal,
    Tuple,
    Union
    )
from logging import Logger
from abc import ABCMeta, abstractmethod
from telegram.ext import PersistenceInput




class DataStore(metaclass=ABCMeta):
    """
    Interface for data stores.

    Data stores control data methods.
    """

    @abstractmethod
    async def post_init(self, logger: Logger) -> None:
        """
        """


    @abstractmethod
    async def get_data(self,
            data_type: Literal['user', 'chat', 'bot']
            ):
        """
        """


    @abstractmethod
    async def update_data(self,
            data_type: Literal['user', 'chat', 'bot'],
            data_id: int, local_data: dict) -> None:
        """
        """


    @abstractmethod
    async def refresh_data(self,
            data_type: Literal['user', 'chat', 'bot'],
            data_id: int,
            local_data: dict
            ) -> None:
        """
        """


    @abstractmethod
    async def drop_data(self,
            data_type: Literal['user', 'chat', 'bot'],
            data_id: int) -> None:
        """
        """


    @abstractmethod
    async def get_conversations(self, name: str) -> dict:
        """
        """


    @abstractmethod
    async def refresh_conversation(
        self,
        name: str,
        local_data: ConversationDict,
        key: Tuple[Union[int, str], ...] | None = None,
        ) -> None:
        """
        """


    @abstractmethod
    async def update_conversation(self,
            name: str,
            key: Tuple[Union[int, str], ...],
            local_state: object | None
            ) -> None:
        """
        """


    @abstractmethod
    async def flush(self) -> None:
        """
        """


    @abstractmethod
    def build_persistence_input(self) -> PersistenceInput:
        """
        """
    
