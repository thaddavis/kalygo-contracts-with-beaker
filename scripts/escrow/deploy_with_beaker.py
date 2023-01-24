from beaker.application import Application
from beaker.client.application_client import ApplicationClient
from modules.clients.AlgodClient import Algod
from algosdk.atomic_transaction_composer import AccountTransactionSigner
import json

from modules.helpers.utils import (
    get_private_key_from_mnemonic,
)

from contracts.escrow.contract import EscrowContract
import config.escrow as config


def main():

    deployer_mnemonic = config.account_a_mnemonic
    deployer_private_key = get_private_key_from_mnemonic(deployer_mnemonic)
    signer = AccountTransactionSigner(deployer_private_key)

    escrowContract = EscrowContract()
    app_client = ApplicationClient(
        client=Algod().getClient(config.algod_token, config.algod_url),
        app=escrowContract,
        signer=signer,
    )

    print("deploying")

    app_client.create(global_buyer_pullout_flag=0)

    print(f"Current app state: {app_client.get_application_state()}")
    app_client.call(escrowContract.increment)
    print(f"Current app state: {app_client.get_application_state()}")

    print("DONE")


# if __name__ == "__main__":
#     main()
