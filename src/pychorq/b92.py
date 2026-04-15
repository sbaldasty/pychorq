from pychor import Party, local_function
from pychorq.core import LocalQuantumBackend
from qiskit.circuit import ClassicalRegister
from qiskit.circuit import QuantumCircuit
from qiskit.circuit import QuantumRegister
from qiskit_aer import AerSimulator
from random import choices


@local_function
def choose_bits(n):
    return choices([0, 1], k=n)


@local_function
def encode_bits(bits):
    qr = QuantumRegister(len(bits), 'q')
    circuit.add_register(qr)

    for i, bit in enumerate(bits):
        if bit == 1:
            circuit.h(qr[i])

    return qr


@local_function
def choose_bases(n):
    return choices(['X', 'Z'], k=n)


@local_function
def measure_qubits(qr, bases):
    n = len(bases)
    cr = ClassicalRegister(n)
    circuit.add_register(cr)

    for i, basis in enumerate(bases):
        if basis == 'X':
            circuit.h(qr[i])

    circuit.measure(qr, cr)
    backend = AerSimulator()
    result = backend.run(circuit).result()
    counts = result.get_counts(circuit)
    bits = list(counts.keys())[0]
    return [int(bit) for bit in bits][::-1]


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
    circuit = QuantumCircuit()
    a_key, b_key = b92(alice, bob, 20)
    print('B92')
    print(a_key)
    print(b_key)
