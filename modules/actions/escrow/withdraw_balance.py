from modules.helpers.utils import get_private_key_from_mnemonic
from algosdk import logic
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,
)
from algosdk.abi import Contract


def withdraw_balance(
    app_id: int,
    atc: AtomicTransactionComposer,
    ABI: Contract,
    algod_client: AlgodClient,
    params,
    sender: str,
    sender_private_key: str,
):
    print("Withdrawing balance from contract")
    app_address = logic.get_application_address(app_id)
    print("app_id", app_id, "app_address", app_address, "sender", sender)

    signer = AccountTransactionSigner(sender_private_key)

    atc.add_method_call(
        app_id,
        ABI.get_method_by_name("withdraw_balance"),
        sender,
        params,
        signer,
        method_args=[],
    )

    atc.execute(algod_client, 2)

    # app_args = ["withdraw_balance"]
    # unsigned_txn = transaction.ApplicationNoOpTxn(sender, params, app_id, app_args)

    # signed_txn = unsigned_txn.sign(sender_private_key)
    # tx_id = algod_client.send_transactions([signed_txn])

    # # wait for confirmation
    # print("wait for confirmation...")
    # transaction.wait_for_confirmation(algod_client, tx_id, 4)
    # # print("Transaction information: {}".format(
    # #     json.dumps(confirmed_txn, indent=4)))
    # print("Successfully withdrew balance from contract")
    # # print("Result confirmed in round: {}".format(confirmed_txn["confirmed-round"]))
