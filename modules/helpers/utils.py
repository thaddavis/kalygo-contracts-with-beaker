from ast import Num
from typing import Any
from algosdk import account, mnemonic
from algosdk.future import transaction
from algosdk.kmd import KMDClient
from algosdk.v2client.algod import AlgodClient
import base64
from algosdk.encoding import encode_address

MICRO_ALGO = 1
ALGO = MICRO_ALGO * (10**6)


def get_kmd_client(address="http://localhost:4002", token="a" * 64) -> KMDClient:
    return KMDClient(token, address)


def get_keys_from_wallet(
    kmd_client: KMDClient, wallet_name="unencrypted-default-wallet", wallet_password=""
) -> "list[str] | None":
    wallets = kmd_client.list_wallets()

    handle = None
    for wallet in wallets:
        if wallet["name"] == wallet_name:
            handle = kmd_client.init_wallet_handle(wallet["id"], wallet_password)
            break

    if handle is None:
        raise Exception("Could not find wallet")

    private_keys = None
    try:
        addresses = kmd_client.list_keys(handle)
        private_keys = [
            kmd_client.export_key(handle, wallet_password, address)
            for address in addresses
        ]
    finally:
        kmd_client.release_wallet_handle(handle)

    return private_keys


def get_algod_client(address="http://localhost:4001", token="a" * 64):
    return AlgodClient(token, address)


def generate_account():
    (private_key, _) = account.generate_account()
    return private_key


def make_atomic(
    signing_keys=[], transactions=[]
) -> "list[transaction.SignedTransaction]":
    return [
        tx.sign(key)
        for key, tx in zip(
            signing_keys, transaction.assign_group_id(transactions), strict=True
        )
    ]


def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    # return base64.encode(private_key)
    return private_key


def wait_for_confirmation(client, txid):
    last_round = client.status().get("last-round")
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get("confirmed-round") and txinfo.get("confirmed-round") > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print(
        "Transaction {} confirmed in round {}.".format(
            txid, txinfo.get("confirmed-round")
        )
    )
    return txinfo


# helper function to compile program source


def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


# convert 64 bit integer i to byte string


def intToBytes(i):
    return i.to_bytes(8, "big")


def format_app_global_state(state):
    formatted = {}

    for item in state:
        key = item["key"]
        value = item["value"]
        formatted_key = base64.b64decode(key).decode("utf-8")
        if value["type"] == 1:
            # byte string
            if formatted_key == "owner":
                formatted_value = encode_address(base64.b64decode(value["bytes"]))
            else:
                formatted_value = value["bytes"]
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value["uint"]
    return formatted


def format_state(state):
    formatted = {}
    for item in state:
        key = item["key"]
        value = item["value"]
        formatted_key = base64.b64decode(key).decode("utf-8")
        if value["type"] == 1:
            # byte string
            if formatted_key == "owner":
                formatted_value = encode_address(base64.b64decode(value["bytes"]))
            else:
                formatted_value = value["bytes"]
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value["uint"]
    return formatted


# read app global state


def read_created_app_state(client: AlgodClient, addr: Any, app_id: Num):
    results = client.account_info(addr)
    apps_created = results["created-apps"]
    for app in apps_created:
        if app["id"] == app_id:
            return app
    return {}
