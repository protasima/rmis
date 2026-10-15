import numpy as np
import sympy as sp

# 1. Матрица коэффициентов СДУ
A = np.array([
    [-1.0,   0.0,   0.0,   0.0,   0.0,   0.244, 0.84 ],
    [ 0.444, -1.0,   0.0,   0.0,   0.0,   0.122, 0.0  ],
    [ 0.259,  0.0,  -1.0,   0.0,   0.0,   0.073, 0.0  ],
    [ 0.167,  0.0,   0.0,  -1.0,   0.818, 0.561, 0.0  ],
    [ 0.111,  0.0,   0.0,   0.0,  -1.0,   0.0,   0.14 ],
    [ 0.0,    0.808, 0.806, 0.833, 0.0,   -1.0,   0.0  ],
    [ 0.019,  0.192, 0.194, 0.167, 0.182, 0.0,   -1.0 ]
])

# Начальные условия при t = 0 (из вашего условия: p0(0)=1, остальные 0)
t_init = 0
p_init = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

print("Численно находим спектр матрицы системы...")
eigenvalues, eigenvectors = np.linalg.eig(A)

# Находим константы интегрирования С из линейной системы: V * C = p_init
C = np.linalg.solve(eigenvectors, p_init)

# 2. Собираем точные аналитические формулы в SymPy
t = sp.symbols('t', real=True)
analytical_solutions = []

print("Формируем аналитические выражения...")
for i in range(7):
    expr = 0
    for j in range(7):
        lam = eigenvalues[j]
        v_ij = eigenvectors[i, j]
        c_j = C[j]
        
        # Общая формула: C_j * V_ij * e^(lambda_j * t)
        term = c_j * v_ij * sp.exp(lam * t)
        expr += term
    
    # Отбрасываем микроскопические комплексные погрешности float округления (+0.j)
    expr_real = sp.re(expr)
    
    # Округляем коэффициенты до 4 знаков для читаемости
    readable_expr = expr_real.evalf(4)
    analytical_solutions.append(readable_expr)

# 3. Красивый вывод аналитического решения
print("\n" + "="*60)
print("АНАЛИТИЧЕСКОЕ РЕШЕНИЕ СИСТЕМЫ (для t >= 0):")
print("="*60)
for i in range(7):
    compact_expr = analytical_solutions[i].evalf(4)
    print(f"p{i}(t) = {compact_expr}")
    print("-" * 60)