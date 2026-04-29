from qutip import ket


def bell_state():
    return (ket("00") + ket("11")).unit()


def ket_zero():
    return ket("0")


def ket_one():
    return ket("1")


def ket_plus():
    return (ket_zero() + ket_one()).unit()
