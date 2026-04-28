from qutip import Qobj
from qutip import basis
from qutip import qeye
from qutip import tensor
from random import random

# Useful for creating common qubits
KET_ZERO = basis(2, 0)
KET_ONE = basis(2, 1)

P0 = KET_ZERO * KET_ZERO.dag()
P1 = KET_ONE * KET_ONE.dag()


class QuantumSystem:
    def __init__(self, state, qubits):
        assert isinstance(state, Qobj)
        assert isinstance(qubits, list)
        self.state = state
        self.qubits = qubits


class Qubit:
    def __init__(self, state):
        assert isinstance(state, Qobj)
        assert state.dims == [[2], [1]]
        self.system = QuantumSystem(state.unit(), [self])

    def index(self):
        return self.system.qubits.index(self)

    def measure(self):
        n = len(self.system.qubits)
        i = self.index()

        def lifted(P):
            ops = [qeye(2)] * n
            ops[i] = P
            return tensor(*ops)

        M0 = lifted(P0)
        M1 = lifted(P1)
        state = self.system.state
        prob_0 = (state.dag() * M0 * state)[0, 0].real
        bit = 0 if random() < prob_0 else 1
        M = M0 if bit == 0 else M1

        self.system.state = (M * state).unit()
        return bit

    @classmethod
    def combine_systems(cls, q1, q2):
        assert isinstance(q1, Qubit)
        assert isinstance(q2, Qubit)

        if q1.system is q2.system:
            return

        system = QuantumSystem(
            state=tensor(q1.system.state, q2.system.state),
            qubits=q1.system.qubits + q2.system.qubits)

        for q in system.qubits:
            q.system = system
