from numpy import pi
from pychor import Party, local_function
from pychorq.qubit import LocalQuantumBackend
from qiskit.circuit import ClassicalRegister
from qiskit.circuit import QuantumCircuit
from qiskit.circuit import QuantumRegister
from qiskit_aer import AerSimulator
from random import choices


@local_function
def entangle_qubits(n):
    alice_qr = QuantumRegister(n, 'alice')
    bob_qr = QuantumRegister(n, 'bob')
    circuit.add_register(alice_qr)
    circuit.add_register(bob_qr)
    for qa, qb in zip(alice_qr, bob_qr):
        circuit.h(qa)
        circuit.cx(qa, qb)

    return alice_qr, bob_qr


@local_function
def choose_angles_set_1(n):
    opts = [0.0, pi / 8.0, pi / 4.0]
    return choices(opts, k=n)


@local_function
def choose_angles_set_2(n):
    opts = [0.0, pi / 8.0, -pi / 8.0]
    return choices(opts, k=n)


@local_function
def measure_qubits(qr, angles):
    # TODO Is this right?
    n = len(angles)
    cr = ClassicalRegister(n)
    circuit.add_register(cr)

    for qubit, angle in zip(qr, angles):
        if angle == pi / 8.0:
            circuit.h(qubit)
        elif angle == -pi / 8.0:
            circuit.sdg(qubit)
            circuit.h(qubit)

    circuit.measure(qr, cr)
    backend = AerSimulator()
    result = backend.run(circuit).result()
    counts = result.get_counts(circuit)
    bits = list(counts.keys())[0]
    bits = bits.split(' ')[-1]
    print(f'bits: {bits}')
    return [int(bit) for bit in bits][::-1]


@local_function
def sift_bits(bits, angles1, angles2):
    tbl = zip(bits, angles1, angles2)
    return [bit for bit, a1, a2 in tbl if a1 == a2]


def e91(alice, bob, n_bits, source):
    with LocalQuantumBackend():
        # Source creates entangled qubits, and sends them to Alice and Bob
        a_qr, b_qr = entangle_qubits(n_bits@source).untup(2)
        a_qr.send(src=source, dest=alice)
        b_qr.send(src=source, dest=bob)

        # Alice and Bob choose from non-orthogonal measurement bases
        a_angles = choose_angles_set_1(n_bits@alice)
        b_angles = choose_angles_set_2(n_bits@bob)

        # Alice and Bob measure their qubits in the chosen bases
        a_bits = measure_qubits(a_qr, a_angles)
        b_bits = measure_qubits(b_qr, b_angles)

        # Alice and Bob reveal their measurement bases
        a_angles.send(src=alice, dest=bob)
        b_angles.send(src=bob, dest=alice)

        # Alice and Bob keep only the bits where their bases matched
        a_key = sift_bits(a_bits, a_angles, b_angles)
        b_key = sift_bits(b_bits, a_angles, b_angles)

        return a_key, b_key


if __name__ == '__main__':
    alice = Party('alice')
    bob = Party('bob')
    source = Party('source')
    circuit = QuantumCircuit()
    a_key, b_key = e91(alice, bob, 50, source)
    print('E91')
    print(a_key)
    print(b_key)
