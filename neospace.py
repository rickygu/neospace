from boa.interop.Neo.Runtime import CheckWitness, GetTime
from boa.interop.Neo.Storage import GetContext, Put, Delete, Get
from boa.builtins import concat


def is_owner(space_id):
    """
    Verify that the space is owned by the requesting user.
    """
    print('Am I the space owner?')
    space_owner = Get(GetContext(), space_id)
    is_space_owner = CheckWitness(space_owner)
    if not is_space_owner:
        print('Not the space owner!')
    return is_space_owner
    return True

# Main Operation


def Main(operation, args):
    """
    Main definition for the smart contracts
    :param operation: the operation to be performed
    :type operation: str
    :param args: list of arguments.
        args[0] is always sender script hash
        args[1] is always space_id
        args[2] (optional) is always another script hash
        args[3] (optional) unix timestamp for lease expiry

    :param type: str
    :return:
        byterarray: The result of the operation
    """
    # Am I who I say I am?
    user_hash = args[0]
    authorized = CheckWitness(user_hash)
    if not authorized:
        print("Not Authorized to perform action")
        return False
    print("Authorized")
    # Common definitions
    space_id = args[1]
    user_lease = concat(user_hash, space_id)
    lease_expiry = GetTime() + 31556926 #1 year from today

    if len(args) == 4:
        print('Lease for another user with expiry date')
        lease_expiry = args[3]
        requested_user = args[2]
        requested_lease = concat(requested_user, space_id)
    else:
        print('Lease for me')
        requested_user = user_hash
        requested_lease = user_lease

    if operation != None:
        if operation == 'AddSpace':
            print('AddSpace')
            space_exists = Get(GetContext(), space_id)
            if not space_exists:
                Put(GetContext(), space_id, user_hash)
                print("Space Added")
                return True

        if operation == 'LeaseSpace':
            print('LeaseSpace')
            if is_owner(space_id):
                # Lease the space
                Put(GetContext(), requested_lease, lease_expiry)
                print("Space Leased")
                return True

        if operation == 'TransferLease':
            lease_owner = Get(GetContext(), user_lease)
            if lease_owner:
                print("Lease exists")
                is_lease_owner = CheckWitness(lease_owner)
                # Am I the lease owner?
                if is_lease_owner:
                    print("User is Lease Owner")
                    # Transfer Lease
                    new_user_hash = args[2]
                    new_lease = concat(new_user_hash, space_id)
                    expiry = Get(GetContext(), user_lease)
                    Delete(GetContext(), user_lease)
                    Put(GetContext(), new_lease, expiry)
                    print("Lease Transfered")
                    return True

        if operation == 'RemoveLease':
           # Am I the space owner?
            if is_owner(space_id):
                # Delete the lease
                user_hash_to_del = args[2]
                lease_to_del = concat(user_hash_to_del, space_id)
                Delete(GetContext(), lease_to_del)
                return True

        if operation == 'GetLeaseExpiry':
            print("Get Lease Expiry")
            expiry = Get(GetContext(), requested_lease)
            if expiry:
                return expiry
            else:
                print('Lease does not exist')
                return False

        return False
