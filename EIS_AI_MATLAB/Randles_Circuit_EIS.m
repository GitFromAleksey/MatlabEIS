% Моделирование схемы Рэндлса для Li-ion 18650: Диаграмма Найквиста и График Боде
clear; clc; close all;

%% 1. Задание массива степеней заряда (SOC)
SOC_array = [1.0, 0.5, 0.2, 0.05]; 

%% 2. Задание диапазона частот
f = logspace(-2, 4, 500); % От 0.01 Гц до 10 000 Гц
omega = 2 * pi * f;       

%% 3. Физические константы ячейки 18650 при SOC = 50%
Rs_base  = 0.018; 
Rct_base = 0.022;
Cdl_base = 2.5;
Aw_base  = 0.008;

colors_matrix = lines(length(SOC_array)); 
legend_labels = cell(1, length(SOC_array));

% Выделяем память под графические элементы для легенд
lines_magnitude = cell(1, length(SOC_array));
max_Real_Z = 0; 

%% ========================================================================
%% ГРАФИК 1: СЕМЕЙСТВО ДИАГРАММ НАЙКВИСТА
%% ========================================================================
figure(1);
set(gcf, 'Color', 'w'); 
hold on;
grid on;

for k = 1:length(SOC_array)
    SOC = SOC_array(k);
    
    % Зависимость параметров от SOC
    Rs  = Rs_base * (1 + 0.15 * (1 - SOC)^4); 
    Rct = Rct_base * (1 + 0.5 * (SOC - 0.5)^2 + 2.5 * exp(-15 * SOC)); 
    Cdl = Cdl_base * (1 - 0.2 * (SOC - 0.5)^2);
    Aw  = Aw_base * (1 + 1.8 * exp(-10 * SOC));
    
    % Расчет комплексного импеданса
    Zw = Aw * (1 - 1j) ./ sqrt(omega); 
    Z_branch = Rct + Zw;
    Z_Cdl = 1 ./ (1j * omega * Cdl);
    Z_tot = Rs + (Z_Cdl .* Z_branch) ./ (Z_Cdl + Z_branch);
    
    Real_Z = real(Z_tot);
    Imag_Z = imag(Z_tot);
    max_Real_Z = max(max_Real_Z, max(Real_Z));
    
    % Годограф импеданса
    plot(Real_Z, -Imag_Z, 'LineWidth', 2.5, 'Color', colors_matrix(k,:));
    
    % Исправлено: Явное задание маркеров частоты без использования квадратных скобок
    f_marker_1 = 1.0;
    f_marker_2 = 100.0;
    
    [~, idx1] = min(abs(f - f_marker_1));
    plot(Real_Z(idx1), -Imag_Z(idx1), 'o', 'MarkerFaceColor', colors_matrix(k,:), 'MarkerEdgeColor', 'k', 'MarkerSize', 6);
    
    [~, idx2] = min(abs(f - f_marker_2));
    plot(Real_Z(idx2), -Imag_Z(idx2), 's', 'MarkerFaceColor', colors_matrix(k,:), 'MarkerEdgeColor', 'k', 'MarkerSize', 6);
    
    legend_labels{k} = sprintf('SOC = %.0f%%', SOC*100);
end

% Оформление графика Найквиста
axis equal; 
xlim([0, max_Real_Z * 1.05]);
ylim([0, max_Real_Z * 0.6]); 
xlabel('Действительное сопротивление Z'' (\Omega)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('-Мнимая часть Z'''' (\Omega)', 'FontSize', 11, 'FontWeight', 'bold');
title('Диаграммы Найквиста в зависимости от SOC', 'FontSize', 12, 'FontWeight', 'bold');
legend(legend_labels, 'Location', 'NorthWest');
ax1 = gca; ax1.Box = 'on'; ax1.LineWidth = 1.2;

%% ========================================================================
%% ГРАФИК 2: СОВМЕЩЕННЫЙ ГРАФИК БОДЕ
%% ========================================================================
figure(2);
set(gcf, 'Color', 'w'); 
grid on;
hold on;

for k = 1:length(SOC_array)
    SOC = SOC_array(k);
    
    % Повторный расчет параметров для графика Боде
    Rs  = Rs_base * (1 + 0.15 * (1 - SOC)^4); 
    Rct = Rct_base * (1 + 0.5 * (SOC - 0.5)^2 + 2.5 * exp(-15 * SOC)); 
    Cdl = Cdl_base * (1 - 0.2 * (SOC - 0.5)^2);
    Aw  = Aw_base * (1 + 1.8 * exp(-10 * SOC));
    
    Zw = Aw * (1 - 1j) ./ sqrt(omega); 
    Z_branch = Rct + Zw;
    Z_Cdl = 1 ./ (1j * omega * Cdl);
    Z_tot = Rs + (Z_Cdl .* Z_branch) ./ (Z_Cdl + Z_branch);
    
    % Амплитуда и Фаза
    Z_magnitude = abs(Z_tot);          
    Z_phase = angle(Z_tot) * (180/pi); 
    
    % Левая ось Y: Модуль импеданса (Сплошная линия)
    yyaxis left
    lines_magnitude{k} = semilogx(f, Z_magnitude, 'LineWidth', 2.5, 'Color', colors_matrix(k,:));
    hold on;
    
    % Правая ось Y: Фазовый сдвиг (Пунктирная линия)
    yyaxis right
    semilogx(f, Z_phase, '--', 'LineWidth', 1.8, 'Color', colors_matrix(k,:));
    hold on;
end

% Оформление графика Боде
yyaxis left
ylabel('Модуль импеданса |Z| (\Omega)', 'FontSize', 11, 'FontWeight', 'bold');
ylim([0, max(Z_magnitude)*1.2]);
ax2 = gca; ax2.YColor = [0.15 0.15 0.15];

yyaxis right
ylabel('Фазовый сдвиг \phi (градусы \circ)', 'FontSize', 11, 'FontWeight', 'bold');
ylim([-50, 10]);
ax2.YColor = [0.15 0.15 0.15];

set(gca, 'XScale', 'log');
xlabel('Частота f (Гц)', 'FontSize', 11, 'FontWeight', 'bold');
title('Совмещенный график Боде (Амплитуда и Фаза)', 'FontSize', 12, 'FontWeight', 'bold');
legend([lines_magnitude{:}], legend_labels, 'Location', 'SouthWest');
ax2.Box = 'on'; ax2.LineWidth = 1.2;

% Пояснительные аннотации структуры графиков Боде
text(10^1.5, max(Z_magnitude)*1.0, '\bf Сплошная линия (—) = Модуль |Z|', 'FontSize', 9);
text(10^1.5, max(Z_magnitude)*0.9, '\bf Пунктир (--) = Фаза \phi', 'FontSize', 9);
