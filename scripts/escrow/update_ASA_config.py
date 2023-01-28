from algosdk.v2client import indexer
import config.escrow as config
from modules.clients.AlgodClient import Algod
from algosdk.future.transaction import AssetConfigTxn
from modules.clients.IndexerClient import Indexer
import json
from modules.helpers.utils import (
    get_private_key_from_mnemonic,
    format_app_global_state,
    wait_for_confirmation,
)

stablecoin_ASA: int = config.stablecoin_ASA


def main():

    print("")
    print("update ASA config")

    manager_address = config.account_c_address
    manager_mnemonic = config.account_c_mnemonic
    manager_private_key = get_private_key_from_mnemonic(manager_mnemonic)

    custom_clawback_address = config.account_a_address
    asset_id = config.stablecoin_ASA

    algod_client = Algod.getClient()

    asset_info = Algod.getClient().asset_info(stablecoin_ASA)
    print("asset info: {}".format(json.dumps(asset_info, indent=4)))

    params = algod_client.suggested_params()

    txn = AssetConfigTxn(
        sender=manager_address,
        sp=params,
        index=asset_id,
        manager=manager_address,
        reserve=manager_address,
        freeze=manager_address,
        clawback=custom_clawback_address,
    )

    # sign by the current manager
    stxn = txn.sign(manager_private_key)

    # try:
    #     txid = algod_client.send_transaction(stxn)
    #     print("Signed transaction with txID: {}".format(txid))
    #     # Wait for the transaction to be confirmed
    #     confirmed_txn = wait_for_confirmation(algod_client, txid)
    #     print("TXID: ", txid)
    #     print("Result confirmed in round: {}".format(confirmed_txn["confirmed-round"]))
    # except Exception as err:
    #     print(err)
