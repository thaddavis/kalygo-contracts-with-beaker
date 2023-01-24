from pyteal import abi, TealType, Global, Int, Seq, Approve, Reject, If
from beaker.decorators import external, create, Authorize
from beaker.application import Application


class InitMixin(Application):
    @create
    def create(self, global_buyer_pullout_flag: abi.Uint64):
        return Seq(
            self.initialize_application_state(),
            # self.max_count.set(max_count.get()),
        )
