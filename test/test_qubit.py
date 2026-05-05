from pychorq.qubit import Qubit
from pychorq.state import bell_state
from pychorq.state import ket_one
from pychorq.state import ket_plus
from pychorq.state import ket_zero
from qutip import ket
from qutip import sigmax
from qutip.core.gates import cnot


def unordered_edge_set(edges):
    return {frozenset(edge) for edge in edges}


def entanglement_structure(system, nodes, edges):
    graph = system.entanglements
    return (
        set(graph.nodes) == set(nodes)
        and unordered_edge_set(graph.edges) == unordered_edge_set(edges))


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
    assert q1.system is q2.system
    # State is the Bell state
    assert q1.system.state == bell_state()
    assert entanglement_structure(q1.system, [q1, q2], [(q1, q2)])


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
    assert entanglement_structure(q1.system, [q1], [])
    assert entanglement_structure(q2.system, [q2], [])
    # Measure the second qubit of a Bell pair
    q1 = Qubit(ket_plus())
    q2 = Qubit(ket_zero())
    Qubit.unitary(cnot(), qubits=[q1, q2])
    [bit] = Qubit.measure([q2])
    assert q1.system is not q2.system
    expected = ket_zero() if bit == 0 else ket_one()
    assert q1.system.state == expected
    assert q2.system.state == expected
    assert entanglement_structure(q1.system, [q1], [])
    assert entanglement_structure(q2.system, [q2], [])


def test_normalization():
    '''
    Qubits become normalized even if initialized with state that is not.
    '''
    q = Qubit(ket_zero() * 10)
    assert q.system.state == ket_zero()


def test_unitary_targets_middle_qubit():
    '''
    A unitary applied to the middle qubit of a 3-qubit system expands to the
    correct index. It leaves the other qubits unchanged.
    '''
    q1 = Qubit(ket_zero())
    q2 = Qubit(ket_zero())
    q3 = Qubit(ket_zero())
    Qubit.unitary(cnot(), qubits=[q1, q2])
    Qubit.unitary(cnot(), qubits=[q2, q3])
    assert q1.system.state == ket("000")
    assert entanglement_structure(q1.system, [q1, q2, q3], [(q1, q2), (q2, q3)])
    Qubit.unitary(sigmax(), qubits=[q2])
    assert Qubit.measure([q1, q2, q3]) == [0, 1, 0]


def test_unitary_on_non_adjacent_qubits():
    '''
    A unitary correctly targets qubits that are not adjacent in the combined
    system.
    '''
    q1 = Qubit(ket_one())
    q2 = Qubit(ket_zero())
    q3 = Qubit(ket_zero())
    Qubit.unitary(cnot(), qubits=[q1, q2])  # |10> -> |11>; system [q1,q2]
    Qubit.unitary(cnot(), qubits=[q1, q3])  # q3 joins; CNOT(idx0,idx2) on |110> -> |111>
    assert q1.system.state == ket("111")
    assert entanglement_structure(q1.system, [q1, q2, q3], [(q1, q2), (q1, q3)])


def test_ghz_state_creation():
    '''
    CNOT from the same control onto two separate targets produces a GHZ state.
    '''
    q1 = Qubit(ket_plus())
    q2 = Qubit(ket_zero())
    q3 = Qubit(ket_zero())
    Qubit.unitary(cnot(), qubits=[q1, q2])
    Qubit.unitary(cnot(), qubits=[q1, q3])
    assert q1.system.state == (ket("000") + ket("111")).unit()
    assert entanglement_structure(q1.system, [q1, q2, q3], [(q1, q2), (q1, q3)])


def test_measure_targets_middle_qubit():
    '''
    Measuring the middle qubit of a GHZ state collapses the other two qubits
    to the same value.
    '''
    q1 = Qubit(ket_plus())
    q2 = Qubit(ket_zero())
    q3 = Qubit(ket_zero())
    Qubit.unitary(cnot(), qubits=[q1, q2])
    Qubit.unitary(cnot(), qubits=[q1, q3])
    # Collapse the middle qubit
    [b2] = Qubit.measure([q2])
    assert q2.system.qubits == [q2]
    assert entanglement_structure(q2.system, [q2], [])
    assert q1.system is q3.system
    assert entanglement_structure(q1.system, [q1, q3], [(q1, q3)])
    # Collapse the others
    [b1, b3] = Qubit.measure([q1, q3])
    assert b1 == b2 == b3
    assert q1.system is not q3.system
    assert entanglement_structure(q1.system, [q1], [])
    assert entanglement_structure(q3.system, [q3], [])


def test_measure_middle_qubit_separates_chain():
    '''
    Measuring the middle qubit of a chain-entangled 3-qubit system separates
    all three into independent systems and preserves the surronding qubit
    states.
    '''
    q1 = Qubit(ket_zero())
    q2 = Qubit(ket_one())
    q3 = Qubit(ket_zero())
    Qubit.unitary(cnot(), qubits=[q1, q2])
    Qubit.unitary(cnot(), qubits=[q2, q3])
    [bit] = Qubit.measure([q2])
    assert bit == 1
    # Removing the center node's edges separates the graph into three components
    assert q1.system is not q2.system
    assert q2.system is not q3.system
    assert q1.system is not q3.system
    assert q1.system.state == ket_zero()
    assert entanglement_structure(q1.system, [q1], [])
    assert entanglement_structure(q2.system, [q2], [])
    assert q3.system.state == ket_one()
    assert entanglement_structure(q3.system, [q3], [])
