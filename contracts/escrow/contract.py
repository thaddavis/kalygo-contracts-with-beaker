from typing import Final
from pyteal import abi, TealType, Global, Int, Seq, Approve, Reject, If
from beaker.application import Application
from beaker.client.application_client import ApplicationClient
from beaker import sandbox
from beaker.state import ApplicationStateValue
import json
from .InitMixin import InitMixin
from .subroutines import (Subroutine_Increment_Mixin)

class EscrowContract(
    InitMixin,
    Subroutine_Increment_Mixin
):

    global_buyer_pullout_flag: Final[ApplicationStateValue] = ApplicationStateValue(stack_type=TealType.uint64, default=Int(0))
    global_buyer_arbitration_flag: Final[ApplicationStateValue] = ApplicationStateValue(stack_type=TealType.uint64, default=Int(0))
    global_seller_arbitration_flag: Final[ApplicationStateValue] = ApplicationStateValue(stack_type=TealType.uint64, default=Int(0))
