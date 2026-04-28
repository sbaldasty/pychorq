from pychor import LocalBackend
from pychor import LocatedVal
from pychor import Party
from pychorq.qubit import Qubit


class LocalQuantumBackend(LocalBackend):
    def __init__(self):
        super().__init__()

    def send(self, party_from, party_to, lv, note=None):
        assert isinstance(lv, LocatedVal)
        assert isinstance(party_from, Party)
        assert isinstance(party_to, Party)
        assert party_from in lv.parties

        single_owner = isinstance(lv.val, Qubit)
        single_owner |= isinstance(lv.val, list) and all(isinstance(q, Qubit) for q in lv.val)

        if not single_owner:
            return super().send(party_from, party_to, lv, note)

        qr = self.unwrap(lv, {party_from})
        self.views[party_to].append(qr)
        lv.parties.clear()
        lv.parties.add(party_to)
