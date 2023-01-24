from algosdk.v2client import algod
import config.general as config


class Algod:
    # Declare the static variables
    client = None  # static variable

    @staticmethod
    def getClient(
        algod_token: str = config.algod_token, algod_url: str = config.algod_url
    ):
        if Algod.client:
            return Algod.client
        else:
            headers = {
                "X-API-Key": algod_token,
            }
            Algod.client = algod.AlgodClient(algod_token, algod_url, headers)
            return Algod.client
