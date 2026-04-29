from pychorq.qubit import Qubit
from pychorq.state import bell_state
from pychorq.state import ket_one
from pychorq.state import ket_plus
from pychorq.state import ket_zero
from qutip import sigmax
from qutip.core.gates import cnot


def test_single_unitary():
    '''
    Applying a unitary to a single qubit updates its state.
    '''
    qubit = Qubit(ket_zero())
    Qubit.unitary(sigmax(), qubits=[qubit])
    assert qubit.system.state == ket_one()


def test_multi_unitary():
    '''
    Applying a unitary to multiple qubits combinese their systems. The unitary
    acts on the combined system.
    '''
    q1 = Qubit(ket_plus())
    q2 = Qubit(ket_zero())
    Qubit.unitary(cnot(), qubits=[q1, q2])
    # Qubits share the same state now
    assert q1.system == q2.system
    # State is the Bell state
    assert q1.system.state == bell_state()


def test_identity_measurement():
    '''
    Measuring a collapsed qubit returns the same value always.
    '''
    # Qubit already in the computational basis
    q = Qubit(ket_one())
    assert Qubit.measure([q]) == [1]
    # Random qubit measured twice
    q = Qubit(ket_plus())
    b1 = Qubit.measure([q])
    b2 = Qubit.measure([q])
    assert b1 == b2


def test_measure_first_qubit():
    '''
    Measuring a qubit properly affects the rest of the system.
    '''
    # Measure the first qubit of a Bell pair
    q1 = Qubit(ket_plus())
    q2 = Qubit(ket_zero())
    Qubit.unitary(cnot(), qubits=[q1, q2])
    [bit] = Qubit.measure([q1])
    assert q1.system is not q2.system
    expected = ket_zero() if bit == 0 else ket_one()
    assert q1.system.state == expected
    assert q2.system.state == expected
    # Measure the second qubit of a Bell pair
    q1 = Qubit(ket_plus())
    q2 = Qubit(ket_zero())
    Qubit.unitary(cnot(), qubits=[q1, q2])
    [bit] = Qubit.measure([q2])
    assert q1.system is not q2.system
    expected = ket_zero() if bit == 0 else ket_one()
    assert q1.system.state == expected
    assert q2.system.state == expected


def test_normalization():
    '''
    Qubits should be normalized even if initialized with state that is not.
    '''
    q = Qubit(ket_zero() * 10)
    assert q.system.state == ket_zero()
