from modules.clients.AlgodClient import Algod
from algosdk.abi import Contract
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
)
from algosdk import logic
import json
from modules.helpers.utils import (
    get_private_key_from_mnemonic,
    format_app_global_state,
)
import config.escrow as config


def main():

    app_id = 65
    sender_address = config.account_a_address
    sender_mnemonic = config.account_a_mnemonic
    sender_private_key = get_private_key_from_mnemonic(sender_mnemonic)
    signer = AccountTransactionSigner(sender_private_key)
    algod_client = Algod().getClient()

    res = algod_client.account_info(sender_address)
    print("Account Balance:", res["amount"])

    with open("build/abi.json") as f:
        js = f.read()

    c = Contract.from_json(js)

    # Instantiate the transaction composer
    atc = AtomicTransactionComposer()
    # Get suggested params from the client
    sp = algod_client.suggested_params()

    print("app_id:", app_id)
    contract_address = logic.get_application_address(app_id)
    print("address for app_id", contract_address)

    app_info = Algod.getClient().application_info(app_id)
    app_info_formatted = format_app_global_state(app_info["params"]["global-state"])
    print(json.dumps(app_info_formatted, indent=4))

    atc.add_method_call(
        app_id,
        c.get_method_by_name("increment"),
        sender_address,
        sp,
        signer,
        method_args=[],
    )

    # Execute Txn
    atc.execute(algod_client, 2)

    app_info = Algod.getClient().application_info(app_id)
    app_info_formatted = format_app_global_state(app_info["params"]["global-state"])
    print(json.dumps(app_info_formatted, indent=4))

    res = algod_client.account_info(sender_address)
    print("Account Balance:", res["amount"])

    print("DONE")


if __name__ == "__main__":
    main()
