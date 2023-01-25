from algosdk.v2client import indexer
import config.general as config


class Indexer:
    # Declare the static variables
    client = None  # static variable

    # def __init__(self):

    @staticmethod
    def getClient():
        if Indexer.client:
            return Indexer.client
        else:
            headers = {
                "X-API-Key": config.algod_token,
            }
            Indexer.client = indexer.IndexerClient(
                config.algod_token, config.indexer_url, headers
            )
            return Indexer.client
