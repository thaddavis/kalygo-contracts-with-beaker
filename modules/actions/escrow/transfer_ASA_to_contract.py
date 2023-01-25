from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,
)


def transfer_ASA_to_contract(
    atc: AtomicTransactionComposer,
    algod_client: AlgodClient,
    params,
    sender: str,
    sender_private_key: str,
    app_address: str,
    ASA_id: int,
    ASA_amount: int,
):
    print(
        "Transferring ASA from sender to contract",
        "ASA_id",
        ASA_id,
        "sender",
        sender,
        "app_address",
        app_address,
    )

    asset_info = algod_client.asset_info(ASA_id)
    print("")
    print("sender_address", sender)
    print("receiver_address (contract)", app_address)
    print("ASA creator", asset_info["params"]["creator"])
    print("")
    signer = AccountTransactionSigner(sender_private_key)
    note = "send escrow payment in stablecoin ASA".encode()
    axfer_txn = transaction.AssetTransferTxn(
        sender, params, app_address, ASA_amount, ASA_id, None, None, note
    )
    print(axfer_txn)

    tws = TransactionWithSigner(axfer_txn, signer)
    atc.add_transaction(tws)

    res = atc.execute(algod_client, 4)
    tx_id = res.tx_ids[0]

    # wait for confirmation
    try:
        print("wait for confirmation...")
        confirmed_txn = transaction.wait_for_confirmation(algod_client, tx_id, 4)
        print("Successfully Opted-in Contract to ASA")
    except Exception as err:
        print("ERROR", err)
