from beaker.application import Application
from beaker.client.application_client import ApplicationClient
from beaker import sandbox
from algosdk.atomic_transaction_composer import AccountTransactionSigner
import json

from modules.helpers.utils import (
    get_private_key_from_mnemonic,
)

from contracts.escrow.contract import EscrowContract
import config.escrow as config


def main():

    print("compiling Escrow contract")

    # deployer_mnemonic = config.account_a_mnemonic
    # deployer_private_key = get_private_key_from_mnemonic(deployer_mnemonic)

    # signer = AccountTransactionSigner(deployer_private_key)

    escrowContract = EscrowContract()
    # app_client = ApplicationClient(
    #     client=sandbox.get_algod_client(), app=escrowContract, signer=signer
    # )

    # print("escrowContract", escrowContract)

    escrowContract.dump("./build")

    # app_client.create(global_buyer_pullout_flag=0)
    # print(f"Current app state: {app_client.get_application_state()}")
    # app_client.call(escrowContract.increment)
    # print(f"Current app state: {app_client.get_application_state()}")

    with open("./build/approval.teal", "w") as h:
        h.write(escrowContract.approval_program)  # type: ignore
    print("wrote approval program to build dir")

    with open("./build/clear.teal", "w") as h:
        h.write(escrowContract.clear_program)  # type: ignore
    print("wrote clear program to build dir")

    with open("./build/abi.json", "w") as h:
        h.write(json.dumps(escrowContract.contract.dictify()))
    print("wrote ABI program to build dir")

    # print(json.dumps(counterApp.contract.dictify()))


if __name__ == "__main__":
    main()
