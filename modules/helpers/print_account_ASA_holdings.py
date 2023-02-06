def print_account_ASA_holdings(
    algod_client, indexer_client, ASA_id: int, account_in_question: str
):
    print("")
    asset_info = algod_client.asset_info(ASA_id)
    results = indexer_client.accounts(asset_id=ASA_id)
    print("asset name:", asset_info["params"]["name"])
    print("")

    for account in results["accounts"]:
        if account["address"] == account_in_question:
            if "assets" in account:
                print("address:", account["address"])
                for asset in account["assets"]:
                    if asset["asset-id"] == ASA_id:
                        print("holdings are: ", asset["amount"])
                        continue
                print("")

    print("")
