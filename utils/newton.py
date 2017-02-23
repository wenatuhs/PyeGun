import numpy as np
from utils.roundup import float4

def seek_root(x, jacob, options=None):
    """ Seek for the root of a given multi-objection multi-variance function within given accuracy.
    
    Keyword arguments:
    x -- initial guess, np array
    jacob -- function that calculate the value and Jacobian matrix of the function
    options
        err -- target root accuracy
        max_cycle -- [100] cycle limitation
        eta -- [0.5] relax parameter
    
    Returns:
    x -- final root
    y -- final err
    """
    try:
        err = options['err']
        max_cycle = options['max_cycle']
        eta = options['eta']
    except KeyError:
        err = 1e-3
        max_cycle = 100
        eta = 0.5
        print('Error reading options, fallback to default settings!')

    cycle = 0
    while True:
        y, mat = jacob(x)
        print('Cycle {0}: y={1}'.format(cycle, list(y)))

        if not np.sum(np.abs(y) > err):
            print('Succeed! find root in {} cylce(s)!'.format(cycle))
            return x, y

        imat = np.linalg.inv(mat)
        dx = np.dot(y, imat.transpose())
        _x = float4(x-eta*dx)  # next guess

        if np.array_equal(_x, x):
            print('The local best solution has been achieved in cycle {}, \
                however it does not satisfy the accuracy requirements.'.format(cycle))
            return x, y

        if cycle >= max_cycle:
            print('Sorry, can not find solutions with \
                good enough accuracy in {} cycles!'.format(max_cycle))
            return x, y
        
        x = _x
        cycle += 1
        