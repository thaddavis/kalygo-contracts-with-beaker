from modules.helpers.utils import get_private_key_from_mnemonic
import config.escrow as config
from algosdk import account, constants, logic
from algosdk.future import transaction
from algosdk.error import AlgodHTTPError
from algosdk.v2client import algod
from algosdk.encoding import encode_address
from modules.clients.AlgodClient import Algod

sender_private_key = get_private_key_from_mnemonic(config.account_c_mnemonic)
receiver_private_key = get_private_key_from_mnemonic(config.account_a_mnemonic)
stablecoin_ASA: int = config.stablecoin_ASA


def main():
    asset_info = Algod.getClient().asset_info(stablecoin_ASA)
    sender_address = account.address_from_private_key(sender_private_key)
    receiver_address = account.address_from_private_key(receiver_private_key)

    print("")
    print("sender_address", sender_address)
    print("receiver_address", receiver_address)
    print("ASA creator", asset_info["params"]["creator"])
    print("")

    params = Algod.getClient().suggested_params()
    params.flat_fee = True
    params.fee = constants.MIN_TXN_FEE

    sender = sender_address
    receiver = receiver_address

    unsigned_txn_A = transaction.AssetTransferTxn(
        sender,  # sender (str): address of the sender
        params,  # sp (SuggestedParams): suggested params from algod
        receiver,  # receiver (str): address of the receiver
        10000000,  # amt (int): amount of asset base units to send
        stablecoin_ASA,  # index (int): index of the asset
    )

    print("signing opt-in txn")
    signed_txn_A = unsigned_txn_A.sign(sender_private_key)

    # submit transaction
    print("sending txn")
    tx_id = Algod.getClient().send_transactions([signed_txn_A])

    # wait for confirmation
    try:
        print("wait for confirmation...")
        confirmed_txn = transaction.wait_for_confirmation(Algod.getClient(), tx_id, 4)

        print("Asset amount transferred successfully")
        print("Result confirmed in round: {}".format(confirmed_txn["confirmed-round"]))
    except Exception as err:
        print("ERROR", err)
