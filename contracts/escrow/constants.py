from pyteal.ast.bytes import Bytes

GLOBAL_CREATOR: Bytes = Bytes("global_creator")  # stores byteslice
GLOBAL_BUYER: Bytes = Bytes("global_buyer")  # stores byteslice
GLOBAL_SELLER: Bytes = Bytes("global_seller")  # stores byteslice

GLOBAL_ESCROW_PAYMENT_1 = Bytes("global_escrow_payment_1")  # stores uint64
GLOBAL_ESCROW_PAYMENT_2 = Bytes("global_escrow_payment_2")  # stores uint64
GLOBAL_ESCROW_TOTAL = Bytes("global_escrow_total")  # stores uint64
GLOBAL_ASA_ID = Bytes("global_asa_id")

GLOBAL_ENABLE_TIME_CHECKS = Bytes("global_enable_time_checks")  # stores uint64
GLOBAL_INSPECTION_START_DATE = Bytes("global_inspection_start_date")  # stores uint64
GLOBAL_INSPECTION_END_DATE = Bytes("global_inspection_end_date")  # stores uint64
GLOBAL_INSPECTION_EXTENSION_DATE = Bytes(
    "global_inspection_extension_date"
)  # stores uint64
GLOBAL_MOVING_DATE = Bytes("global_moving_date")
GLOBAL_CLOSING_DATE = Bytes("global_closing_date")  # stores uint64
GLOBAL_FREE_FUNDS_DATE = Bytes("global_free_funds_date")  # stores uint64

GLOBAL_BUYER_PULLOUT_FLAG = Bytes("global_buyer_pullout_flag")  # stores uint64
GLOBAL_BUYER_ARBITRATION_FLAG = Bytes("global_buyer_arbitration_flag")  # stores uint64
GLOBAL_SELLER_ARBITRATION_FLAG = Bytes(
    "global_seller_arbitration_flag"
)  # stores uint64

INCREMENT_COUNTER = Bytes("increment")
WITHDRAW_BALANCE = Bytes("withdraw_balance")
WITHDRAW_ASA = Bytes("withdraw_ASA")
OPTIN_CONTRACT = Bytes("optin_contract")
OPTOUT_CONTRACT = Bytes("optout_contract")
HAS_ESCROW_PAYMENT_1 = Bytes("has_escrow_payment_1")
HAS_ESCROW_PAYMENT_2 = Bytes("has_escrow_payment_2")
HAS_ESCROW_TOTAL = Bytes("has_escrow_total")

BUYER_SET_PULLOUT = Bytes("buyer_set_pullout")
BUYER_SET_ARBITRATION = Bytes("buyer_set_arbitration")
SELLER_SET_ARBITRATION = Bytes("seller_set_arbitration")