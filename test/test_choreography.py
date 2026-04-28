from pychor import Party
from pychorq.choreography import LocalQuantumBackend
from pychorq.qubit import Qubit
from pytest import raises
from qutip import ket

def test_qubit_ownership():
    '''
    Qubits have exactly one owner at a time. Sending qubits transfers
    ownership. Parties can only send qubits they own.
    '''
    alice = Party('Alice')
    bob = Party('Bob')
    qubit = Qubit(ket("0"))
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
        loc_val.send(src=alice, dest=charlie)
        # Alice can still send the value to Charlie
        assert loc_val.parties == {alice, bob, charlie}


def test_qubit_list_ownership():
    '''
    Lists of qubits are treated as single values for ownership purposes.
    '''
    alice = Party('Alice')
    bob = Party('Bob')
    qubits = [Qubit(ket("0")), Qubit(ket("1"))]@alice
    with LocalQuantumBackend():
        qubits.send(src=alice, dest=bob)
        # Owner should be exlusively Bob
        assert qubits.parties == {bob}
        # Alice should not be able to send the qubits anymore
        with raises(expected_exception=AssertionError):
            qubits.send(src=alice, dest=bob)
