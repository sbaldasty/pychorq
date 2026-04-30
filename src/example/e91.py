from numpy import pi
from pychor import Party
from pychor import local_function
from example.common import eavesdrop
from pychorq.choreography import LocalQuantumBackend
from pychorq.qubit import Qubit
from pychorq.state import ket_plus
from pychorq.state import ket_zero
from qutip.core.gates import cnot
from qutip.core.gates import ry
from random import choices


# Common angle used for key generation and CHSH test
CA = pi / 2.0

# Angles that only Alice can choose
AA1, AA2 = 0.0, pi / 4.0

# Angles that only Bob can choose
BA1, BA2 = pi / 4.0, 3 * pi / 4.0


@local_function
def entangle_qubits(n):
    bank_1 = [Qubit(ket_plus()) for _ in range(n)]
    bank_2 = [Qubit(ket_zero()) for _ in range(n)]
    for q1, q2 in zip(bank_1, bank_2):
        Qubit.unitary(cnot(), [q1, q2])

    return bank_1, bank_2


@local_function
def choose_angles_set_1(n):
    opts = [AA1, AA2, CA]
    return choices(opts, k=n)


@local_function
def choose_angles_set_2(n):
    opts = [BA1, BA2, CA]
    return choices(opts, k=n)


@local_function
def measure_qubits(qubits, angles):
    for qubit, angle in zip(qubits, angles):
        # Rotate the measurement axis in the X-Z plane
        Qubit.unitary(ry(-2.0 * angle), [qubit])

    return Qubit.measure(qubits)


@local_function
def split_bits(bits, angles1, angles2):
    '''
    Split bits into two lists, one with the bits where the angles matched and
    one with the remaining bits. Also return the angles for the remaining bits
    for doing CHSH.
    '''
    ca = lambda x, y: x == CA and y == CA
    tbl = list(zip(bits, angles1, angles2))
    key_bits = [bit for bit, a1, a2 in tbl if ca(a1, a2)]
    test_bits = [bit for bit, a1, a2 in tbl if not ca(a1, a2)]
    ang1 = [a1 for _, a1, a2 in tbl if not ca(a1, a2)]
    ang2 = [a2 for _, a1, a2 in tbl if not ca(a1, a2)]
    return key_bits, test_bits, ang1, ang2


def correlation(bits1, bits2):
    '''
    Correlation for outcomes mapped as 0 -> +1 and 1 -> -1.
    '''
    if len(bits1) == 0:
        return 0.0

    # Convert bits to +1 and -1 instead of 0 and 1
    mapped = [((1 - 2 * b1), (1 - 2 * b2)) for b1, b2 in zip(bits1, bits2)]
    # Calculate the pairwise average product
    return sum(a * b for a, b in mapped) / len(mapped)


def chsh_value(bits1, bits2, angles1, angles2):
    pairs = {
        (AA1, BA1): ([], []),
        (AA1, BA2): ([], []),
        (AA2, BA1): ([], []),
        (AA2, BA2): ([], []),
    }

    for bit1, bit2, a, b in zip(bits1, bits2, angles1, angles2):
        key = (a, b)
        if key in pairs:
            pairs[key][0].append(bit1)
            pairs[key][1].append(bit2)

    e00 = correlation(*pairs[(AA1, BA1)])
    e01 = correlation(*pairs[(AA1, BA2)])
    e10 = correlation(*pairs[(AA2, BA1)])
    e11 = correlation(*pairs[(AA2, BA2)])

    s = e00 + e01 + e10 - e11
    return abs(s)


@local_function
def eve_detected(bits1, bits2, angles1, angles2):
    s = chsh_value(bits1, bits2, angles1, angles2)
    return s < 2.0


def e91(alice, bob, eve, source, n_bits, pct_eve=0.0):
    with LocalQuantumBackend():
        # Source creates entangled qubits, and sends them to Alice and Bob
        a_qubits, b_qubits = entangle_qubits(n_bits@source).untup(2)
        a_qubits.send(src=source, dest=eve)
        eavesdrop(a_qubits, pct_eve@eve)
        a_qubits.send(src=eve, dest=alice)
        b_qubits.send(src=source, dest=eve)
        eavesdrop(b_qubits, pct_eve@eve)
        b_qubits.send(src=eve, dest=bob)

        # Alice and Bob choose from non-orthogonal measurement bases
        a_angles = choose_angles_set_1(n_bits@alice)
        b_angles = choose_angles_set_2(n_bits@bob)

        # Alice and Bob measure their qubits in the chosen bases
        a_bits = measure_qubits(a_qubits, a_angles)
        b_bits = measure_qubits(b_qubits, b_angles)

        # Alice and Bob reveal their measurement bases
        a_angles.send(src=alice, dest=bob)
        b_angles.send(src=bob, dest=alice)

        # Alice and Bob decide on key bits and bits for Bell test
        a_key, a_test, a_ta1, a_ta2 = split_bits(a_bits, a_angles, b_angles).untup(4)
        b_key, b_test, b_ta1, b_ta2 = split_bits(b_bits, a_angles, b_angles).untup(4)

        # Alice and bob exchange test bits
        a_test.send(src=alice, dest=bob)
        b_test.send(src=bob, dest=alice)

        # Alice and Bob check for eavesdropping using CHSH
        a_eve_detected = eve_detected(a_test, b_test, a_ta1, a_ta2)
        b_eve_detected = eve_detected(a_test, b_test, b_ta1, b_ta2)

        return a_key, b_key, a_eve_detected, b_eve_detected


if __name__ == '__main__':
    alice = Party('alice')
    bob = Party('bob')
    eve = Party('eve')
    source = Party('source')
    a_key, b_key, a_eve_detected, b_eve_detected = e91(alice, bob, eve, source, 150)
    print('E91')
    print(a_key, a_eve_detected)
    print(b_key, b_eve_detected)
