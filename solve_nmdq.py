# файл для решения дифференциальных уравнений при заданных начальных условиях
# численное решение СДУ при заданных начальных условиях


import numpy as np
from scipy.integrate import solve_ivp

# определение системы дифференциальных уравнений
def system(t, p):
    p0, p1, p2, p3, p4, p5, p6 = p

    dp0_dt = 0.84 * p6 + 0.244 * p5 - p0
    dp1_dt = 0.444 * p0 + 0.122 * p5 - p1
    dp2_dt = 0.259 * p0 + 0.073 * p5 - p2
    dp3_dt = 0.167 * p0 + 0.818 * p4 + 0.561 * p5 - p3
    dp4_dt = 0.111 * p0 + 0.14 * p6 - p4
    dp5_dt = 0.808 * p1 + 0.806 * p2 + 0.833 * p3 - p5
    dp6_dt = -(dp0_dt + dp1_dt + dp2_dt + dp3_dt + dp4_dt + dp5_dt)

    return [dp0_dt, dp1_dt, dp2_dt, dp3_dt, dp4_dt, dp5_dt, dp6_dt]

# численное решение системы дифференциальных уравнений
# t_start - исходное время отсчета
# p_start - начальные условия
# t_span - пределы интегрирования обычно (t_start, t_end)
def solve_system(t_start: int | float, 
                 p_start: list[float],  
                 t_span: tuple):
    """
    для изменения СДУ изменить функцию system(t, p)

    начальные условия задаются массивом: 
    [p0(t0), p1(t0), ...]

    t_start = t0 - начальный момент
        p0(0) -> t_start = 0
        p0(4) -> t_start = 4 и т.д.
    
    t_span = (t_start*, t_end) - пределы интегрирования
    есть ли смысл интегрировать не от t_start? маловероятно...

    method - меняйте только если знаете зачем 
    """
    # t_eval = np.linspace(t_span[0], t_span[1], 1000)
    
    # новый вариант расчета t_eval
    smooth_grid = np.linspace(t_span[0], t_span[1], 1000)

    start_ceil = int(np.ceil(t_span[0]))
    end_floor = int(np.floor(t_span[1]))
    integer_grid = np.arange(start_ceil, end_floor + 1, dtype = float)

    t_eval = np.union1d(smooth_grid, integer_grid)
    
    solution = solve_ivp(system, t_span, 
                         p_start,
                         t_eval = t_eval,
                         method = 'Radau')
    return solution

if __name__ == "__main__":
    solution = solve_system(0, [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], (0, 100))
    print(solution.y)
