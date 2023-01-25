from algosdk.v2client import indexer
import config.escrow as config
from modules.clients.AlgodClient import Algod
from modules.clients.IndexerClient import Indexer

stablecoin_ASA: int = config.stablecoin_ASA


def main():

    print("")
    asset_info = Algod.getClient().asset_info(stablecoin_ASA)
    results = Indexer.getClient().accounts(asset_id=stablecoin_ASA)
    # print("assets account info: {}".format(
    #     json.dumps(results, indent=4)))
    print("asset name:", asset_info["params"]["name"])
    print("")
    print("HOLDERS")
    print("")

    for account in results["accounts"]:
        if "assets" in account:
            print("address:", account["address"])
            for asset in account["assets"]:
                if asset["asset-id"] == stablecoin_ASA:
                    print("holdings are: ", asset["amount"])
                    continue
            print("")
