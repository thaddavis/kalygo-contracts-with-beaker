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
        glbl_creator=deployer_address,
        glbl_buyer=buyer_address,
        glbl_seller=seller_address,
        glbl_escrow_payment_1=100000,
        glbl_escrow_payment_2=100000,
        glbl_total_price=200000,
        glbl_inspection_start_date=int(get_current_timestamp()),
        glbl_inspection_end_date=int(get_future_timestamp_in_secs(60)),
        glbl_inspection_extension_date=int(get_future_timestamp_in_secs(120)),
        glbl_moving_date=int(get_future_timestamp_in_secs(180)),
        glbl_closing_date=int(get_future_timestamp_in_secs(240)),
        glbl_free_funds_date=int(get_future_timestamp_in_secs(300)),
        glbl_asa_id=12,
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
