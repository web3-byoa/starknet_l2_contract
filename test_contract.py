import os
import pytest
import asyncio
from starkware.starknet.testing.starknet import Starknet
from starkware.starkware_utils.error_handling import StarkException

# `str_to_felt` taken from Openzeppelin Cairo Contract Helpers
def str_to_felt(text):
    b_text = bytes(text, 'ascii')
    return int.from_bytes(b_text, "big")


CONTRACT_FILE = os.path.join(
    os.path.dirname(__file__), "contract.cairo")

ADDRESS = 0x123456
ADDRESS_2 = 0x567890


# Enables modules.
@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

# Reusable to save testing time.
@pytest.fixture(scope='module')
async def contract_factory():
    starknet = await Starknet.empty()
    # Deploy the contract.
    contract = await starknet.deploy(
        source=CONTRACT_FILE,
    )
    return starknet, contract

@pytest.mark.asyncio
async def test_contract(contract_factory):
    starknet, contract = contract_factory

    # User app length 0 by default
    assert (await contract.get_app_len(user=ADDRESS).call()).result.res == 0

    # When app length 0, throw exception for finding to find an app that doesn't exist
    with pytest.raises(StarkException):
        await (contract.get_app_array(user=ADDRESS, index=10).call())

    with pytest.raises(StarkException):
        await (contract.get_app_array(user=ADDRESS, index=-1).call())

    # Add apps to user 1 and check they are added and installed
    await contract.add_app_id(app_id=123).invoke(caller_address=ADDRESS)
    assert (await contract.get_app_len(user=ADDRESS).call()).result.res == 1
    await contract.add_app_id(app_id=456).invoke(caller_address=ADDRESS)
    assert (await contract.get_app_len(user=ADDRESS).call()).result.res == 2
    assert (await contract.get_app_installation(user=ADDRESS, index=0).call()).result.res == 1
    assert (await contract.get_app_installation(user=ADDRESS, index=1).call()).result.res == 1

    with pytest.raises(StarkException):
        await contract.get_app_installation(user=ADDRESS, index=2).call()
    with pytest.raises(StarkException):
        await contract.get_app_installation(user=ADDRESS, index=-1).call()

    # Uninstall the second app
    await contract.toggle_install_app_by_index(index=1, installed=0).invoke(caller_address=ADDRESS)
    assert (await contract.get_app_installation(user=ADDRESS, index=1).call()).result.res == 0

    # Reinstall the second app
    await contract.toggle_install_app_by_index(index=1, installed=1).invoke(caller_address=ADDRESS)
    assert (await contract.get_app_installation(user=ADDRESS, index=1).call()).result.res == 1

    # Attempt to out of bounds install
    with pytest.raises(StarkException):
        await contract.toggle_install_app_by_index(index=1, installed=2).invoke(caller_address=ADDRESS)
    with pytest.raises(StarkException):
        await contract.toggle_install_app_by_index(index=1, installed=-1).invoke(caller_address=ADDRESS)

    # Get the correct app ids back by index
    assert (await (contract.get_app_array(user=ADDRESS, index=0).call())).result.res == 123
    assert (await (contract.get_app_array(user=ADDRESS, index=1).call())).result.res == 456

    # Check the param counts
    assert (await (contract.get_app_param_count(user=ADDRESS, app_index=0).call())).result.res == 0
    assert (await (contract.get_app_param_count(user=ADDRESS, app_index=1).call())).result.res == 0

    # Add a new param
    await contract.add_param(
        user=ADDRESS,
        app_index=1,
        param_id=str_to_felt("testkey"),
        param_value=str_to_felt("testvalue"),
    ).invoke(caller_address=ADDRESS)

    await contract.add_param(
        user=ADDRESS,
        app_index=1,
        param_id=str_to_felt("testkey2"),
        param_value=str_to_felt("testvalue2"),
    ).invoke(caller_address=ADDRESS)

    # Read the written param data
    assert (await (contract.get_app_param_count(user=ADDRESS, app_index=1).call())).result.res == 2
    assert (await (contract.get_app_param_value_array(user=ADDRESS, app_index=1, param_index=0).call())).result.res == (str_to_felt("testkey"), str_to_felt("testvalue"))
    assert (await (contract.get_app_param_value_array(user=ADDRESS, app_index=1, param_index=1).call())).result.res == (str_to_felt("testkey2"), str_to_felt("testvalue2"))

    # Set a param value again
    await contract.set_param_at_index(
        user=ADDRESS,
        app_index=1,
        param_index=1,
        param_id=str_to_felt("testkey2rewritten"),
        param_value=str_to_felt("testvalue2rewritten"),
    ).invoke(caller_address=ADDRESS)

    assert (await (contract.get_app_param_value_array(user=ADDRESS, app_index=1, param_index=1).call())).result.res == (str_to_felt("testkey2rewritten"), str_to_felt("testvalue2rewritten"))

    # Check that other users do not interact with each others data
    assert (await contract.get_app_len(user=ADDRESS_2).call()).result.res == 0
    await contract.add_app_id(app_id=111).invoke(caller_address=ADDRESS_2)
    assert (await contract.get_app_len(user=ADDRESS_2).call()).result.res == 1
    assert (await contract.get_app_len(user=ADDRESS).call()).result.res == 2

    # Check out of bounds for param setting
    with pytest.raises(StarkException):
        await contract.set_param_at_index(
            user=ADDRESS,
            app_index=1,
            param_index=10,
            param_id=str_to_felt("testkey2rewritten"),
            param_value=str_to_felt("testvalue2rewritten"),
        ).invoke(caller_address=ADDRESS)

    with pytest.raises(StarkException):
        await contract.set_param_at_index(
            user=ADDRESS,
            app_index=10,
            param_index=0,
            param_id=str_to_felt("testkey2rewritten"),
            param_value=str_to_felt("testvalue2rewritten"),
        ).invoke(caller_address=ADDRESS)

    with pytest.raises(StarkException):
        await contract.set_param_at_index(
            user=ADDRESS,
            app_index=-1,
            param_index=0,
            param_id=str_to_felt("testkey2rewritten"),
            param_value=str_to_felt("testvalue2rewritten"),
        ).invoke(caller_address=ADDRESS)

    # Check out of bounds for param adding
    with pytest.raises(StarkException):
        await contract.add_param(
            user=ADDRESS,
            app_index=-1,
            param_id=str_to_felt("testkey2"),
            param_value=str_to_felt("testvalue2"),
        ).invoke(caller_address=ADDRESS)

