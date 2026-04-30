from pychor import local_function
from pychorq.qubit import Qubit
from random import choices
from random import sample

@local_function
def choose_bits(n):
    '''
    Choose n random bits.
    '''
    return choices([0, 1], k=n)


@local_function
def choose_indexes(bits, k):
    '''
    Choose k random indexes from the bits, without replacement.
    '''
    return sample(range(len(bits)), k=k)


@local_function
def eavesdrop(qubits, pct):
    '''
    Measure pct percent of the qubits.
    '''
    n_reads = int(len(qubits) * pct)
    peek = sample(qubits, k=n_reads)
    Qubit.measure(peek)

    
@local_function
def split_bits(bits, idxs):
    '''
    Split bits into two lists, one with the bits at the given indexes and one
    with the remaining bits.
    '''
    all_idxs = range(len(bits))
    key_bits = [bits[i] for i in all_idxs if i not in idxs]
    chk_bits = [bits[i] for i in all_idxs if i in idxs]
    return key_bits, chk_bits


@local_function
def eve_detected(bits1, bits2, threshold):
    '''
    Check if the number of differing bits exceeds the given threshold.
    '''
    return sum(bit1 != bit2 for bit1, bit2 in zip(bits1, bits2)) > threshold
