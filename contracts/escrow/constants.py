from pyteal.ast.bytes import Bytes

GLOBAL_CREATOR: Bytes = Bytes("glbl_creator")  # stores byteslice
GLOBAL_BUYER: Bytes = Bytes("glbl_buyer")  # stores byteslice
GLOBAL_SELLER: Bytes = Bytes("glbl_seller")  # stores byteslice

GLOBAL_ESCROW_PAYMENT_1 = Bytes("glbl_escrow_1")  # stores uint64
GLOBAL_ESCROW_PAYMENT_2 = Bytes("glbl_escrow_2")  # stores uint64
GLOBAL_TOTAL = Bytes("glbl_total")  # stores uint64
GLOBAL_ASA_ID = Bytes("glbl_asa_id")

GLOBAL_ENABLE_TIME_CHECKS = Bytes("glbl_enable_time_checks")  # stores uint64
GLOBAL_INSPECT_START_DATE = Bytes("glbl_inspect_start_date")  # stores uint64
GLOBAL_INSPECT_END_DATE = Bytes("glbl_inspect_end_date")  # stores uint64
GLOBAL_INSPECT_EXTENSION_DATE = Bytes("glbl_inspect_extension_date")  # stores uint64
GLOBAL_MOVING_DATE = Bytes("glbl_moving_date")
GLOBAL_CLOSING_DATE = Bytes("glbl_closing_date")  # stores uint64
GLOBAL_FREE_FUNDS_DATE = Bytes("glbl_free_funds_date")  # stores uint64

GLOBAL_BUYER_PULLOUT_FLAG = Bytes("glbl_buyer_pullout_flag")  # stores uint64
GLOBAL_BUYER_ARBITRATION_FLAG = Bytes("glbl_buyer_arbitration_flag")  # stores uint64
GLOBAL_SELLER_ARBITRATION_FLAG = Bytes("glbl_seller_arbitration_flag")  # stores uint64

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
