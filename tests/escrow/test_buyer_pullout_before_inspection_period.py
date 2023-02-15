import pytest
from modules.actions.escrow.deploy_new import deploy_new
from modules.actions.escrow.delete_contract import delete_contract
from datetime import datetime
from algosdk import account
from contracts.escrow.contract import EscrowContract
from algosdk.future import transaction
import config.escrow as config
from modules.helpers.utils import (
    format_app_global_state,
    get_private_key_from_mnemonic,
)
from algosdk.abi import Contract
from modules.clients.AlgodClient import Algod
from modules.helpers.get_txn_params import get_txn_params
from modules.helpers.time import get_current_timestamp, get_future_timestamp_in_secs
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
        config.account_a_address,
        config.account_a_mnemonic,
        config.account_b_address,
        config.account_c_address,
        config.escrow_payment_1,
        config.escrow_payment_2,
        config.total_price,
        config.stablecoin_ASA,
        int(get_current_timestamp()),  # Inspection Period Start Date
        int(get_future_timestamp_in_secs(60)),  # Inspection Period End Date
        int(get_future_timestamp_in_secs(90)),  # Inspection Period Extension Date
        int(get_future_timestamp_in_secs(120)),  # Moving Date
        int(get_future_timestamp_in_secs(240)),  # Closing Date
        int(get_future_timestamp_in_secs(360)),  # Free Funds Date
        True,  # True, -> ENABLE_TIME_CHECKS
    )
    yield deployed_contract["app_id"], deployed_contract[
        "confirmed_round"
    ], deployed_contract["inspection_start"], deployed_contract["inspection_end"]
    print()
    print("tear down in fixture", deployed_contract["app_id"])
    delete_contract(
        EscrowContract,
        deployed_contract["app_id"],
        config.account_a_mnemonic,
    )


def test_buyer_pullout(escrow_contract):
    app_id, confirmed_round, inspection_start, inspection_end = escrow_contract
    algod_client = Algod.getClient()
    app_info = algod_client.application_info(app_id)
    app_info_formatted = format_app_global_state(app_info["params"]["global-state"])
    print()
    print(
        '"glbl_buyer_pullout_flag"',
        app_info_formatted["glbl_buyer_pullout_flag"],
    )
    assert app_info_formatted["glbl_buyer_pullout_flag"] == 0

    #
    # onchain_timestamp = algod_client.block_info(confirmed_round)["block"]["ts"]
    # print("debug...")
    # print(datetime.fromtimestamp(onchain_timestamp), ":On-chain time:")
    # print(datetime.fromtimestamp(inspection_end), ":Inspection period end date:")
    #

    buyer_address = config.account_b_address
    buyer_mnemonic = config.account_b_mnemonic
    buyer_private_key = get_private_key_from_mnemonic(buyer_mnemonic)
    signer = AccountTransactionSigner(buyer_private_key)

    with open("build/abi.json") as f:
        js = f.read()
    c = Contract.from_json(js)
    atc = AtomicTransactionComposer()
    sp = algod_client.suggested_params()

    print("testing buyer pullout...")

    atc.add_method_call(
        app_id,
        c.get_method_by_name("buyer_set_pullout"),
        buyer_address,
        sp,
        signer,
        method_args=[],
    )

    atc.execute(algod_client, 2)

    app_info = algod_client.application_info(app_id)
    app_info_formatted = format_app_global_state(app_info["params"]["global-state"])
    print()
    print(
        '"glbl_buyer_pullout_flag"',
        app_info_formatted["glbl_buyer_pullout_flag"],
    )
    assert app_info_formatted["glbl_buyer_pullout_flag"] == 1


def teardown_module(module):
    """teardown any state that was previously setup with a setup_module method."""
