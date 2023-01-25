import pytest
import json
from modules.actions.escrow.deploy_new import deploy_new
from modules.actions.escrow.delete_contract import delete_contract

from algosdk import logic
from contracts.escrow.contract import EscrowContract
import config.escrow as config
from modules.helpers.utils import (
    format_app_global_state,
    get_private_key_from_mnemonic,
)
from modules.helpers.time import get_current_timestamp, get_future_timestamp_in_secs
from modules.clients.AlgodClient import Algod

from algosdk.abi import Contract
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
)


@pytest.fixture(scope="module")
def escrow_contract():
    print()
    print()
    print("deploying escrow contract...")

    deployed_contract = deploy_new(
        EscrowContract,
        config.account_a_address,  # deployer_address
        config.account_a_mnemonic,
        config.account_b_address,  # buyer_address
        config.account_c_address,
        config.escrow_payment_1,  # escrow_payment_1
        config.escrow_payment_2,
        config.total_price,  # total_price
        config.stablecoin_ASA,
        int(get_current_timestamp()),  # Inspection Period Start Date
        int(get_future_timestamp_in_secs(60)),  # Inspection Period End Date
        int(get_future_timestamp_in_secs(90)),  # Inspection Period Extension Date
        int(get_future_timestamp_in_secs(120)),  # Moving Date
        int(get_future_timestamp_in_secs(240)),  # Closing Date
        int(get_future_timestamp_in_secs(360)),  # Free Funds Date
    )
    yield deployed_contract["app_id"]
    print()
    print("tear down in fixture", deployed_contract["app_id"])
    delete_contract(
        EscrowContract,
        deployed_contract["app_id"],
        config.account_a_mnemonic,
    )


def test_buyer_arbitration_flag(escrow_contract):
    app_id = escrow_contract
    app_info = Algod.getClient().application_info(app_id)
    app_info_formatted = format_app_global_state(app_info["params"]["global-state"])

    sender_address = config.account_b_address
    sender_mnemonic = config.account_b_mnemonic
    sender_private_key = get_private_key_from_mnemonic(sender_mnemonic)
    signer = AccountTransactionSigner(sender_private_key)
    algod_client = Algod().getClient()

    res = algod_client.account_info(sender_address)
    print("Account Balance:", res["amount"])

    with open("build/abi.json") as f:
        js = f.read()

    c = Contract.from_json(js)

    atc = AtomicTransactionComposer()
    sp = algod_client.suggested_params()

    print("app_id:", app_id)
    contract_address = logic.get_application_address(app_id)
    print("address for app_id", contract_address)

    app_info = Algod.getClient().application_info(app_id)
    app_info_formatted = format_app_global_state(app_info["params"]["global-state"])
    # print(json.dumps(app_info_formatted, indent=4))

    assert app_info_formatted["global_buyer_arbitration_flag"] == 0

    atc.add_method_call(
        app_id,
        c.get_method_by_name("buyer_set_arbitration"),
        sender_address,
        sp,
        signer,
        method_args=[],
    )

    # Execute Txn
    atc.execute(algod_client, 2)

    app_info = Algod.getClient().application_info(app_id)
    app_info_formatted = format_app_global_state(app_info["params"]["global-state"])
    # print(json.dumps(app_info_formatted, indent=4))

    assert app_info_formatted["global_buyer_arbitration_flag"] == 1
