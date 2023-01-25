from multiprocessing.dummy import Array
from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,
)
from algosdk.abi import Contract


def optin_contract_to_ASA(
    app_id: int,
    atc: AtomicTransactionComposer,
    abi: Contract,
    algod_client: AlgodClient,
    params,
    sender: str,
    sender_private_key: str,
    receiver: str,
    ASA_id: int,
):
    print(
        "Opting-in Contract to ASA...",
        "ASA id:",
        ASA_id,
        "app_id",
        app_id,
        "sender",
        sender,
        "receiver",
        receiver,
    )

    signer = AccountTransactionSigner(sender_private_key)

    atc.add_method_call(
        app_id,
        abi.get_method_by_name("optin_to_ASA"),
        sender,
        params,
        signer,
        method_args=[],
        foreign_assets=[ASA_id],
    )

    res = atc.execute(algod_client, 2)

    # print("___ ___ ___", res.tx_ids[0])
    # tx_id = res.tx_ids[0]
    # wait for confirmation
    # try:
    #     print("wait for confirmation...")
    #     confirmed_txn = transaction.wait_for_confirmation(algod_client, tx_id, 4)
    #     print("Successfully Opted-in Contract to ASA")
    # except Exception as err:
    #     print("ERROR", err)
