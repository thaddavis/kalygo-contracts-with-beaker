import time
from datetime import datetime
import pytest
from modules.actions.escrow.deploy_new import deploy_new
from modules.actions.escrow.delete_contract import delete_contract
from contracts.escrow.contract import EscrowContract
from algosdk import account, error
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

buyer_private_key = get_private_key_from_mnemonic(config.account_b_mnemonic)


@pytest.fixture(scope="function")
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
        int(get_future_timestamp_in_secs(8)),  # Inspection Period End Date
        int(get_future_timestamp_in_secs(40)),  # Inspection Period Extension Date
        int(get_future_timestamp_in_secs(50)),  # Moving Date
        int(get_future_timestamp_in_secs(60)),  # Closing Date
        int(get_future_timestamp_in_secs(120)),  # Free Funds Date
    )
    yield deployed_contract["app_id"], deployed_contract[
        "confirmed_round"
    ], deployed_contract["inspection_start"], deployed_contract["inspection_end"]
    print()
    print("teardown phase of fixture", "deleting app_id:", deployed_contract["app_id"])
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
        '"global_buyer_pullout_flag"',
        app_info_formatted["global_buyer_pullout_flag"],
    )
    assert app_info_formatted["global_buyer_pullout_flag"] == 0

    onchain_timestamp = algod_client.block_info(confirmed_round)["block"]["ts"]
    last_round = confirmed_round
    while onchain_timestamp < inspection_end:
        status = algod_client.status()
        print(
            "confirmed_round",
            confirmed_round,
            'status["last-round"]',
            status["last-round"],
        )
        if last_round != status["last-round"]:
            last_round = status["last-round"]
            onchain_timestamp = algod_client.block_info(status["last-round"])["block"][
                "ts"
            ]

        # print(datetime.fromtimestamp(onchain_timestamp), ":On-chain time:")
        # print(datetime.fromtimestamp(inspection_end), ":Inspection period end date:")

        time.sleep(2)

    print("inspection period has elapsed...")

    with open("build/abi.json") as f:
        js = f.read()
    c = Contract.from_json(js)
    atc = AtomicTransactionComposer()
    sp = algod_client.suggested_params()

    with pytest.raises(error.AlgodHTTPError):
        print("testing buyer pullout...")

        buyer_address = config.account_b_address
        buyer_mnemonic = config.account_b_mnemonic
        buyer_private_key = get_private_key_from_mnemonic(buyer_mnemonic)
        signer = AccountTransactionSigner(buyer_private_key)

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
        '"global_buyer_pullout_flag"',
        app_info_formatted["global_buyer_pullout_flag"],
    )
    assert app_info_formatted["global_buyer_pullout_flag"] == 0
    print("`buyer_set_pullout` failed as expected")


# def teardown_module(module):
#     """teardown any state that was previously setup with a setup_module method."""
