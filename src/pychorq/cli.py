from pychor import Party
from pychor import locally
from pychorq.core import LocalQuantumBackend
from pytest import raises
from qiskit.circuit import QuantumRegister
from qiskit.circuit.library import HGate, Measure
from qiskit import QuantumCircuit, ClassicalRegister


def main() -> None:
    alice = Party('Alice')
    bob = Party('Bob')
    with LocalQuantumBackend():
        # Alice prepares a qubit in the |+> state and sends it to Bob
        qubit = QuantumRegister(1, "q")
        # loc_q = qubit@alice
        # loc_q.send(src=alice, dest=bob)

        # # Bob measures the qubit in the X basis
        # def measure_in_x_basis(q):
        #     qc = QuantumCircuit(1, 1)
        #     qc.append(HGate(), [0])
        #     qc.append(Measure(), [0], [0])
        #     return qc

        # measurement = locally(measure_in_x_basis, loc_q)
        # print(f'Bob measured: {measurement.val}')
    print("Hello, world from pychorq!")


if __name__ == "__main__":
    main()
