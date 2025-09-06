#Example: calcular los cuadrados de una lista de números usando multiprocessing

import multiprocessing

def square(x):
    return x * x

if __name__ == '__main__':
    pool = multiprocessing.Pool()
    inputs = [1, 2, 3, 4, 5]
    outputs_async = pool.map_async(square, inputs)
    outputs = outputs_async.get()
    print(outputs)