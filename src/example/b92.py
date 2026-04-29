from pychor import Party, local_function
from pychorq.choreography import LocalQuantumBackend
from pychorq.qubit import Qubit
from qutip import ket
from qutip.core.gates import hadamard_transform
from qutip import sigmaz
from random import choices


def ket_plus():
    return (ket("0") + ket("1")).unit()


@local_function
def choose_bits(n):
    return choices([0, 1], k=n)


@local_function
def encode_bits(bits):
    return [Qubit(ket("0") if bit == 0 else ket_plus()) for bit in bits]


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


def b92(alice, bob, n_bits):
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
        a_key = sift_bits(a_bits, conclusives)
        b_key = sift_bits(b_bits, conclusives)

        return a_key, b_key


if __name__ == '__main__':
    alice = Party('alice')
    bob = Party('bob')
    a_key, b_key = b92(alice, bob, 50)
    print('B92')
    print(a_key)
    print(b_key)
