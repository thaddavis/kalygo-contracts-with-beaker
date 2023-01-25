from algosdk import constants


def get_txn_params(algod_client, fee=constants.MIN_TXN_FEE, fee_multiple=1):
    params = algod_client.suggested_params()
    params.flat_fee = True
    # "* 2" is how to pool fees for optin inner group txn
    params.fee = fee * fee_multiple
    return params
