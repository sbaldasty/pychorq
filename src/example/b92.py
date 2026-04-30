from example.common import choose_bits
from example.common import choose_indexes
from example.common import eve_detected
from example.common import split_bits
from pychor import Party
from pychor import local_function
from pychorq.choreography import LocalQuantumBackend
from pychorq.qubit import Qubit
from pychorq.state import ket_plus
from pychorq.state import ket_zero
from qutip.core.gates import hadamard_transform
from qutip import sigmaz
from random import choices


@local_function
def encode_bits(bits):
    return [Qubit(ket_zero() if bit == 0 else ket_plus()) for bit in bits]


@local_function
def choose_bases(n):
    return choices(['X', 'Z'], k=n)


@local_function
def measure_qubits(qubits, bases):
    for qubit, basis in zip(qubits, bases):
        op = hadamard_transform() if basis == 'X' else sigmaz()
        Qubit.unitary(op, [qubit])

    return Qubit.measure(qubits)


@local_function
def infer_bits(bases, bits):
    return [int(bit == 1 and basis == 'Z')
        for basis, bit in zip(bases, bits)]


@local_function
def sift_bits(bits, conclusives):
    return [bit for bit, conclusive in zip(bits, conclusives) if conclusive]


def b92(alice, bob, n_bits, n_checks, threshold):
    with LocalQuantumBackend():
        # Alice chooses random bits
        a_bits = choose_bits(n_bits@alice)

        # Alice encodes the bits as non-orthogonal qubit states
        qubits = encode_bits(a_bits)

        # Alice sends the non-orthogonal qubit states to Bob
        qubits.send(src=alice, dest=bob)

        # Bob chooses random bases and measures the qubits in them
        b_bases = choose_bases(n_bits@bob)
        conclusives = measure_qubits(qubits, b_bases)

        # Bob infers the correct bit for each conclusive measurement
        b_bits = infer_bits(b_bases, conclusives)

        # Bob shares which bits were conclusive with Alice
        conclusives.send(src=bob, dest=alice)

        # Alice and Bob keep only the conclusively measured bits
        a_keep = sift_bits(a_bits, conclusives)
        b_keep = sift_bits(b_bits, conclusives)

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
    a_key, b_key, a_eve_detected, b_eve_detected = b92(alice, bob, 100, 10, 2)
    print('B92')
    print(a_key, a_eve_detected)
    print(b_key, b_eve_detected)
