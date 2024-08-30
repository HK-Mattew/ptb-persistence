from ptb_persistence.datastores.mongodb import MongoDBDataStore
from motor.motor_asyncio import AsyncIOMotorClient
from telegram.ext import PersistenceInput
import pymongo.errors
import pytest
import config


pytestmark = pytest.mark.asyncio(loop_scope="session")



async def test_update_data(motor_client: AsyncIOMotorClient):

    data_store = MongoDBDataStore(
        client_or_uri=motor_client,
        database=config.MONGO_DB_NAME,
        collection_userdata='userdata'
    )
    
    result = await data_store.update_data(
        data_type='user',
        data_id=12345678,
        new_data={
            'my_key': 'value of my key'
        }
    )

    assert result is None


async def test_get_data(motor_client: AsyncIOMotorClient):

    data_store = MongoDBDataStore(
        client_or_uri=motor_client,
        database=config.MONGO_DB_NAME,
        collection_userdata='userdata'
    )
    
    data = await data_store.get_data(
        data_type='user'
    )

    assert isinstance(data, dict)
    assert len(data) == 1
    assert data[12345678] == {
        'my_key': 'value of my key'
    }


async def test_refresh_data(motor_client: AsyncIOMotorClient):

    data_store = MongoDBDataStore(
        client_or_uri=motor_client,
        database=config.MONGO_DB_NAME,
        collection_userdata='userdata'
    )

    user_data = {}
    
    result = await data_store.refresh_data(
        data_type='user',
        data_id=12345678,
        local_data=user_data
    )

    assert result is None
    assert user_data == {
        'my_key': 'value of my key'
    }


async def test_drop_data(motor_client: AsyncIOMotorClient):

    data_store = MongoDBDataStore(
        client_or_uri=motor_client,
        database=config.MONGO_DB_NAME,
        collection_userdata='userdata'
    )

    drop_result = await data_store.drop_data(
        data_type='user',
        data_id=12345678
    )

    assert drop_result is None

    data_found = await data_store.get_data(
        data_type='user',
        data_id=12345678
    )

    assert isinstance(data_found, dict)
    assert 12345678 not in data_found


async def test_update_conversation(motor_client: AsyncIOMotorClient):

    data_store = MongoDBDataStore(
        client_or_uri=motor_client,
        database=config.MONGO_DB_NAME,
        collection_conversationsdata='conversations'
    )

    result = await data_store.update_conversation(
        name='chatconv',
        key=(12345678, 12345678),
        new_state={
            'ping': 'pong'
        }
    )

    assert result is None


async def test_get_conversations(motor_client: AsyncIOMotorClient):

    data_store = MongoDBDataStore(
        client_or_uri=motor_client,
        database=config.MONGO_DB_NAME,
        collection_conversationsdata='conversations'
    )

    result = await data_store.get_conversations(
        name='chatconv'
    )

    assert isinstance(result, dict)
    assert len(result) == 1
    assert 'chatconv' in result
    assert result['chatconv'][(12345678, 12345678)] == {
        'ping': 'pong'
    }


async def test_build_persistence_input(motor_client: AsyncIOMotorClient):

    data_store = MongoDBDataStore(
        client_or_uri=motor_client,
        database=config.MONGO_DB_NAME
    )

    result = data_store.build_persistence_input()

    assert isinstance(result, PersistenceInput)


async def test_flush_do_not_close_client(motor_client: AsyncIOMotorClient):

    data_store = MongoDBDataStore(
        client_or_uri=motor_client,
        database=config.MONGO_DB_NAME
    )

    result = await data_store.flush()

    assert result is None

    await motor_client.admin.command("ping")


async def test_flush_close_client():

    data_store = MongoDBDataStore(
        client_or_uri=config.MONGO_DB_URI,
        database=config.MONGO_DB_NAME
    )

    result = await data_store.flush()

    assert result is None

    with pytest.raises(pymongo.errors.InvalidOperation):
        await data_store._client.admin.command('ping')

