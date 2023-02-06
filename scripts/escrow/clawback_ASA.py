import time
import config.escrow as config
from modules.clients.AlgodClient import Algod
from modules.clients.IndexerClient import Indexer
from algosdk.future import transaction
from modules.helpers.print_account_ASA_holdings import print_account_ASA_holdings
from modules.helpers.utils import get_private_key_from_mnemonic
from modules.helpers.get_txn_params import get_txn_params

# import json


def main():
    # REVOKE ASSET
    # The clawback address `sender` revokes asset units from `revocation_target` and places them with `receiver`

    params = get_txn_params(Algod.getClient())
    sender = "A3326WI7EK3RVOQ4JRZSLY3HO26JCVGT7HGU2RBBFAX3KOVG4XFA4XCTOQ"  # use the `print_ASA_info.py` script to find the clawback address for the asset
    receiver = "YRRGGYPFQYUIKHTYCWL3V7FGMDNNVZ46QJKE6GQQDURQL3NIVUIUFQSXAY"
    revocation_target = "S2TYGLIHGRZZE3RGFXS2KZ5TNFXP32TZSDA3AQPAOAMYFS7R436GMHE2AE"

    sender_private_key = get_private_key_from_mnemonic(
        "device hour foster key rhythm worry able mom student fatal spread forest fresh nominee frown hedgehog medal wood balance hole solar accident place able soap"
    )

    print("PRE-revoke holdings for revocation_target")
    print_account_ASA_holdings(
        Algod.getClient(), Indexer.getClient(), config.stablecoin_ASA, revocation_target
    )

    # Must be signed by the account that is the Asset's clawback address
    txn = transaction.AssetTransferTxn(
        sender=sender,
        sp=params,
        receiver=receiver,
        amt=10000000,
        index=config.stablecoin_ASA,
        revocation_target=revocation_target,
    )
    stxn = txn.sign(sender_private_key)

    try:
        txid = Algod.getClient().send_transaction(stxn)
        print("Signed transaction with txID: {}".format(txid))
        # Wait for the transaction to be confirmed
        confirmed_txn = transaction.wait_for_confirmation(Algod.getClient(), txid, 4)
        print("TXID: ", txid)
        print("Result confirmed in round: {}".format(confirmed_txn["confirmed-round"]))
    except Exception as err:
        print(err)

    print("")
    print("waiting to allow indexer to update new balance amount...")
    time.sleep(3)
    print("")
    print(
        "POST-revoke holdings for revocation_target"
    )  # The balance of revocation target should be reduced by `amount``
    print_account_ASA_holdings(
        Algod.getClient(), Indexer.getClient(), config.stablecoin_ASA, revocation_target
    )
