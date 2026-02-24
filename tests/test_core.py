from pychor import Party
from pychor import locally
from pychorq.core import LocalQuantumBackend
from pytest import raises
from qiskit.circuit import QuantumRegister


def test_qubit_ownership():
    '''
    Qubits have exactly one owner at a time. Sending qubits transfers
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


def test_classical_ownership():
    '''
    Classical values can have multiple owners. Sending classical adds to the
    set of owners. Parties can only send classical values they own.
    '''
    alice = Party('Alice')
    bob = Party('Bob')
    charlie = Party('Charlie')
    val = 42
    with LocalQuantumBackend():
        loc_val = val@alice
        # Owner should be exlusively Alice
        assert loc_val.parties == {alice}
        loc_val.send(src=alice, dest=bob)
        # Alice and Bob should both be owners
        assert loc_val.parties == {alice, bob}
        # Charlie does not own the value and should not be able to send it
        with raises(expected_exception=AssertionError):
            loc_val.send(src=charlie, dest=bob)
