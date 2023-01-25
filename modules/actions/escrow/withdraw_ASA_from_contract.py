from algosdk import logic
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,
)
from algosdk.abi import Contract


def withdraw_ASA_from_contract(
    app_id: int,
    atc: AtomicTransactionComposer,
    abi: Contract,
    algod_client: AlgodClient,
    params,
    sender: str,
    sender_private_key: str,
    ASA_id: int,
):
    print("Withdraw ASA from contract")
    app_address = logic.get_application_address(app_id)
    print("app_id", app_id, "app_address", app_address)

    signer = AccountTransactionSigner(sender_private_key)

    atc.add_method_call(
        app_id,
        abi.get_method_by_name("withdraw_ASA"),
        sender,
        params,
        signer,
        method_args=[],
        foreign_assets=[ASA_id],
    )

    res = atc.execute(algod_client, 2)

    # app_args = ["withdraw_ASA"]
    # unsigned_txn = transaction.ApplicationNoOpTxn(
    #     sender, params, app_id, app_args, foreign_assets=[ASA_id]
    # )

    # signed_txn = unsigned_txn.sign(sender_private_key)
    # tx_id = algod_client.send_transactions([signed_txn])

    # # wait for confirmation
    # print("wait for confirmation...")
    # transaction.wait_for_confirmation(algod_client, tx_id, 4)
    # print("Successfully withdrew ASA from contract")
