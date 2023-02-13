from beaker.application import Application, get_method_spec
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
        app_id=1183,
        client=Algod().getClient(),
        app=escrowContract,
        signer=signer,
    )

    print("updating")

    update_spec = get_method_spec(EscrowContract.update)

    print("update_spec", update_spec)

    app_client.update(
        sender=deployer_address,
        signer=signer,
        # args=[
        #     buyer_address,
        #     seller_address,
        #     100000,
        #     100000,
        #     200000,
        #     int(get_current_timestamp()),
        #     int(get_future_timestamp_in_secs(60)),
        #     int(get_future_timestamp_in_secs(120)),
        #     int(get_future_timestamp_in_secs(180)),
        #     int(get_future_timestamp_in_secs(240)),
        #     int(get_future_timestamp_in_secs(300)),
        #     12,
        # ],
        global_buyer=buyer_address,
        global_seller=seller_address,
        global_escrow_payment_1=200000,
        global_escrow_payment_2=200000,
        global_total_price=400000,
        # global_buyer: abi.Address,
        # global_seller: abi.Address,
        # global_escrow_payment_1: abi.Uint64,
        # global_escrow_payment_2: abi.Uint64,
        # global_total_price: abi.Uint64,
        # global_inspection_start_date: abi.Uint64,
        # global_inspection_end_date: abi.Uint64,
        # global_inspection_extension_date: abi.Uint64,
        # global_moving_date: abi.Uint64,
        # global_closing_date: abi.Uint64,
        # global_free_funds_date: abi.Uint64,
        # global_asa_id: abi.Uint64,
    )

    print(f"updated app_id: {app_client.app_id}")
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
