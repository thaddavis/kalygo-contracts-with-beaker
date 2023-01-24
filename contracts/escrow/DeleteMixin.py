from pyteal import abi, TealType, Global, Int, Seq, Approve, Reject, If
from beaker.decorators import external, create, Authorize, delete
from beaker.application import Application


class DeleteMixin(Application):
    @delete
    def delete(self):
        return Approve()
