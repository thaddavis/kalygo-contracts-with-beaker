from multiprocessing.dummy import Array
from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,
)
from algosdk.abi import Contract


def fund_minimum_balance(
    atc: AtomicTransactionComposer,
    algod_client: AlgodClient,
    params,
    sender: str,
    sender_private_key: str,
    receiver: str,
    amount: int,  # need to send 100,000 mAlgos for each ASA the contract opts into
):
    print(
        "Fund Minimum Balance...",
        "sender",
        sender,
        "receiver",
        receiver,
    )

    signer = AccountTransactionSigner(sender_private_key)

    note = "for optin to stablecoin ASA".encode()
    ptxn = transaction.PaymentTxn(sender, params, receiver, amount, None, note)
    tws = TransactionWithSigner(ptxn, signer)
    atc.add_transaction(tws)
    atc.execute(algod_client, 2)
