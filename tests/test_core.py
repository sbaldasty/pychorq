from pychor import Party
from pychor import locally
from pychorq.core import LocalQuantumBackend
from pytest import raises
from qiskit.circuit import QuantumRegister


def test_single_qubit_ownership():
    '''
    Qubits have exactly one owner at a time. Sending a qubit transfers
    ownership. Parties can only send qubits they own.
    '''
    alice = Party('Alice')
    bob = Party('Bob')
    qubit = QuantumRegister(1, "q")
    with LocalQuantumBackend():
        loc_q = qubit@alice
        # Owner should be exlusively Alice
        assert loc_q.parties == {alice}
        loc_q.send(src=alice, dest=bob)
        # Owner should be exlusively Bob
        assert loc_q.parties == {bob}
        # Alice should not be able to send the qubit anymore
        with raises(expected_exception=AssertionError):
            loc_q.send(src=alice, dest=bob)
