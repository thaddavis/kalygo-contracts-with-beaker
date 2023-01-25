from algosdk import account
from algosdk.future import transaction
from modules.helpers.utils import (
    wait_for_confirmation,
    get_private_key_from_mnemonic,
)
import config.escrow as config
from modules.clients.AlgodClient import Algod
from modules.helpers.get_txn_params import get_txn_params
from beaker.application import Application
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from beaker.client.application_client import ApplicationClient


def delete_contract(
    EscrowContractClass,
    app_id: int,
    creator_mnemonic: str = config.account_a_mnemonic,
):
    deployer_private_key = get_private_key_from_mnemonic(creator_mnemonic)
    signer = AccountTransactionSigner(deployer_private_key)
    escrowContract = EscrowContractClass()
    app_client = ApplicationClient(
        client=Algod().getClient(),
        app=escrowContract,
        app_id=app_id,
        signer=signer,
    )
    print("Deleting application...")
    tx_id = app_client.delete()
    # await confirmation
    wait_for_confirmation(Algod.getClient(), tx_id)
    # display results
    # transaction_response = Algod.getClient().pending_transaction_info(tx_id)
    # print(transaction_response)
    print("Successfully deleted contract")
