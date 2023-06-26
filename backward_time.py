from scipy.optimize import fsolve
# from sympy import *
import numpy as np
import multiprocessing as mp
import p_tqdm


def f(x, *vars):
    a, x_n_1 = vars
    return a * np.sin(x) * (1 - np.power(x, 2)) - 1 - x_n_1


def solve(args):
    aas = args[0]
    arr_shape = args[1]
    offset = args[2]
    # print(arr_shape)
    backward_steps = 300
    xxs = args[3]
    x0s = args[4]
    sol = np.zeros(arr_shape)
    sol_flag = np.zeros(arr_shape)
    for i, a in enumerate(aas):
        # print("i=", i, " a=:", a)
        for j, x_n_1 in enumerate(xxs):
            # print(j)
            x = x_n_1
            for t in range(backward_steps):
                for x0 in np.random.permutation(x0s):
                    # np.repeat(x0, aas.shape[0])
                    [_x, fval, exitflag, output] = fsolve(f, x0, (a, x), full_output=True)
                    if exitflag == 1:
                        sol_flag[j, i+offset] = 1
                        x = _x
                        break
            # print(i, j)
            sol[j, i+offset] = x
    return (sol, sol_flag)

def multi_process():
    num_of_processes = 12
    chunk_size = int(aas.shape[0] / num_of_processes)
    chunks = [[aas[i:i + chunk_size], x_grid.shape, j*chunk_size, xxs, x0s] for j, i in enumerate(range(0, aas.shape[0], chunk_size))]
    pool = mp.Pool(processes=num_of_processes)
    test = np.array(pool.map(solve, chunks))
    results = test[:, 0, ...]
    flags = test[:, 1, ...]
    # results, flags = pool.map(solve, chunks)
    results = np.array(results)
    flags = np.array(flags)
    final_result = np.zeros(results[0].shape)
    final_flag = np.zeros(flags[0].shape)
    for i in range(results.shape[0]):
        final_result = np.add(final_result, results[i])
        final_flag = np.add(final_flag , flags[i])
    # print(final_flag)
    print(final_flag.size - np.sum(final_flag))
    coordinates = np.zeros(2 * a_grid.size)
    coordinates[::2] = a_grid.reshape(1, -1)
    coordinates[1::2] = final_result.reshape(-1)
    np.save("coordinates3", coordinates)

if __name__ == '__main__':
    xxs = np.linspace(-6, 6, 80)
    aas = np.linspace(-4, 4, 1000)
    print(aas)
    x0s = np.array([0.4, -0.4, 2.3, -2.3, 5, -5, 7, -7])

    # a = 0.514
    # x_n_1 = 0
    # for x_n_1 in xxs:
    a_grid, x_grid = np.meshgrid(aas, xxs)
    print("x_grid: ", '\n', x_grid.shape, a_grid.shape, '\n')

    # sol[:, 0] = aas
    multi_process()

    # print(sol_flag.size - np.sum(sol_flag))
    # coordinates = np.zeros(2 * a_grid.size)
    # coordinates[::2] = a_grid.reshape(1, -1)
    # coordinates[1::2] = sol.reshape(-1)
    # np.save("coordinates3", coordinates)
    # print(coordinates)
