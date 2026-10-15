# основной файл для проведения хакерской атаки
import numpy as np
import solve_nmdq
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# параметры симуляции
t_start = 0
t_end = 20
t_span_normal = (t_start, t_end)
# массив предельных вероятностей из решения СЛАУ
p_limits = np.array([0.1502, 0.1074, 0.0633, 0.2354,
                     0.0281, 0.3338, 0.0818])
# точность совпадения 
epsilon = 0.0001

# момент времени, с которого система стабилизировалась после атаки
t_stab = None
idx_stab = None



# генерируем случайную точку разрыва t*
t_attack = np.random.randint(t_start + 1, 10)
print(f"Случайная точка разрыва t* сгенерирована: {t_attack} ед. вр.")

# РАСЧЕТ ЧИСЛЕННЫХ РЕШЕНИЙ СДУ

# получаем значения СДУ при начальных условиях
# и нормальной работе системы
normal_sol = solve_nmdq.solve_system(t_start, 
                                   [1.0, 0.0, 0.0, 0.0, 
                                    0.0, 0.0, 0.0], 
                                   t_span_normal)

# фиксируем значения вероятностей в точке t_attack
idx = np.where(np.isclose(normal_sol.t, t_attack))[0][0]

p_values_at_t_attack = normal_sol.y[:, idx]
for i in range(7):
    print(f"\tp{i}(t*) = {float(p_values_at_t_attack[i]):.4f};")
else:
    print()

# получаем значения СДУ при начальных условиях
# и атаке на систему, т.е. p0(t*) = 1.0, p1(t*) = 0.0 ...
t_span_attack = (t_attack, t_end)
attack_sol = solve_nmdq.solve_system(t_attack,
                                    [1.0, 0.0, 0.0, 0.0, 
                                     0.0, 0.0, 0.0],
                                     t_span_attack)

# ищем момент времени, с которого система стабилизировалась
for idx in range(len(attack_sol.t)):
    # проверяем абсолютное отклонение всех вероятностей
    current_p = attack_sol.y[:, idx]
    diff = np.abs(current_p - p_limits)

    if np.all(diff < epsilon):
        t_stab = attack_sol.t[idx]
        idx_stab = idx
        break

if t_stab is not None:
    # если за отведенное время система успела стабилизироваться
    delta_t = np.ceil(t_stab) - t_attack
    print(f"Система вышла на предельные вероятности при t = {np.ceil(t_stab)} ед. вр.")
    print(f"Время адаптации после атаки Δt = {delta_t} ед. вр.")
else:
    # если система не успела выйти на режим до конца t_end
    t_stab = attack_sol.t[-1]
    delta_t = np.ceil(t_stab) - t_attack
    print(f"Внимание: система не успела полностью стабилизироваться до t_end! Время: {t_stab} ед. вр. С атаки прошло: {delta_t} ед. вр.")
    # в таком случае, выведем вероятности которые получились при t_stab и предельные
    curr_idx = np.where(np.isclose(attack_sol.t, t_stab))[0][0]
    current_p = attack_sol.y[:, idx]
    print(f"{'Текущие вероятности':<{24}}{'Предельные вероятности':<{25}}{'Разница':<} ")
    for i in range(7):
        p_curr_str = f"{current_p[i]:.4f}"
        p_lim_str = f"{p_limits[i]:.4f}"
        diff_str = f"{np.abs(current_p[i] - p_limits[i]):.4f}"
        print(f"{p_curr_str:<{24}}{p_lim_str:<{25}}{diff_str:<{10}}")

# ЧАСТЬ ОТРИСОВКИ ГРАФИКА И АНИМАЦИИ

# ОБЪЕДИНЕНИЕ ДАННЫХ
# данные нормальной работы включая точку атаки
idx_normal = np.where(normal_sol.t <= t_attack)[0]
t_part1 = normal_sol.t[idx_normal]
y_part1 = normal_sol.y[:, idx_normal]

# данные атаки, исключая t*
idx_attack = np.where(attack_sol.t > t_attack)[0]
t_part2 = attack_sol.t[idx_attack]
y_part2 = attack_sol.y[:, idx_attack]

# точка разрыва в t*
t_nan = np.array([t_attack])
y_nan = np.full((7, 1), np.nan)

# склейка массивов для сквозной анимации
t_all = np.concatenate([t_part1, t_nan, t_part2])
y_all = np.concatenate([y_part1, y_nan, y_part2], axis = 1)
total_frames = len(t_all)

# НАСТРОЙКА ХОЛСТА
fig, ax = plt.subplots(figsize = (12, 7))
ax.set_xlim(t_start, t_end)
ax.set_ylim(0, 1.05)
ax.set_xlabel("Время t", fontsize = 12)
ax.set_ylabel("Вероятности состояний p_i(t)", fontsize = 12)
ax.set_title("Моделирование атаки на систему", fontsize = 14)
ax.grid(True, linestyle = ":", alpha = 0.6)
print(int(np.ceil(t_stab)))
# настройка оси t
base_ticks = list(range(int(t_start), int(t_end) + 1, 2))
if t_attack not in base_ticks: base_ticks.append(t_attack)
if int(np.ceil(t_stab)) not in base_ticks: 
    print('da') 
    base_ticks.append(t_stab)
base_ticks = sorted(base_ticks)
labels = []
for t in base_ticks:
    if t == t_attack:
        labels.append(f"$t^*={t}$")
    elif t == int(np.ceil(t_stab)):
        labels.append(f"$t^'={int(np.ceil(t))}$")
    else:
        labels.append(str(t))
ax.set_xticks(base_ticks)
ax.set_xticklabels(labels)

for tick_label in ax.get_xticklabels():
        if "$t^*" in tick_label.get_text():
            tick_label.set_color('red')
            tick_label.set_fontweight('bold')
        elif "$t^'" in tick_label.get_text():
            tick_label.set_color('green')
            tick_label.set_fontweight('bold')


# линии состояний
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', "#0b6e69", '#e377c2']
lines = []
for i in range(7):
    line, = ax.plot([], [], lw=2, color=colors[i], label=f'p{i}(t)')
    lines.append(line)

# вертикальная линия для отметки момента атаки (изначально невидимая)
v_line_attack = ax.axvline(x = t_attack, color = 'red', linestyle = (0, (10, 15)), lw = 2, alpha = 0.0)

# вертикальная линия для отметки момента стабилизации
v_line_stab = ax.axvline(x = int(np.ceil(t_stab)), color = 'green', linestyle = (0, (10, 15)), lw = 2, alpha = 0.0)

# полигон для закраски области между t_attack и t_stab
span_box = ax.axvspan(t_attack, int(np.ceil(t_stab)), color = 'gray', alpha = 0.0)

ax.legend(loc = 'upper right', bbox_to_anchor = (1.25, 1.0))
plt.tight_layout()

# ФУНКЦИИ ИНИЦИАЛИЗАЦИИ И ОБНОВЛЕНИЯ КАДРА

def init():
    for line in lines:
        line.set_data([], [])
    v_line_attack.set_alpha(0.0)
    v_line_stab.set_alpha(0.0)
    span_box.set_alpha(0.0)

    return lines + [v_line_attack, v_line_stab, span_box] # все изменяемые объекты

# обновление меток на оси для t*, t_stab
def update_axis_labels(show_attack = False, show_stab = False):
    ticks = list(range(int(t_start), int(t_end) + 1, 2))
    labels = [str(t) for t in ticks]

    # если прошли точку атаки, добавить t*
    if show_attack:
        ticks.append(t_attack)
        labels.append(f"$t^*={t_attack}$")

    # если прошли точку восстановления, добавить t_stab
    if show_stab:
        ticks.append(t_stab)
        labels.append(f"$t_{{stab}}={np.ceil(t_stab)}$")

    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)

    for tick_label in ax.get_xticklabels():
        if "$t^*" in tick_label.get_text():
            tick_label.set_color('red')
            tick_label.set_fontweight('bold')
        elif "$t_{stab}" in tick_label.get_text():
            tick_label.set_color('green')
            tick_label.set_fontweight('bold')

def update(frame):

    current_t = t_all[frame]

    # отрисовываем историю от 0 до текущего кадра для всех функций
    for i in range(7):
        lines[i].set_data(t_all[:frame+1], y_all[i, :frame+1])

    # если время дошло до атаки, включаем видимость красного пунктира
    if current_t >= t_attack: 
        v_line_attack.set_alpha(1.0)
    else: v_line_attack.set_alpha(0.0)

    # если время дошло до точки стабилизации, видимость зеленого пунктира
    # и серого выделения
    if current_t >= t_stab:
        v_line_stab.set_alpha(1.0)
        span_box.set_alpha(0.15)
    else:
        v_line_stab.set_alpha(0.0)
        span_box.set_alpha(0.0)


    return lines + [v_line_attack, v_line_stab, span_box]



# ЗАПУСК АНИМАЦИИ
ani = animation.FuncAnimation(
    fig, update, frames = total_frames, init_func=init,
    interval = 10, blit = True, repeat = False)

plt.show()