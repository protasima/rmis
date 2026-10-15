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

plt.tight_layout()
plt.show()

