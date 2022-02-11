# Mallows / BYOA Layer 2 Configuration Contract

Mallows / BYOA provides a mechanism for storing and running arbitrary code from NFT metadata. The byoa applications are provisioned on L1 Mainnet. This StarkNet contract provides an interface for a user to register one of these byoa applications to their StarkNet Layer 2 account.

## Installation
You must have valid StarkNet contract and cario contract build resources installed on your build machine. You can follow the official documentation from the Cairo Lang website [here](https://www.cairo-lang.org/docs/quickstart.html).

Once your Cairo environment is configured, you can clone this repository and move to the Building instructions.

## Building
```
starknet-compile contract.cairo --output contract_compiled.json --abi contract_abi.json
```

## Testing
Ensure that the `cairo-compile` tool is installed before attempting to run the tests.
```
cairo-compile test.cairo --output test_compiled.json
cairo-run --program=test_compiled.json --print_output --print_info --relocate_prints
```

## Running
```
# Set the desired StarkNet network to deploy to.
export STARKNET_NETWORK=alpha-goerli

# Deploy the contract and note the returned contract address
starknet deploy --contract contract_compiled.json
```

## Interfaces
### `get_app_len(user)`
Return the number of byoa apps that have been registered for a particular user's address.

### `get_app_array(user, index)`
Return the app id at the specified index.  Use `get_app_len` to know the length of the underlying array that you will be indexing into.

### `get_app_param_count(user, index)`
For the app at the given index, return the number of parameters which have been configured for this specific app.

### `get_app_param_value_array(user, app_index, param_index)`
For a given app at `app_index` for user account `user`, return the configured param at `param_index`. Use `get_app_param_count` to return the number of params which have been configured for a particular app.

### `add_app_id(app_id)` 
Authenticated users can add a new app_id to the list of installed apps. This method does not currently check for validity on L1, nor does it prevent double installs.

### `set_param_at_index(app_index, param_id, param_value)`
Authenticated uesrs can set an arbitrary key,value pair for an installed app at `app_index` with key=`param_id` and value=`param_value`.

## Interacting
You can interact directly with the contract using the StarkNet contract tools, such as `starknet` and by running `starknet call`.

### Example for `get_app_len`
```
starknet call \
    --address DEPLOYED_CONTRACT_ADDRESS \
    --abi contract_abi.json \
    --function get_app_len \
    --inputs \
        ACCOUNT_ADDRESS \
    --signature \
        REPLACE_ME \
        REPLACE_ME
```

## Releases
Currently in the beta phase, subject to frequent changes. Below we will list deployed contracts that map to a particular release.

## Contributing
Please submit Pull Requests to start the discussion for improvements and enhancements to this contract. Currently it is maintained by the mallows.xyz team.

