from numpy import pi
from pychor import Party, local_function
from pychorq.choreography import LocalQuantumBackend
from pychorq.qubit import Qubit
from pychorq.state import ket_plus
from pychorq.state import ket_zero
from qutip.core.gates import cnot
from random import choices


@local_function
def entangle_qubits(n):
    bank_1 = [Qubit(ket_zero()) for _ in range(n)]
    bank_2 = [Qubit(ket_plus()) for _ in range(n)]
    for q1, q2 in zip(bank_1, bank_2):
        Qubit.unitary(cnot(), [q1, q2])

    return bank_1, bank_2


@local_function
def choose_angles_set_1(n):
    opts = [0.0, pi / 8.0, pi / 4.0]
    return choices(opts, k=n)


@local_function
def choose_angles_set_2(n):
    opts = [0.0, pi / 8.0, -pi / 8.0]
    return choices(opts, k=n)


@local_function
def measure_qubits(qubits, angles):
    # TODO Is this right?
    n = len(angles)

    for qubit, angle in zip(qr, angles):
        if angle == pi / 8.0:
            circuit.h(qubit)
        elif angle == -pi / 8.0:
            circuit.sdg(qubit)
            circuit.h(qubit)

    return Qubit.measure(qubits)


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
    a_key, b_key = e91(alice, bob, 50, source)
    print('E91')
    print(a_key)
    print(b_key)
