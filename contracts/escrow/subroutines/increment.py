from pyteal import abi, TealType, Global, Int, Seq, Approve, Reject, If
from beaker.decorators import external, create, Authorize
from beaker.application import Application

class Subroutine_Increment_Mixin(Application):
    @external(authorize=Authorize.only(Global.creator_address()))
    def increment(self):
        return Seq(
            If(
                self.global_buyer_pullout_flag + Int(1) < Int(10)
            ).Then(
                self.global_buyer_pullout_flag.set(self.global_buyer_pullout_flag + Int(1)),
                Approve()
            ).Else(
                Reject()
            )
        )