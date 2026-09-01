% Моделирование семейства кривых Найквиста схемы Рэндлса для Li-ion 18650 в зависимости от SOC
clear; clc; close all;

%% 1. Задание массива степеней заряда (SOC)
% Можно задать любой массив значений от 0.0 до 1.0
SOC_array = [1.0, 0.5, 0.2, 0.05];

% Проверка корректности ввода
if any(SOC_array < 0) || any(SOC_array > 1)
    error('Все значения SOC должны быть в диапазоне от 0 до 1');
end

%% 2. Задание диапазона частот
f = logspace(-2, 4, 500); % От 0.01 Гц до 10 000 Гц
omega = 2 * pi * f;       

%% 3. Настройка графического окна
figure('Color', 'w'); % Ошибка исправилась: убрана пустая позиция
hold on;
grid on;

% Базовые физические константы ячейки 18650 при SOC = 50%
Rs_base  = 0.018; 
Rct_base = 0.022;
Cdl_base = 2.5;
Aw_base  = 0.008;

% Подготовка массива цветов для разных графиков
colors_matrix = lines(length(SOC_array)); 
legend_labels = cell(1, length(SOC_array));

max_Real_Z = 0; % Переменная для динамической настройки масштаба осей

%% 4. Цикл расчета и построения для каждого значения SOC
for k = 1:length(SOC_array)
    SOC = SOC_array(k);
    
    % Эмпирические зависимости параметров 18650 от SOC
    Rs  = Rs_base * (1 + 0.15 * (1 - SOC)^4); 
    Rct = Rct_base * (1 + 0.5 * (SOC - 0.5)^2 + 2.5 * exp(-15 * SOC)); 
    Cdl = Cdl_base * (1 - 0.2 * (SOC - 0.5)^2);
    Aw  = Aw_base * (1 + 1.8 * exp(-10 * SOC));
    
    % Расчет аналитического импеданса
    Zw = Aw * (1 - 1j) ./ sqrt(omega); 
    Z_branch = Rct + Zw;
    Z_Cdl = 1 ./ (1j * omega * Cdl);
    
    % Полный импеданс схемы Рэндлса
    Z_tot = Rs + (Z_Cdl .* Z_branch) ./ (Z_Cdl + Z_branch);
    Real_Z = real(Z_tot);
    Imag_Z = imag(Z_tot);
    
    % Сохраняем максимальное значение для лимитов графика
    max_Real_Z = max(max_Real_Z, max(Real_Z));
    
    % Построение годографа (инвертированная мнимая ось)
    plot(Real_Z, -Imag_Z, 'LineWidth', 2.5, 'Color', colors_matrix(k,:));
    
    % Отредактировано: маркеры характерных частот 1 Гц и 100 Гц
    f_markers = [1, 100]; 
    for m = 1:length(f_markers)
        [~, idx] = min(abs(f - f_markers(m)));
        plot(Real_Z(idx), -Imag_Z(idx), 'o', 'MarkerFaceColor', colors_matrix(k,:), ...
             'MarkerEdgeColor', 'k', 'MarkerSize', 6);
    end
    
    % Текст для легенды
    legend_labels{k} = sprintf('SOC = %.0f%% (Rs=%.1fm\\Omega, Rct=%.1fm\\Omega)', ...
                        SOC*100, Rs*1000, Rct*1000);
end

%% 5. Оформление семейства графиков
axis equal; 
xlim([0, max_Real_Z * 1.05]);
ylim([0, max_Real_Z * 0.6]); % Традиционное соотношение осей для EIS
ax = gca;
ax.Box = 'on';
ax.LineWidth = 1.2;
ax.FontSize = 11;

xlabel('Действительное сопротивление Z'' (\Omega)', 'FontSize', 12, 'FontWeight', 'bold');
ylabel('-Мнимая часть Z'''' (\Omega)', 'FontSize', 12, 'FontWeight', 'bold');
title('Семейство диаграмм Найквиста для Li-ion 18650 в зависимости от SOC', 'FontSize', 13, 'FontWeight', 'bold');
legend(legend_labels, 'Location', 'NorthWest', 'FontSize', 10);

%% 6. Синхронизация с Simulink (экспорт последнего состояния из массива)
model_name = 'Randles_Simulink_Standard';

if bdIsLoaded(model_name)
    % Передаем параметры крайнего рассчитанного SOC в блоки Simulink
    num_W = [Aw]; den_W = [1, 0.5];
    
    set_param([model_name '/Rs_Gain'], 'Gain', num2str(Rs));
    set_param([model_name '/Warburg_TF'], 'Numerator', ['[' num2str(num_W) ']'], 'Denominator', ['[' num2str(den_W) ']']);
    set_param([model_name '/Cdl_Integrator'], 'Numerator', '1', 'Denominator', ['[' num2str(Cdl) ' 0]']);
    save_system(model_name);
    fprintf('\n[Simulink] Параметры модели настроены на конечное значение массива: SOC = %.0f%%\n', SOC*100);
else
    fprintf('\n[Инфо] Для автоматического обновления параметров откройте модель "%s" в Simulink.\n', model_name);
end
