# тестовый файл для построения графиков
import numpy as np
import solve_nmdq
import matplotlib.pyplot as plt

t_span = (0, 100)
solution = solve_nmdq.solve_system(0, 
                                   [1.0, 0.0, 0.0, 0.0, 
                                    0.0, 0.0, 0.0], 
                                   t_span)
plt.figure(figsize=(12, 6))

t_target = 5.0
idx = np.where(np.isclose(solution.t, t_target))[0][0]

p_values_at_5 = solution.y[:, idx]

for i in range(7):
    print(f"Значения в точке t* = {t_target}: p{i}(t*) = {float(p_values_at_5[i]):.4f};")
else:
    print()

for i in range(7):
    plt.plot(solution.t, solution.y[i], label = f"$p_{i}(t)$", lw = 2)

plt.title("Изменение вероятностей состояний системы во времени",
          fontsize = 14)
plt.xlabel('Время $t$', fontsize = 12)
plt.ylabel('Вероятность состояний $p_i(t)$', fontsize = 12)
plt.grid(True, linestyle = '--', alpha = 0.6)

plt.legend(bbox_to_anchor = (1.02, 1), loc = 'upper left',
           borderaxespad=0, fontsize=11)

plt.xlim(t_span[0], t_span[1])
plt.xticks(np.arange(t_span[0], t_span[1] + 1, step=10))

p_limits = np.array([0.1502, 0.1074, 0.0633, 0.2354,
                     0.0281, 0.3338, 0.0818])
epsilon = 0.0001
t_stab = None
idx_stab = None

for idx in range(len(solution.t)):
    # проверяем абсолютное отклонение всех вероятностей
    current_p = solution.y[:, idx]
    diff = np.abs(current_p - p_limits)

    if np.all(diff < epsilon):
        t_stab = solution.t[idx]
        idx_stab = idx
        break

if t_stab is not None:
    # если за отведенное время система успела стабилизироваться
    delta_t = np.ceil(t_stab)
    print(f"Система вышла на предельные вероятности при t = {np.ceil(t_stab)} ед. вр.")
    print(f"Время адаптации после атаки Δt = {delta_t} ед. вр.")
else:
    # если система не успела выйти на режим до конца t_end
    t_stab = solution.t[-1]
    delta_t = np.ceil(t_stab)
    print(f"Внимание: система не успела полностью стабилизироваться до t_end! Время: {t_stab} ед. вр. С атаки прошло: {delta_t} ед. вр.")
    # в таком случае, выведем вероятности которые получились при t_stab и предельные
    curr_idx = np.where(np.isclose(solution.t, t_stab))[0][0]
    current_p = solution.y[:, idx]
    print(f"{'Текущие вероятности':<{24}}{'Предельные вероятности':<{25}}{'Разница':<} ")
    for i in range(7):
        p_curr_str = f"{current_p[i]:.4f}"
        p_lim_str = f"{p_limits[i]:.4f}"
        diff_str = f"{np.abs(current_p[i] - p_limits[i]):.4f}"
        print(f"{p_curr_str:<{24}}{p_lim_str:<{25}}{diff_str:<{10}}")

plt.tight_layout()
plt.show()

