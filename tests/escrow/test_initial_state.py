import pytest
import json
from modules.actions.escrow.deploy_new import deploy_new
from modules.actions.escrow.delete_contract import delete_contract

from algosdk import logic
from contracts.escrow.contract import EscrowContract
import config.escrow as config
from modules.helpers.utils import (
    format_app_global_state,
)
from modules.helpers.time import get_current_timestamp, get_future_timestamp_in_secs
from modules.clients.AlgodClient import Algod


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


def test_initial_state(escrow_contract):
    app_id = escrow_contract
    app_info = Algod.getClient().application_info(app_id)
    app_info_formatted = format_app_global_state(app_info["params"]["global-state"])
    print(json.dumps(app_info_formatted, indent=4))

    assert app_info_formatted["glbl_escrow_payment_1"] == 1000000
    assert app_info_formatted["glbl_escrow_payment_2"] == 2000000
    assert app_info_formatted["glbl_total_price"] == 3000000
    assert app_info_formatted["glbl_asa_id"] == config.stablecoin_ASA
    assert app_info_formatted["glbl_buyer_arbitration_flag"] == 0

    app_address = logic.get_application_address(app_id)
    res = Algod.getClient().account_info(app_address)
    assert res["amount"] == 0
