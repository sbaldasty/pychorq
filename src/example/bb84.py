from example.common import choose_bits
from example.common import choose_indexes
from example.common import eve_detected
from example.common import split_bits
from pychor import Party
from pychor import local_function
from pychorq.choreography import LocalQuantumBackend
from pychorq.qubit import Qubit
from qutip import ket
from qutip import sigmax
from qutip import sigmaz
from random import choices


@local_function
def choose_bases(n):
    '''
    Choose n random bases, either 'X' or 'Z'.
    '''
    return choices(['X', 'Z'], k=n)


@local_function
def set_qubits(bits, bases):
    '''
    Initialize qubits from bits and rotate them pairwise according to bases.
    '''
    qubits = [Qubit(ket(str(bit))) for bit in bits]
    for q, b in zip(qubits, bases):
        op = sigmax() if b == 'X' else sigmaz()
        Qubit.unitary(op, [q])

    return qubits


@local_function
def measure_qubits(qubits, bases):
    '''
    Measure qubits in the given bases pairwise.
    '''
    for qubit, basis in zip(qubits, bases):
        op = sigmax() if basis == 'X' else sigmaz()
        Qubit.unitary(op, [qubit])

    return Qubit.measure(qubits)


@local_function
def sift_bits(bits, bases1, bases2):
    '''
    Keep only the bits where the bases match (all three lists must be the same
    length).
    '''
    tbl = zip(bits, bases1, bases2)
    return [bit for bit, b1, b2 in tbl if b1 == b2]


def bb84(alice, bob, n_bits, n_checks, threshold):
    with LocalQuantumBackend():
        # Alice chooses random bits and a random basis for each bit
        a_bits = choose_bits(n_bits@alice)
        a_bases = choose_bases(n_bits@alice)

        # Alice creates qubits according to her chosen bits and bases
        qubits = set_qubits(a_bits, a_bases)

        # Alice sends the qubits to Bob
        qubits.send(src=alice, dest=bob)

        # Bob chooses random bases and measures the received qubits in them
        b_bases = choose_bases(n_bits@bob)
        b_bits = measure_qubits(qubits, b_bases)

        # Alice and Bob exchange their bases
        a_bases.send(src=alice, dest=bob)
        b_bases.send(src=bob, dest=alice)

        # Alice and Bob keep only the bits where their bases matched
        a_keep = sift_bits(a_bits, a_bases, b_bases)
        b_keep = sift_bits(b_bits, a_bases, b_bases)

        # Alice chooses and shares indexes of bits to check for eavesdropping
        a_idxs = choose_indexes(a_keep, n_checks@alice)
        a_idxs.send(src=alice, dest=bob)

        # Alice and Bob split their remaining bits into key bits and check bits
        a_key, a_chk = split_bits(a_keep, a_idxs).untup(2)
        b_key, b_chk = split_bits(b_keep, a_idxs).untup(2)

        # Alice and Bob exchange their check bits
        a_chk.send(src=alice, dest=bob)
        b_chk.send(src=bob, dest=alice)

        # Alice and Bob check for eavesdropping by comparing their check bits
        a_eve_detected = eve_detected(a_chk, b_chk, threshold@alice)
        b_eve_detected = eve_detected(a_chk, b_chk, threshold@bob)

        return a_key, b_key, a_eve_detected, b_eve_detected


if __name__ == '__main__':
    alice = Party('alice')
    bob = Party('bob')
    a_key, b_key, a_eve_detected, b_eve_detected = bb84(alice, bob, 100, 10, 0)
    print('BB84')
    print(a_key, a_eve_detected)
    print(b_key, b_eve_detected)
