% Моделирование схемы Рэндлса для Li-ion аккумулятора + генерация в Simulink
clear; clc; close all;

%% 1. Исходные параметры схемы Рэндлса
Rs  = 0.025;      % Внутреннее омическое сопротивление (Ом)
Rct = 0.045;      % Сопротивление переносу заряда (Ом)
Cdl = 1.2;        % Емкость двойного электрического слоя (Фарад)
Aw  = 0.015;      % Коэффициент Варбурга (Ом * c^-0.5)

%% 2. Задание диапазона частот и расчет аналитического импеданса
f = logspace(-2, 4, 500); % От 0.01 Гц до 10 000 Гц (500 точек)
omega = 2 * pi * f;       % Угловая частота (рад/с)

% Расчет импеданса компонентов
Zw = Aw * (1 - 1j) ./ sqrt(omega); % Zw = Aw .^ (1 - 1j) ./ sqrt(omega); 
Z_branch = Rct + Zw;
Z_Cdl = 1 ./ (1j * omega * Cdl);

% Полный импеданс схемы: Rs + (Cdl || (Rct + Zw))
Z_tot = Rs + (Z_Cdl .* Z_branch) ./ (Z_Cdl + Z_branch);

Real_Z = real(Z_tot);
Imag_Z = imag(Z_tot);

%% 3. Построение годографа импеданса (Диаграмма Найквиста)
figure('Color', 'w'); 
plot(Real_Z, -Imag_Z, 'LineWidth', 2.5, 'Color', [0 0.4470 0.7410]);
hold on;

% Выделение ключевых точек (маркеры частоты)
f_markers = [0.1, 1, 10, 100, 1000];
colors = ['r', 'g', 'm', 'c', 'k'];
for i = 1:length(f_markers)
    [~, idx] = min(abs(f - f_markers(i)));
    plot(Real_Z(idx), -Imag_Z(idx), [colors(i) 'o'], 'MarkerFaceColor', colors(i), 'MarkerSize', 8);
end

grid on;
axis equal; 
xlim([0, max(Real_Z)*1.1]);
ylim([0, max(-Imag_Z)*1.1]);
xlabel('Действительное сопротивление Z'' (\Omega)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('-Мнимая часть Z'''' (\Omega)', 'FontSize', 11, 'FontWeight', 'bold');
title('Диаграмма Найквиста: Схема Рэндлса для Li-ion', 'FontSize', 12, 'FontWeight', 'bold');

legend_labels = cell(1, length(f_markers)+1);
legend_labels{1} = 'Модель Рэндлса';
for i = 1:length(f_markers)
    legend_labels{i+1} = sprintf('f = %.1f Гц', f_markers(i));
end
legend(legend_labels, 'Location', 'NorthWest');

%% 4. Математическая аппроксимация Варбурга для Simulink
% Так как Simulink работает во временной/s-области, идеальный сдвиг фазы 45 градусов 
% элемента 1/sqrt(s) аппроксимируется эквивалентной передаточной функцией.
num_W = [Aw]; 
den_W = [1, 0.5]; % Базовая low-frequency аппроксимация диффузии

%% 5. Автоматическое создание модели в Simulink
model_name = 'Randles_Simulink_Standard';

% Перезапись модели, если она была открыта
if bdIsLoaded(model_name)
    close_system(model_name, 0);
end

new_system(model_name);
open_system(model_name);

% Определение путей к стандартным блокам библиотеки Simulink
source_blk = 'simulink/Sources/Sine Wave';
gain_blk   = 'simulink/Math Operations/Gain';
sum_blk    = 'simulink/Math Operations/Sum';
tf_blk     = 'simulink/Continuous/Transfer Fcn';
scope_blk  = 'simulink/Sinks/Scope';

% Добавление блоков на холст [лево, верх, право, низ]
add_block(source_blk, [model_name '/Current_Input'],  'Position', [50,  100,  90,  130]);
add_block(gain_blk,   [model_name '/Rs_Gain'],        'Position', [150,  55, 200,  85]);
add_block(sum_blk,    [model_name '/Sum_Z_branch'],   'Position', [150, 140, 180, 170]);
add_block(tf_blk,     [model_name '/Warburg_TF'],     'Position', [220, 140, 300, 170]);
add_block(sum_blk,    [model_name '/Feedback_Sum'],   'Position', [350, 135, 380, 195]);
add_block(tf_blk,     [model_name '/Cdl_Integrator'], 'Position', [420, 150, 500, 180]);
add_block(sum_blk,    [model_name '/Total_Voltage'],  'Position', [560,  95, 590, 135]);
add_block(scope_blk,  [model_name '/Scope_V_Out'],    'Position', [640, 100, 680, 130]);

%% 6. Программное конфигурирование параметров блоков
% Тестовый входной гармонический ток I(t)
set_param([model_name '/Current_Input'], 'Amplitude', '1.0', 'Frequency', '2*pi*1');

% Омическое сопротивление
set_param([model_name '/Rs_Gain'], 'Gain', num2str(Rs));

% Ветвь переноса заряда (Rct + Zw): смещение сумматором на константу Rct
set_param([model_name '/Sum_Z_branch'], 'Inputs', '+');
% Настройка числителя и знаменателя звена Варбурга
set_param([model_name '/Warburg_TF'], 'Numerator', ['[' num2str(num_W) ']'], 'Denominator', ['[' num2str(den_W) ']']);

% Реализация параллельного участка (Cdl || (Rct + Zw)) через контур обратной связи:
% Напряжение U_p = Integral( (I_in - U_p/(Rct+Zw)) / Cdl )
set_param([model_name '/Feedback_Sum'], 'Inputs', '+-');
set_param([model_name '/Cdl_Integrator'], 'Numerator', '1', 'Denominator', ['[' num2str(Cdl) ' 0]']);

% Финальный сумматор полного напряжения: U(t) = I*Rs + U_p
set_param([model_name '/Total_Voltage'], 'Inputs', '++');

%% 7. Прокладка сигнальных линий (Соединения)
% Входной ток разветвляется на Rs и на параллельную структуру
add_line(model_name, 'Current_Input/1', 'Rs_Gain/1', 'autorouting', 'on');
add_line(model_name, 'Current_Input/1', 'Feedback_Sum/1', 'autorouting', 'on');

% Линия через Rs на финальный сумматор
add_line(model_name, 'Rs_Gain/1', 'Total_Voltage/1', 'autorouting', 'on');

% Обратная связь параллельной цепи: Напряжение делится на (Rct + Zw)
add_line(model_name, 'Cdl_Integrator/1', 'Sum_Z_branch/1', 'autorouting', 'on');
add_line(model_name, 'Sum_Z_branch/1', 'Warburg_TF/1', 'autorouting', 'on');

% Выход импеданса ветви заводится на отрицательный вход обратной связи
add_line(model_name, 'Warburg_TF/1', 'Feedback_Sum/2', 'autorouting', 'on');

% Прямая связь от сумматора токов к интегратору емкости Cdl
add_line(model_name, 'Feedback_Sum/1', 'Cdl_Integrator/1', 'autorouting', 'on');

% Напряжение параллельного участка идет на финальный сумматор
add_line(model_name, 'Cdl_Integrator/1', 'Total_Voltage/2', 'autorouting', 'on');

% Вывод общего напряжения на осциллограф
add_line(model_name, 'Total_Voltage/1', 'Scope_V_Out/1', 'autorouting', 'on');

%% 8. Сохранение системы
set_param(model_name, 'ZoomFactor', '100');
save_system(model_name);

disp('Расчет окончен. График Найквиста построен. Модель Simulink успешно сгенерирована!');
