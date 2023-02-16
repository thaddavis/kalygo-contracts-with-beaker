from pyteal import *
from beaker.application import Application
from ..constants import *


@Subroutine(TealType.uint64)
def guard_delete_byr_note_box(acct: Expr):
    return Seq(Or(And(App.globalGet(GLOBAL_BUYER) == acct)))
