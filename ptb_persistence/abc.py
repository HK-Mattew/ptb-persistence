from typing import (
    Literal,
    Tuple,
    Union
    )
from abc import ABCMeta, abstractmethod
from telegram.ext import PersistenceInput




class DataStore(metaclass=ABCMeta):
    """
    Interface for data stores.

    Data stores control data methods.
    """

    @abstractmethod
    async def post_init(self) -> None:
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
            data_id: int, new_data: dict) -> None:
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
    async def update_conversation(self,
            name: str,
            key: Tuple[Union[int, str], ...],
            new_state: object | None
            ) -> None:
        """
        """


    @abstractmethod
    def build_persistence_input(self) -> PersistenceInput:
        """
        """


    @abstractmethod
    async def flush(self) -> None:
        """
        """
    
