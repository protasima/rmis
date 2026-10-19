# основной файл для проведения хакерской атаки
import numpy as np
import solve_nmdq
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime

# параметры симуляции
t_start = 0
t_end = 20
# массив предельных вероятностей из решения СЛАУ
p_limits = np.array([0.1502, 0.1074, 0.0633, 0.2354,
                     0.0281, 0.3338, 0.0818])

p_start_init = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
p_start_error = None 
title = "Моделирование атаки на систему"


# TODO: добавить сохранение результатов в файл в виде форматированного ввода
# текущее состояние - только вывод в консоль
# сохранять: 
# статические параметры симуляции - два начальных состояния, t_start, t_end, epsilon
# динамические параметры симуляции - t*, вероятности в точке t*, t', delta t


# точность совпадения 
epsilon = 0.0001



# добавлены различные варианты симуляции
# выбор в соответствии с вводом пользователя в командную строку
# ввод повторяется до совпадения с конкретным вариантом
# для каждого варианта изменяется только p_start_error
# т.е. начальное состояние системы после атаки
print("Начало работы скрипта. Выберите вариант атаки (режим моделирования):")
print("1. Моделирование DDOS-атаки с полным сбросом системы, p0(t*) = 1.0, pi(t*) = 0.0, i != 0.0;")
print("2. Моделирование DDOS-атаки с частичным восстановлением системы, p0(t*) = 0.3, p4(t*) = 0.7, pi(t*) = 0.0;")
print("3. Моделирование TDOS-атаки (ботнет, искусственное завышение интенсивности входного потока) (1 вариант, p3 = p4 -> max);")
print("4. Моделирование TDOS-атаки (ботнет, искусственное завышение интенсивности входного потока) (2 вариант, p6 -> max).")
print("Выберите пункт для дальнейшей работы: ", end = "")
user_choice: str = None
while user_choice not in ['1', '2', '3', '4']:
    # 1. симуляция DDOS-атаки с полным сбросом системы
    user_choice = input()
    match user_choice:
        case '1': 
            p_start_error = [1.0, 0.0, 0.0, 0.0, 
                                    0.0, 0.0, 0.0]
            # p0(t*) = 1.0, pi(t*) = 0.0, i != 0
            title = "Моделирование DDOS-атаки с полным сбросом системы."
        case '2': 
            # восстанавливается очередь и начальное состояние
            p_start_error = [0.3, 0.0, 0.0, 0.0,
                                   0.7, 0.0, 0.0]
            # p0(t*) = 0.3, p4(t*) = 0.7, pi(t*) = 0.0
            title = "Моделирование DDOS-атаки с полным сбросом системы."
        case '3': 
            # ботнет-атака, макс. загрузка операторов и очереди, маленькая вероятность ошибки 
            p_start_error = [0.0, 0.0, 0.0, 0.45, 
                                    0.45, 0.0, 0.1]
            # p3 = p4 -> max, p6 = 1 - (p3 + p4)
            title = "TDOS-атака (1 вариант, p3 = p4 -> max)."
        case '4': 
            # ботнет-атака, макс. вероятность атаки, нагрузка операторов и очереди
            p_start_error = [0.0, 0.0, 0.0, 0.1,
                                   0.1, 0.0, 0.8]
            # p6 -> max, p3 = p4 = 1/2 (1 - p6)
            title = "TDOS-атака (2 вариант, p6 -> max)."
            # СМ: необходимо увеличить t_end
            t_end = 30
        case '_': print('Не найдено совпадений. Повторите ввод: ', end="")
    



# момент времени, с которого система стабилизировалась после атаки
t_stab = None
idx_stab = None

t_span_normal = (t_start, t_end)
# генерируем случайную точку разрыва t*
t_attack = np.random.randint(t_start + 1, 10)
print(f"Случайная точка разрыва t* сгенерирована: {t_attack} ед. вр.")

# РАСЧЕТ ЧИСЛЕННЫХ РЕШЕНИЙ СДУ

# получаем значения СДУ при начальных условиях
# и нормальной работе системы
normal_sol = solve_nmdq.solve_system(t_start, 
                                   p_start_init, 
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
                                    p_start_error,
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

# вывод для сохранения в файле
record: dict = {
    "static_params": f"Начальное время, t_start: {t_start} ед. вр.\n Конец симуляции, t_end: {t_end} ед. вр.\nТочность совпадения по предельным вероятностям, epsilon: {epsilon}.",
    "dynamic_params": ""} 

now = datetime.now()
p_init_str = "".join(f"\t\tp{i}(0) = {val:.2f}\n" for i, val in enumerate(p_start_init)) #нач. знач. до атаки
p_at_attack_str = "".join(f"\t\tp{i}(t*) = {val:.2f}\n" for i, val in enumerate(p_values_at_t_attack)) #знач. вер. в момент атаки
p_error_str = "".join(f"\t\tp{i}(t*+1) = {val:.2f}\n" for i, val in enumerate(p_start_error)) #нач. знач. после атаки

to_save = (
    f"\n---------------------------------------------\n"
    f"-- Моделирование атаки на систему ({user_choice} вариант). {now.year}-{now.month}-{now.day} {now.hour:02}:{now.minute:02}.\n"
    f"-- Статические параметры симуляции:\n\t* Точка отсчета, t_start: {t_start} ед. вр.\n\t* Конец симуляции, t_end: {t_end} ед. вр.\n\t* Точность совпадения по предельным вероятностям, epsilon: {epsilon}\n"
    f"\t* Начальные условия (значения вероятностей) до момента атаки:\n{p_init_str}"
    f"-- Динамические параметры симуляции:\n\t<- Момент атаки, t*: {t_attack} ед. вр.\n"
    f"\t* Значения вероятностей в момент атаки:\n{p_at_attack_str}"
    f"\t* Начальные условия (значения вероятностей) после момента атаки:\n{p_error_str}"
    f"\t* Момент стабилизации, t_stab: {int(np.ceil(t_stab))} ед. вр.\n\t* Потребовалось для стабилизации, delta_t: {delta_t}\n"
    f"---------------------------------------------\n"
)
with open("results.txt", "+a", encoding="utf-8") as file:
    file.write(to_save)

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
ax.set_title(title, fontsize = 14)
ax.grid(True, linestyle = ":", alpha = 0.6)
# настройка оси t
base_ticks = list(range(int(t_start), int(t_end) + 1, 2))
if t_attack not in base_ticks: base_ticks.append(t_attack)
if int(np.ceil(t_stab)) not in base_ticks: base_ticks.append(int(np.ceil(t_stab)))
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
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', "#245169", '#9467bd', "#0b6e69", '#e377c2']
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
    interval = 1, blit = True, repeat = False)


plt.show()