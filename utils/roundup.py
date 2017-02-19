import random

def uniform4(m, M):
    return random.randint(np.floor(m*1e4), np.ceil(M*1e4))/10000

def float4(x):
    return np.rint(x*1e4)/10000
