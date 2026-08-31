% Скрипт для автоматического EIS сканирования схемы Рэндлса с элементом Варбурга
clear; clc; close all;

%% 1. Создание и настройка модели
modelName = 'Randles_Warburg_Automation';
if bdIsLoaded(modelName)
    close_system(modelName, 0); 
end
new_system(modelName);
open_system(modelName);

% Пути к базовым блокам Specialized Power Systems
powerguiBlock = 'powerlib/powergui';
sourceAC      = 'powerlib/Electrical Sources/AC Voltage Source';
rBlock        = 'powerlib/Elements/Series RLC Branch'; 
currentSensor = 'powerlib/Measurements/Current Measurement';
voltageSensor = 'powerlib/Measurements/Voltage Measurement';
toWS          = 'simulink/Sinks/To Workspace';

% Добавление основных блоков цепи Рэндлса
add_block(powerguiBlock, [modelName, '/powergui']);
add_block(sourceAC,      [modelName, '/EIS_Source'],          'Orientation', 'up');
add_block(currentSensor, [modelName, '/Current_Meas']);
add_block(rBlock,        [modelName, '/R_solution']);
add_block(rBlock,        [modelName, '/R_charge_transfer']);
add_block(rBlock,        [modelName, '/C_double_layer']);

% Добавление блоков для аппроксимации элемента Варбурга (3 RC-цепочки)
add_block(rBlock, [modelName, '/Rw1']); add_block(rBlock, [modelName, '/Cw1']);
add_block(rBlock, [modelName, '/Rw2']); add_block(rBlock, [modelName, '/Cw2']);
add_block(rBlock, [modelName, '/Rw3']); add_block(rBlock, [modelName, '/Cw3']);

% Добавление измерителя напряжения
add_block(voltageSensor, [modelName, '/Voltage_Meas']);

% Добавление блоков вывода в Workspace
add_block(toWS, [modelName, '/ToWS_V']);
add_block(toWS, [modelName, '/ToWS_I']);

%% 2. Настройка параметров элементов под Li-ion 18650
set_param([modelName, '/R_solution'], 'BranchType', 'R', 'Resistance', '0.020'); 
set_param([modelName, '/R_charge_transfer'], 'BranchType', 'R', 'Resistance', '0.015'); 
set_param([modelName, '/C_double_layer'], 'BranchType', 'C', 'Capacitance', '2.5'); 

% Параметры лестничной цепи Варбурга (распределенная диффузия аккумулятора)
set_param([modelName, '/Rw1'], 'BranchType', 'R', 'Resistance', '0.005');
set_param([modelName, '/Cw1'], 'BranchType', 'C', 'Capacitance', '10');
set_param([modelName, '/Rw2'], 'BranchType', 'R', 'Resistance', '0.010');
set_param([modelName, '/Cw2'], 'BranchType', 'C', 'Capacitance', '50');
set_param([modelName, '/Rw3'], 'BranchType', 'R', 'Resistance', '0.025');
set_param([modelName, '/Cw3'], 'BranchType', 'C', 'Capacitance', '250');

% Тестовый сигнал и выводы данных
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

%% 4. Цикл автоматизации по частотам
frequencies = logspace(log10(0.01), log10(500), 35); 
Z_impedance = zeros(size(frequencies)); 

fprintf('Запуск EIS симуляции (Рэндлс + Варбург) для 18650...\n');

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
    fprintf('Частота: %6.3f Гц | Z = %6.2f + j(%6.2f) мОм\n', freq, real(Z_impedance(k))*1000, imag(Z_impedance(k))*1000);
end

%% 5. Построение годографа Найквиста (Nyquist Plot)
figure('Name', 'EIS Nyquist Plot with Warburg Element', 'NumberTitle', 'off');
plot(real(Z_impedance)*1000, -imag(Z_impedance)*1000, 'o-', 'LineWidth', 2, 'MarkerFaceColor', 'b');
grid on; hold on;
xlabel('Real Impedance, Z'' (мОм)', 'FontSize', 12);
ylabel('-Imaginary Impedance, -Z'''' (мОм)', 'FontSize', 12);
title('Диаграмма Найквиста: Модель Рэндлса + Элемент Варбурга', 'FontSize', 14);

textPoints = 1:5:35; 
for p = textPoints
    text(real(Z_impedance(p))*1000 + 0.3, -imag(Z_impedance(p))*1000 + 0.3, ...
         [num2str(round(frequencies(p), 2)), ' Гц'], 'FontSize', 9, 'Color', 'r');
end
axis equal;

%% 6. Построение диаграммы Боде (Bode Plot)
% Вычисление модуля (в мОм) и фазы (в градусах)
Z_magnitude = abs(Z_impedance) * 1000; 
Z_phase = angle(Z_impedance) * (180 / pi);

figure('Name', 'EIS Bode Plot - Li-ion 18650', 'NumberTitle', 'off');

% Верхний график: Амплитудно-частотная характеристика (АЧХ)
subplot(2, 1, 1);
semilogx(frequencies, Z_magnitude, 's-', 'LineWidth', 2, 'Color', [0 0.5 0]);
grid on;
ylabel('|Z| (мОм)', 'FontSize', 12);
title('Диаграмма Боде для импеданса аккумулятора 18650', 'FontSize', 14);

% Нижний график: Фазочастотная характеристика (ФЧХ)
subplot(2, 1, 2);
semilogx(frequencies, Z_phase, '^-', 'LineWidth', 2, 'Color', [0.6 0 0]);
grid on;
xlabel('Частота (Гц)', 'FontSize', 12);
ylabel('Фаза (градусы)', 'FontSize', 12);
