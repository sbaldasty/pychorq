from qutip import ket


def ket_zero():
    return ket("0")


def ket_one():
    return ket("1")


def ket_plus():
    return (ket_zero() + ket_one()).unit()
