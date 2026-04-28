from pychorq.qubit import Qubit
from qutip import ket
from qutip import sigmax
from qutip.qip.operations import cnot


def test_single_unitary():
    '''
    Applying a unitary to a single qubit updates its state.
    '''
    qubit = Qubit(ket("0"))
    Qubit.unitary(sigmax(), qubits=[qubit])
    assert qubit.system.state == ket("1")


def test_multi_unitary():
    '''
    Applying a unitary to multiple qubits combinese their systems. The unitary
    acts on the combined system.
    '''
    q1 = Qubit(ket("0"))
    q2 = Qubit(ket("1"))
    Qubit.unitary(cnot(), qubits=[q1, q2])
    # Qubits share the same state now
    assert q1.system == q2.system
