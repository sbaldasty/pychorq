from pychor import Party, local_function
from pychorq.qubit import KET_ONE, KET_ZERO, LocalQuantumBackend
from pychorq.qubit import Qubit
from qiskit.circuit import ClassicalRegister
from qiskit.circuit import QuantumCircuit
from qiskit.circuit import QuantumRegister
from qiskit_aer import AerSimulator
from random import choices


@local_function
def choose_bits(n):
    return choices([0, 1], k=n)


@local_function
def choose_bases(n):
    return choices(['X', 'Z'], k=n)


@local_function
def set_qubits(bits, bases):
    qubits = [Qubit(KET_ZERO if bit == 0 else KET_ONE) for bit in bits]
    qr = QuantumRegister(len(bits), 'q')
    circuit.add_register(qr)

    for i, (bit, basis) in enumerate(zip(bits, bases)):
        if bit == 1:
            circuit.x(qr[i])
        if basis == 'X':
            circuit.h(qr[i])

    return qr


@local_function
def measure_qubits(qr, bases):
    n = len(bases)
    cr = ClassicalRegister(n)
    circuit.add_register(cr)

    for qubit, basis in zip(qr, bases):
        if basis == 'X':
            circuit.h(qubit)

    circuit.measure(range(n), range(n))
    backend = AerSimulator()
    result = backend.run(circuit).result()
    counts = result.get_counts(circuit)
    bits = list(counts.keys())[0]
    return [int(bit) for bit in bits][::-1]


@local_function
def sift_bits(bits, bases1, bases2):
    tbl = zip(bits, bases1, bases2)
    return [bit for bit, b1, b2 in tbl if b1 == b2]


def bb84(alice, bob, n_bits):
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
        a_key = sift_bits(a_bits, a_bases, b_bases)
        b_key = sift_bits(b_bits, a_bases, b_bases)

        return a_key, b_key


if __name__ == '__main__':
    alice = Party('alice')
    bob = Party('bob')
    circuit = QuantumCircuit()
    a_key, b_key = bb84(alice, bob, 20)
    print('BB84')
    print(a_key)
    print(b_key)
