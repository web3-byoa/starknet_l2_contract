import pytest
import asyncio
from starkware.starknet.testing.starknet import Starknet
from utils.Signer import Signer

# Arbitrary fake private key
signer = Signer(5858585858585858)
# ethereum.eth
L1_ADDRESS = 0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae

# Enables modules.
@pytest.fixture(scope='module')
def event_loop():
    return asyncio.new_event_loop()

# Reusable to save testing time.
@pytest.fixture(scope='module')
async def contract_factory():
    starknet = await Starknet.empty()
    contract = await starknet.deploy("./contract.cairo")
    return starknet, contract

@pytest.mark.asyncio
async def test_contract(contract_factory):
    starknet, contract = contract_factory

    add_app_id = signer.build_transaction(
        
    )