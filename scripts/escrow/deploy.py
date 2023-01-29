from beaker.application import Application
from beaker.client.application_client import ApplicationClient
from modules.clients.AlgodClient import Algod
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from modules.helpers.time import get_current_timestamp, get_future_timestamp_in_secs
import json

from modules.helpers.utils import (
    get_private_key_from_mnemonic,
)

from contracts.escrow.contract import EscrowContract
import config.escrow as config


def main():

    deployer_address = config.account_a_address
    deployer_mnemonic = config.account_a_mnemonic

    # buyer_address = config.account_b_address
    # seller_address = config.account_c_address
    buyer_address = config.account_a_address
    seller_address = config.account_a_address

    deployer_private_key = get_private_key_from_mnemonic(deployer_mnemonic)
    signer = AccountTransactionSigner(deployer_private_key)

    escrowContract = EscrowContract()

    app_client = ApplicationClient(
        client=Algod().getClient(),
        app=escrowContract,
        signer=signer,
    )

    print("deploying")

    app_client.create(
        global_creator=deployer_address,
        global_buyer=buyer_address,
        global_seller=seller_address,
        global_escrow_payment_1=100000,
        global_escrow_payment_2=100000,
        global_total_price=200000,
        global_inspection_start_date=int(get_current_timestamp()),
        global_inspection_end_date=int(get_future_timestamp_in_secs(60)),
        global_inspection_extension_date=int(get_future_timestamp_in_secs(120)),
        global_moving_date=int(get_future_timestamp_in_secs(180)),
        global_closing_date=int(get_future_timestamp_in_secs(240)),
        global_free_funds_date=int(get_future_timestamp_in_secs(300)),
        global_asa_id=12,
        note="cashBuy__v1.0.0",
    )

    print(f"deployed app_id: {app_client.app_id}")
    print(
        f"Current app state: {json.dumps(app_client.get_application_state(), indent=4)}"
    )

    # json.dumps(confirmed_txn, indent=4)))
    # app_client.call(escrowContract.increment)
    # print(f"Current app state: {app_client.get_application_state()}")
    # print("deleting...")
    # app_client.delete(deployer_address, signer)

    print("DONE")


if __name__ == "__main__":
    main()
