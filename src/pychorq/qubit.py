from itertools import combinations
from networkx import Graph
from networkx import compose_all
from networkx import connected_components
from qutip import Qobj
from qutip import ket
from qutip import qeye
from qutip import tensor
from qutip import expand_operator
from random import random


class QuantumSystem:
    '''
    Stores the state of one or more entangled qubits, and an in-order list of
    the qubits objects the state represents. Not intended for direct use
    outside the framework.
    '''
    def __init__(self, state, qubits, graph):
        assert isinstance(state, Qobj)
        assert isinstance(qubits, list)
        assert isinstance(graph, Graph)
        self.state = state
        self.qubits = qubits
        self.entanglements = graph


class Qubit:
    '''
    Object representing a single qubit. The state of the qubit is stored in a
    QuantumSystem object, which may be shared with other qubits if they are
    entangled.
    '''
    def __init__(self, state):
        '''
        Create a new qubit with its own quantum system in the given state. The
        state should be a normalized ket of length two.
        '''
        assert isinstance(state, Qobj)
        assert state.dims == [[2], [1]]
        graph = Graph()
        graph.add_node(self)
        self.system = QuantumSystem(state.unit(), [self], graph)


    @property
    def index(self):
        '''
        Gets the index of this qubit in its quantum system. Not intended for
        direct use outside the framework.
        '''
        return self.system.qubits.index(self)


    @staticmethod
    def measure(qubits):
        '''
        Measure the given qubits in the computational basis, returning a list
        of bits.
        '''

        # Check qubits is a list of distinct Qubits
        assert isinstance(qubits, list)
        assert all(isinstance(q, Qubit) for q in qubits)
        assert len(set(qubits)) == len(qubits)

        result = []
        for qubit in qubits:
            n = len(qubit.system.qubits)
            i = qubit.index

            def lifted(P):
                ops = [qeye(2)] * n
                ops[i] = P
                return tensor(*ops)

            m0 = lifted(ket("0") * ket("0").dag())
            m1 = lifted(ket("1") * ket("1").dag())

            # Perform the measurement probabilistically
            state = qubit.system.state
            prob_0 = (state.dag() * m0 * state).real
            bit = 0 if random() < prob_0 else 1

            # Measurement becomes part of the result
            result.append(bit)

            # Part of the state collapses
            m = m0 if bit == 0 else m1
            qubit.system.state = (m * state).unit()

            # Identify any groups of qubits now disentangled from the rest
            subsystems = connected_components(qubit.system.entanglements)
            # TODO Figure out how to split the state

        return result


    @staticmethod
    def unitary(unitary, qubits):
        '''
        Apply a unitary to the given qubits, in order.
        '''
        assert isinstance(unitary, Qobj)

        # Check qubits is a non-empty list of distinct Qubits
        assert isinstance(qubits, list)
        assert len(qubits) > 0
        assert all(isinstance(q, Qubit) for q in qubits)
        assert len(set(qubits)) == len(qubits)

        # Combine systems of all involved qubits
        subsystems = list(set(q.system for q in qubits))
        entanglements = compose_all(s.entanglements for s in subsystems)
        entanglements.add_edges_from(combinations(qubits, 2))

        system = QuantumSystem(
            state=tensor(*[s.state for s in subsystems]),
            qubits=[q for s in subsystems for q in s.qubits],
            graph=entanglements)

        for q in system.qubits:
            q.system = system

        # Expand unitary to act on the combined system
        indexes = [system.qubits.index(q) for q in qubits]
        expanded_unitary = expand_operator(unitary, system.state.dims[0], indexes)

        # Act on combined system and normalize
        system.state = (expanded_unitary * system.state).unit()
