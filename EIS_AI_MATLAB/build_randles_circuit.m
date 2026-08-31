% Скрипт для EIS сканирования схемы Рэндлса с элементом Варбурга и зависимостью от SOC
clear; clc; close all;

%% ==================== НАСТРОЙКА SOC АККУМУЛЯТОРА ====================
SOC = 1; % Степень заряда батареи в процентах (задайте значение от 0 до 100)
%% ====================================================================

% Проверка корректности ввода SOC
if SOC < 0 || SOC > 100
    error('Значение SOC должно быть в диапазоне от 0% до 100%.');
end

%% 1. Математический расчет параметров схемы в зависимости от SOC
% Номинальные базовые значения (для SOC = 50%)
Rs_base  = 0.020; % 20 мОм
Rct_base = 0.015; % 15 мОм
Cdl_base = 2.5;   % 2.5 Ф

% Моделирование зависимостей (характерных для Li-ion 18650)
soc_frac = SOC / 100; % перевод в доли от 0 до 1

% Rs: стабильно на полке, растет на краях разряда/заряда
Rs_calculated = Rs_base * (1 + 0.3 * (1 - soc_frac)^4 + 0.1 * soc_frac^4);

% Rct: U-образная зависимость (сильный рост при разряде)
Rct_calculated = Rct_base * (1 + 4.5 * (1 - soc_frac)^3 + 0.2 * soc_frac^2);

% Cdl: Перевернутая U-образная зависимость
Cdl_calculated = Cdl_base * (0.6 + 0.4 * sin(pi * soc_frac));

% Масштабирование элементов Варбурга (диффузия ухудшается при разряде ячейки)
warburg_factor = (1 + 3.0 * (1 - soc_frac)^2);
Rw1_calc = 0.005 * warburg_factor;
Cw1_calc = 10    / warburg_factor;
Rw2_calc = 0.010 * warburg_factor;
Cw2_calc = 50    / warburg_factor;
Rw3_calc = 0.025 * warburg_factor;
Cw3_calc = 250   / warburg_factor;

% Вывод рассчитанных параметров в командное окно
fprintf('--- Параметры ячейки 18650 для SOC = %d%% ---\n', SOC);
fprintf('R_solution (Rs):         %.2f мОм\n', Rs_calculated * 1000);
fprintf('R_charge_transfer (Rct): %.2f мОм\n', Rct_calculated * 1000);
fprintf('C_double_layer (Cdl):    %.2f Ф\n', Cdl_calculated);
fprintf('--------------------------------------------\n\n');

%% 2. Создание и настройка модели Simulink
modelName = 'Randles_Warburg_SOC_Automation';
if bdIsLoaded(modelName)
    close_system(modelName, 0); 
end
new_system(modelName);
open_system(modelName);

powerguiBlock = 'powerlib/powergui';
sourceAC      = 'powerlib/Electrical Sources/AC Voltage Source';
rBlock        = 'powerlib/Elements/Series RLC Branch'; 
currentSensor = 'powerlib/Measurements/Current Measurement';
voltageSensor = 'powerlib/Measurements/Voltage Measurement';
toWS          = 'simulink/Sinks/To Workspace';

add_block(powerguiBlock, [modelName, '/powergui']);
add_block(sourceAC,      [modelName, '/EIS_Source'],          'Orientation', 'up');
add_block(currentSensor, [modelName, '/Current_Meas']);
add_block(rBlock,        [modelName, '/R_solution']);
add_block(rBlock,        [modelName, '/R_charge_transfer']);
add_block(rBlock,        [modelName, '/C_double_layer']);

add_block(rBlock, [modelName, '/Rw1']); add_block(rBlock, [modelName, '/Cw1']);
add_block(rBlock, [modelName, '/Rw2']); add_block(rBlock, [modelName, '/Cw2']);
add_block(rBlock, [modelName, '/Rw3']); add_block(rBlock, [modelName, '/Cw3']);
add_block(voltageSensor, [modelName, '/Voltage_Meas']);
add_block(toWS,          [modelName, '/ToWS_V']);
add_block(toWS,          [modelName, '/ToWS_I']);

% Запись динамически вычисленных параметров в блоки Simulink
set_param([modelName, '/R_solution'], 'BranchType', 'R', 'Resistance', num2str(Rs_calculated)); 
set_param([modelName, '/R_charge_transfer'], 'BranchType', 'R', 'Resistance', num2str(Rct_calculated)); 
set_param([modelName, '/C_double_layer'], 'BranchType', 'C', 'Capacitance', num2str(Cdl_calculated)); 

set_param([modelName, '/Rw1'], 'BranchType', 'R', 'Resistance', num2str(Rw1_calc));
set_param([modelName, '/Cw1'], 'BranchType', 'C', 'Capacitance', num2str(Cw1_calc));
set_param([modelName, '/Rw2'], 'BranchType', 'R', 'Resistance', num2str(Rw2_calc));
set_param([modelName, '/Cw2'], 'BranchType', 'C', 'Capacitance', num2str(Cw2_calc));
set_param([modelName, '/Rw3'], 'BranchType', 'R', 'Resistance', num2str(Rw3_calc));
set_param([modelName, '/Cw3'], 'BranchType', 'C', 'Capacitance', num2str(Cw3_calc));

set_param([modelName, '/EIS_Source'], 'Amplitude', '0.005'); 
set_param([modelName, '/ToWS_V'], 'VariableName', 'sim_V', 'SaveFormat', 'Timeseries');
set_param([modelName, '/ToWS_I'], 'VariableName', 'sim_I', 'SaveFormat', 'Timeseries');

%% 3. Соединение линий схемы
add_line(modelName, 'EIS_Source/LConn1', 'Current_Meas/LConn1', 'autorouting', 'on');
add_line(modelName, 'Current_Meas/RConn1', 'R_solution/LConn1', 'autorouting', 'on');
add_line(modelName, 'R_solution/RConn1', 'C_double_layer/LConn1', 'autorouting', 'on');
add_line(modelName, 'R_solution/RConn1', 'R_charge_transfer/LConn1', 'autorouting', 'on');
add_line(modelName, 'R_charge_transfer/RConn1', 'Rw1/LConn1', 'autorouting', 'on');
add_line(modelName, 'R_charge_transfer/RConn1', 'Cw1/LConn1', 'autorouting', 'on');
add_line(modelName, 'Rw1/RConn1', 'Rw2/LConn1', 'autorouting', 'on');
add_line(modelName, 'Cw1/RConn1', 'Rw2/LConn1', 'autorouting', 'on');
add_line(modelName, 'Cw1/RConn1', 'Cw2/LConn1', 'autorouting', 'on');
add_line(modelName, 'Rw2/RConn1', 'Rw3/LConn1', 'autorouting', 'on');
add_line(modelName, 'Cw2/RConn1', 'Rw3/LConn1', 'autorouting', 'on');
add_line(modelName, 'Cw2/RConn1', 'Cw3/LConn1', 'autorouting', 'on');
add_line(modelName, 'C_double_layer/RConn1', 'EIS_Source/RConn1', 'autorouting', 'on');
add_line(modelName, 'Rw3/RConn1', 'EIS_Source/RConn1', 'autorouting', 'on');
add_line(modelName, 'Cw3/RConn1', 'EIS_Source/RConn1', 'autorouting', 'on');
add_line(modelName, 'Current_Meas/RConn1', 'Voltage_Meas/LConn1', 'autorouting', 'on');
add_line(modelName, 'Rw3/RConn1', 'Voltage_Meas/LConn2', 'autorouting', 'on');
add_line(modelName, 'Voltage_Meas/1', 'ToWS_V/1', 'autorouting', 'on');
add_line(modelName, 'Current_Meas/1', 'ToWS_I/1', 'autorouting', 'on');

Simulink.BlockDiagram.arrangeSystem(modelName);

%% 4. Цикл автоматизации по частотам (EIS Свипирование)
frequencies = logspace(log10(0.01), log10(500), 35); 
Z_impedance = zeros(size(frequencies)); 

fprintf('Запуск симуляции EIS...\n');

for k = 1:length(frequencies)
    freq = frequencies(k);
    set_param([modelName, '/EIS_Source'], 'Frequency', num2str(freq));
    
    period = 1 / freq;
    simTime = period * 6; 
    set_param(modelName, 'StopTime', num2str(simTime));
    
    simOut = sim(modelName, 'SimulationMode', 'normal', 'ReturnWorkspaceOutputs', 'on');
    
    t = simOut.sim_V.Time; v = simOut.sim_V.Data; i = simOut.sim_I.Data;
    idx = t > (simTime - period);
    t_last = t(idx); v_last = v(idx); i_last = i(idx);
    
    omega = 2 * pi * freq;
    C_v = sum(v_last .* cos(omega * t_last)) / length(t_last);
    S_v = sum(v_last .* sin(omega * t_last)) / length(t_last);
    C_i = sum(i_last .* cos(omega * t_last)) / length(t_last);
    S_i = sum(i_last .* sin(omega * t_last)) / length(t_last);
    
    Z_impedance(k) = (C_v - 1i*S_v) / (C_i - 1i*S_i);
end
fprintf('Расчет завершен!\n');

%% 5. Построение годографа Найквиста (Nyquist Plot)
figure('Name', sprintf('EIS Nyquist Plot - SOC %d%%', SOC), 'NumberTitle', 'off');
plot(real(Z_impedance)*1000, -imag(Z_impedance)*1000, 'o-', 'LineWidth', 2, 'MarkerFaceColor', 'b');
grid on; hold on;
xlabel('Real Impedance, Z'' (мОм)', 'FontSize', 12);
ylabel('-Imaginary Impedance, -Z'''' (мОм)', 'FontSize', 12);
title(sprintf('Диаграмма Найквиста аккумулятора 18650 (SOC = %d%%)', SOC), 'FontSize', 13);

textPoints = 1:5:35; 
for p = textPoints
    text(real(Z_impedance(p))*1000 + 0.3, -imag(Z_impedance(p))*1000 + 0.3, ...
         [num2str(round(frequencies(p), 2)), ' Гц'], 'FontSize', 9, 'Color', 'r');
end
axis equal;

%% 6. Построение диаграммы Боде (Bode Plot)
Z_magnitude = abs(Z_impedance) * 1000; 
Z_phase = angle(Z_impedance) * (180 / pi);

figure('Name', sprintf('EIS Bode Plot - SOC %d%%', SOC), 'NumberTitle', 'off');

subplot(2, 1, 1);
semilogx(frequencies, Z_magnitude, 's-', 'LineWidth', 2, 'Color', [0 0.5 0]);
grid on;
ylabel('|Z| (мОм)', 'FontSize', 12);
title(sprintf('Диаграмма Боде (SOC = %d%%)', SOC), 'FontSize', 13);

subplot(2, 1, 2);
semilogx(frequencies, Z_phase, '^-', 'LineWidth', 2, 'Color', [0.6 0 0]);
grid on;
xlabel('Частота (Гц)', 'FontSize', 12);
ylabel('Фаза (градусы)', 'FontSize', 12);
