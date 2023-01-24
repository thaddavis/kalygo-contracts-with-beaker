from modules.clients.AlgodClient import Algod
from algosdk.future.transaction import PaymentTxn
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,
)
import json

from modules.helpers.utils import (
    get_private_key_from_mnemonic,
)

import config.escrow as config


def main():

    app_id = 54
    sender_address = config.account_a_address
    sender_mnemonic = config.account_a_mnemonic
    recv_address = config.account_b_address
    sender_private_key = get_private_key_from_mnemonic(sender_mnemonic)
    signer = AccountTransactionSigner(sender_private_key)
    algod_client = Algod().getClient()
    res = algod_client.account_info(sender_address)
    print("Account Balance:", res["amount"])
    # Instantiate the transaction composer
    atc = AtomicTransactionComposer()
    # Get suggested params from the client
    sp = algod_client.suggested_params()
    # Create a transaction
    ptxn = PaymentTxn(sender_address, sp, recv_address, 1000)
    # Construct TransactionWithSigner
    tws = TransactionWithSigner(ptxn, signer)
    # Pass TransactionWithSigner to ATC
    atc.add_transaction(tws)
    # Execute Txn
    atc.execute(algod_client, 2)

    res = algod_client.account_info(sender_address)
    print("Account Balance:", res["amount"])

    print("DONE")


if __name__ == "__main__":
    main()
