import pytest
from algosdk import constants, logic
import config.escrow as config
from modules.helpers.utils import (
    get_private_key_from_mnemonic,
)
from algosdk.abi import Contract
from contracts.escrow.contract import EscrowContract
from modules.actions.escrow.deploy_new import deploy_new
from modules.actions.escrow.fund_minimum_balance import fund_minimum_balance
from modules.actions.escrow.withdraw_ASA_from_contract import withdraw_ASA_from_contract
from modules.actions.escrow.withdraw_balance import withdraw_balance
from modules.actions.escrow.optin_contract_to_ASA import optin_contract_to_ASA
from modules.actions.escrow.transfer_ASA_to_contract import transfer_ASA_to_contract

from modules.actions.escrow.optout_contract_from_ASA import optout_contract_from_ASA
from modules.actions.escrow.delete_contract import delete_contract
import pytest
from modules.helpers.time import get_current_timestamp, get_future_timestamp_in_secs
from modules.clients.AlgodClient import Algod
from modules.helpers.get_txn_params import get_txn_params

from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
)


@pytest.fixture(scope="module")
def escrow_contract():
    print()
    print()
    print("deploying escrow contract...")

    deployed_contract = deploy_new(
        EscrowContract,
        config.account_a_address,  # deployer/creator of contract ie: likely will be buyer
        config.account_a_mnemonic,  # deployer/creator of contract mnemonic ie: likely will be buyer
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
        foreign_apps=[],
        foreign_assets=[config.stablecoin_ASA],
    )
    yield deployed_contract["app_id"]
    print()
    print("tear down in fixture", deployed_contract["app_id"])
    delete_contract(
        EscrowContract,
        deployed_contract["app_id"],
        config.account_a_mnemonic,
    )


def test_optin_contract_to_ASA_then_buyer_send_and_withdraw_ASA(escrow_contract):
    app_id = escrow_contract

    algod_client = Algod.getClient()
    txn_params = get_txn_params(algod_client, constants.MIN_TXN_FEE, 1)
    opt_txn_params = get_txn_params(algod_client, constants.MIN_TXN_FEE, 2)

    buyer_address = config.account_b_address
    buyer_private_key = get_private_key_from_mnemonic(config.account_b_mnemonic)
    contract_address = logic.get_application_address(app_id)
    stablecoin_ASA = config.stablecoin_ASA

    res = algod_client.account_info(contract_address)
    assert res["amount"] == 0

    with open("build/abi.json") as f:
        js = f.read()
    ABI = Contract.from_json(js)

    atc = AtomicTransactionComposer()
    fund_minimum_balance(
        atc,
        algod_client,
        txn_params,
        buyer_address,
        buyer_private_key,
        contract_address,
        200000,  # 100,000 mAlgos min_balance for optin to ASA + 100,000 mAlgos for contract to be able to call other contracts
    )

    res = algod_client.account_info(contract_address)
    assert res["amount"] == 200000

    atc = AtomicTransactionComposer()
    optin_contract_to_ASA(
        app_id,
        atc,
        ABI,
        algod_client,
        opt_txn_params,
        buyer_address,
        buyer_private_key,
        contract_address,
        stablecoin_ASA,
    )

    res = Algod.getClient().account_info(contract_address)
    assert res["amount"] == 200000

    account_info = algod_client.account_info(contract_address)
    print()
    print("account_info", account_info)
    print()
    print("loop over assets opted into by the contract address")
    for asset in account_info["assets"]:
        if asset["asset-id"] == stablecoin_ASA:
            print("contract ASA holdings before transfer:", asset["amount"])
            assert asset["amount"] == 0

    # Transfer ASA to contract
    atc = AtomicTransactionComposer()
    transfer_ASA_to_contract(
        atc,
        algod_client,
        txn_params,
        buyer_address,
        buyer_private_key,
        contract_address,
        stablecoin_ASA,
        20,
    )

    print("debug...", contract_address)

    account_info = algod_client.account_info(contract_address)
    for asset in account_info["assets"]:
        if asset["asset-id"] == stablecoin_ASA:
            print("contract ASA holdings after transfer:", asset["amount"])
            assert asset["amount"] == 20

    atc = AtomicTransactionComposer()
    withdraw_ASA_from_contract(
        app_id,
        atc,
        ABI,
        algod_client,
        opt_txn_params,
        buyer_address,
        buyer_private_key,
        stablecoin_ASA,
    )

    account_info = algod_client.account_info(contract_address)
    for asset in account_info["assets"]:
        if asset["asset-id"] == stablecoin_ASA:
            print("contract ASA holdings after transfer:", asset["amount"])
            assert asset["amount"] == 0

    atc = AtomicTransactionComposer()
    optout_contract_from_ASA(
        app_id,
        atc,
        ABI,
        algod_client,
        opt_txn_params,
        buyer_address,
        buyer_private_key,
        stablecoin_ASA,
    )

    account_info = algod_client.account_info(contract_address)
    assert len(account_info["assets"]) == 0

    atc = AtomicTransactionComposer()
    withdraw_balance(
        app_id, atc, ABI, algod_client, txn_params, buyer_address, buyer_private_key
    )

    res = algod_client.account_info(contract_address)
    assert res["amount"] == 0
