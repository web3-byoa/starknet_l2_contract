# Mallows - L2 BYOA Storage


%lang starknet
%builtins pedersen range_check ecdsa

from starkware.starknet.common.syscalls import get_caller_address

from starkware.cairo.common.cairo_builtins import (
    HashBuiltin, SignatureBuiltin)
from starkware.cairo.common.hash import (
    hash2
)
from starkware.cairo.common.hash_chain import (
    hash_chain
)
from starkware.cairo.common.signature import (
    verify_ecdsa_signature)
from starkware.starknet.common.syscalls import get_tx_signature
from starkware.cairo.common.dict_access import DictAccess
from starkware.cairo.common.math import (
    assert_lt
)

# For a given user, returns the value of the app at that index
@storage_var
func app_array(user: felt, index: felt) -> (app_id : felt):
end

# For a given user, returns the number of installed apps that they have
@storage_var
func app_len(user: felt) -> (len : felt):
end

# How many params are there for a specific app for the user
@storage_var
func app_param_count(user: felt, app_index: felt) -> (param_count : felt):
end

# For a given user, and an app index, what is the param value
@storage_var
func app_param_value_array(user: felt, app_index: felt, param_index: felt) -> (res : (felt, felt)):
end

# Public method for reading the number of apps the user account has.
@view
func get_app_len{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
        range_check_ptr}(user : felt) -> (res : felt):
    let (res) = app_len.read(user=user)
    return (res)
end

# Public method for reading the app_id at the specified index for the user account.
@view
func get_app_array{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
        range_check_ptr}(user : felt, index: felt) -> (res : felt):
    let (res) = app_array.read(user=user,index=index)
    return (res)
end

# Public method to get the number of params for the users app at the specified index
@view
func get_app_param_count{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
        range_check_ptr}(user : felt, app_index : felt) -> (res : felt):
    let (res) = app_param_count.read(user=user, app_index=app_index)
    return (res)
end

# Public method to get the tuple for the param of a given app by index.
@view
func get_app_param_value_array{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
        range_check_ptr}(user : felt, app_index : felt, param_index : felt) -> (res : (felt, felt)):
    let (stored_tuple) = app_param_value_array.read(user=user, app_index=app_index, param_index=param_index)
    return ((stored_tuple[0], stored_tuple[1]))
end

# Adds an App ID to their profile
@external
func add_app_id{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
        range_check_ptr, ecdsa_ptr : SignatureBuiltin*}(
    app_id : felt):

    let (user) = get_caller_address()
    # Read the current account length into res
    let (res) = app_len.read(user=user)

    # Update the app_len and app_ids
    app_len.write(user, res + 1)
    app_array.write(user, res, app_id)
    # Initialize the param count to 0 (for completeness)
    app_param_count.write(user, res+1,0)

    return ()
end

@external
func set_param_at_index{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
        range_check_ptr, ecdsa_ptr : SignatureBuiltin*}(
        user : felt, 
        app_index : felt, 
        param_index: felt, 
        param_id: felt,
        param_value : felt
    ):
    let (user) = get_caller_address()
    
    # Read the current account length into res
    let (res) = app_len.read(user=user)
    # Assert that this is a valid index
    assert_lt(app_index, res)

    # Assert that this param_index is available
    let (res_pc) = app_param_count.read(user=user, app_index=app_index)
    assert_lt(param_index, res_pc)

    # Update the value at that index
    app_param_value_array.write(user, app_index, param_index, (param_id, param_value))

    return ()
end

@external
func add_param{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*,
        range_check_ptr, ecdsa_ptr : SignatureBuiltin*}(
        user : felt, 
        app_index : felt,  
        param_id : felt,
        param_value : felt
    ):
    let (user) = get_caller_address()


    # Read the current account length into res
    let (res) = app_len.read(user=user)
    # Assert that this is a valid index
    assert_lt(app_index, res)

    # Get the last param count
    let (res_pc) = app_param_count.read(user=user, app_index=app_index)
    
    # Update the values: increment the param counter, and then add the value
    app_param_count.write(user, app_index, res_pc+1)
    app_param_value_array.write(user, app_index, res_pc, (param_id,param_value))

    return ()
end

