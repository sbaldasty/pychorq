from collections import defaultdict
from pychor import ChoreographyBackend
from pychor import LocatedVal
from pychor import Party
from qiskit.circuit import Qubit


class LocalQuantumBackend(ChoreographyBackend):
    """Backend for simulating qubit-only choreography values.

    - Every LocatedVal must have exactly one location.
    - Every LocatedVal.val must be a Qiskit qubit object.
    """

    def __init__(self):
        self.views = defaultdict(list)

    @staticmethod
    def is_qiskit_qubit(val):
        return isinstance(val, Qubit)

    def _validate_qubit_located_value(self, lv):
        assert isinstance(lv, LocatedVal), f'Expected LocatedVal, got {type(lv)}'
        assert len(lv.parties) == 1, f'Qubit values must have exactly one owner: {lv}'
        assert self.is_qiskit_qubit(lv.val), f'Qubit backend only supports Qiskit qubits: {type(lv.val)}'

    def send(self, party_from, party_to, lv, note=None):
        assert isinstance(party_from, Party)
        assert isinstance(party_to, Party)
        self._validate_qubit_located_value(lv)
        assert party_from in lv.parties, f'{party_from} is not owner of {lv}'

        val = self.unwrap(lv, {party_from})
        self.views[party_to].append(val)

        lv.parties.clear()
        lv.parties.add(party_to)

    def locally(self, f, *args, **kwargs):
        new_args, new_parties = get_val(args)
        output = f(*new_args)
        out = LocatedVal(new_parties.copy(), output)
        self._validate_qubit_located_value(out)
        return out

    def unwrap(self, lv, p):
        self._validate_qubit_located_value(lv)
        if p.issubset(lv.parties):
            return lv.val
        return None

    def unlist(self, ls, length):
        self._validate_qubit_located_value(ls)
        raise Exception('QuantumQubitBackend does not support unlist for single-qubit values')

    def untup(self, ls, length):
        self._validate_qubit_located_value(ls)
        raise Exception('QuantumQubitBackend does not support untup for single-qubit values')

    def undict(self, d, keys):
        self._validate_qubit_located_value(d)
        raise Exception('QuantumQubitBackend does not support undict for single-qubit values')

# TODO Copied from pychor for now, this might need to change for qubits
def get_val(lv):
    if isinstance(lv, LocatedVal):
        return cc.unwrap(lv, lv.parties), lv.parties
    elif isinstance(lv, (tuple, list)):
        vals, parties_ls = zip(*[get_val(x) for x in lv])
        parties_setlist = [p for p in parties_ls if p is not None]
        assert len(parties_setlist) > 0, f'No party information for {lv}'
        parties = set.intersection(*parties_setlist)
        assert len(parties) > 0, f'No participating parties for {lv}'
        return vals, parties
    # elif isinstance(lv, (dict)):
    #     return {get_val(k, party): get_val(v, party) for k, v in lv.items()}
    elif isinstance(lv, (int, float, str)):
        return lv, None
    # else:
    #     return lv
    else:
        raise Exception(f'Unsupported value for local computation: {lv} : {type(lv)}')
