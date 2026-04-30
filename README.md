# pychorq

This package provides a tool for modeling quantum key distribution protocols, and other protocols that call for the transmission of qubits between actors, as choreographies.

## Installation

Manually download for now. The dependencies are listed in `pyproject.toml`. Hopefully this project will be coming soon to `pip`...

## Core architecture

For its choreographic framework, `pychorq` extends `pychor` with a new local quantum backend. The backend supports classical messages in the same way the reference implementation supports sending messages between actors, but it also provides custom ownership logic when the messages are qubits or collections of qubits. In contrast to classical messages whose ownership list grows as they are passed around the network, ownership of quantum messages _transitions_ from actor to actor, because qubits cannot be copied.

For modeling quantum systems, `pychorq` adds a qubit abstraction over the `qutip` quantum simulation library. Each qubit is its own object, and is backed by a quantum system. The backing quantum systems can combine as qubits become entangled, and can factor if qubits are measured. This approach eliminates the need for a single global quantum state, allows actors to add new qubits to a model dynamically, supports the messages-as-objects requirement of choreographic programming, and completely mediates access to quantum state matrixes through the `Qubit` objects.

See `src/pychorq` for the source code.

## Examples

This package includes implementations of three sample quantum key distribution protocols: BB84, B92, and E91.

See `/src/example` for the source code of these examples. See `/src/analysis` for Jupyter notebooks that illustrate their use.
