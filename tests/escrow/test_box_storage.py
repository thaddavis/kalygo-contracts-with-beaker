import pytest
import json
from modules.actions.escrow.deploy_new import deploy_new
from modules.actions.escrow.delete_contract import delete_contract
from modules.actions.escrow.fund_minimum_balance import fund_minimum_balance

from algosdk import logic
import base64
from algosdk.encoding import decode_address
from contracts.escrow.contract import EscrowContract
import config.escrow as config
from modules.helpers.get_txn_params import get_txn_params
from modules.helpers.utils import format_app_global_state, get_private_key_from_mnemonic
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
    # print("tear down in fixture", deployed_contract["app_id"])
    # delete_contract(
    #     EscrowContract,
    #     deployed_contract["app_id"],
    #     config.account_a_mnemonic,
    # )


def test_edit_buyer_box(escrow_contract):
    app_id: int = escrow_contract
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

    print("app_id:", app_id)
    contract_address = logic.get_application_address(app_id)
    print("address for app_id", contract_address)

    # app_info = algod_client.application_info(app_id)
    # app_info_formatted = format_app_global_state(app_info["params"]["global-state"])
    # print(algod_client.application_boxes(app_id))
    # return

    res = algod_client.account_info(contract_address)
    print("contract balance", res["amount"])
    assert res["amount"] == 0

    # --- --- --- --- ---
    atc = AtomicTransactionComposer()
    txn_params = get_txn_params(algod_client)
    fund_minimum_balance(
        atc,
        algod_client,
        txn_params,
        sender_address,
        sender_private_key,
        contract_address,
        112100,  # 100,000 mAlgos min_balance for optin to ASA + 100,000 mAlgos for contract to be able to call other contracts
    )
    # --- --- --- --- ---

    res = algod_client.account_info(contract_address)
    print("contract balance", res["amount"])
    assert res["amount"] == 112100

    # --- --- --- --- ---

    atc_1 = AtomicTransactionComposer()
    sp = algod_client.suggested_params()

    print("app_id:", app_id)
    contract_address = logic.get_application_address(app_id)
    print("address for app_id", contract_address)

    app_info = algod_client.application_info(app_id)
    app_info_formatted = format_app_global_state(app_info["params"]["global-state"])
    print("-=-")
    print(json.dumps(app_info_formatted, indent=4))
    print("-=-")
    # assert app_info_formatted["glbl_buyer_arbitration_flag"] == 0

    atc_1.add_method_call(
        app_id,
        c.get_method_by_name("edit_buyer_note_box"),
        sender_address,
        sp,
        signer,
        method_args=["Realtor"],
        boxes=[[app_id, "Buyer"]],  # type: ignore
    )

    # Execute Txn
    atc_1.execute(algod_client, 2)

    app_info = algod_client.application_info(app_id)
    app_info_formatted = format_app_global_state(app_info["params"]["global-state"])

    res = algod_client.application_boxes(app_id)

    print(algod_client.application_boxes(app_id))

    for box in res["boxes"]:
        print("box", box)
        box_name = base64.b64decode(box["name"]).decode("utf-8")
        print("box key:", box_name)
        box_value = algod_client.application_box_by_name(
            app_id, bytes(box_name, "utf-8")
        )["value"]
        print(
            "box value:",
            base64.b64decode(box_value).decode("utf-8"),
        )
