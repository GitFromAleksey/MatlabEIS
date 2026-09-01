% 1. Исходные данные (физические параметры)
Rs  = 10;    % Сопротивление раствора, Ом
Cdl = 1e-5;  % Емкость двойного слоя, Ф
Rct = 100;   % Сопротивление переноса заряда, Ом
Aw  = 50;    % Коэффициент Варбурга, Ом*с^(-0.5)

% 2. Аппроксимация элемента Варбурга передаточной функцией Zw(s)
% Используем метод Фиттинга (invfreqs) для получения коэффициентов числителя (num) и знаменателя (den)
f = logspace(-2, 4, 500); 
omega = 2 * pi * f; 
s = 1j * omega;
Zw_exact = Aw * (1 - 1j) ./ sqrt(omega); % Исходное аналитическое выражение

order = 5; % Порядок аппроксимации передаточной функции
[num_w, den_w] = invfreqs(Zw_exact, omega, order, order);

% 3. Создание новой модели Simulink
model_name = 'RandlesSimulinkModel';
open_system(new_system(model_name));

% 4. Добавление стандартных блоков Simulink
% Входной сигнал (например, Источник Тока I)
add_block('simulink/Sources/Step', [model_name '/Input_Current'], 'Position', [50, 150, 80, 180]);

% Ветвь 1: Сопротивление раствора Rs (Блок Gain)
add_block('simulink/Math Operations/Gain', [model_name '/Gain_Rs'], 'Position', [150, 150, 190, 180], 'Gain', num2str(Rs));

% Ветвь 2: Импеданс параллельного контура Z_p(s) = 1 / (s*Cdl + 1/(Rct + Zw))
% Для этого реализуем Zw, добавим Rct, и пустим в контур обратной связи с Cdl
add_block('simulink/Continuous/Transfer Fcn', [model_name '/TF_Warburg'], ...
    'Position', [250, 250, 330, 290], 'Numerator', mat2str(num_w), 'Denominator', mat2str(den_w));

add_block('simulink/Math Operations/Bias', [model_name '/Bias_Rct'], ...
    'Position', [370, 250, 410, 290], 'Bias', num2str(Rct)); % Сложение с Rct

% Реализация 1/(Rct + Zw)
add_block('simulink/Math Operations/Math Function', [model_name '/Reciprocal'], ...
    'Position', [450, 250, 480, 280], 'Operator', 'reciprocal');

% Сумматор токов в параллельной цепи (I_total = I_Cdl + I_Rct_Zw)
add_block('simulink/Math Operations/Sum', [model_name '/Sum_Currents'], ...
    'Position', [530, 250, 550, 270], 'Inputs', '++');

% Интегратор 1/(s*Cdl) для получения напряжения на параллельном контуре
add_block('simulink/Continuous/Integrator', [model_name '/Integrator_Cdl'], ...
    'Position', [590, 250, 620, 280]);
add_block('simulink/Math Operations/Gain', [model_name '/Gain_InvCdl'], ...
    'Position', [650, 250, 690, 280], 'Gain', num2str(1/Cdl));

% Блок обратной связи (ток через ветвь Rct+Zw зависит от напряжения на ней)
% Напряжение с выхода Gain_InvCdl подаем обратно на вход Zw через Reciprocal
% Для правильной топологии развернем блоки контура
set_param([model_name '/TF_Warburg'], 'Orientation', 'left');
set_param([model_name '/Bias_Rct'], 'Orientation', 'left');
set_param([model_name '/Reciprocal'], 'Orientation', 'left');
% Меняем позиции элементов для красивой обратной связи (контур снизу)
set_param([model_name '/Reciprocal'], 'Position', [450, 320, 480, 350]);
set_param([model_name '/Bias_Rct'], 'Position', [350, 320, 390, 350]);
set_param([model_name '/TF_Warburg'], 'Position', [220, 320, 300, 350]);

% Финальный сумматор общего напряжения (U_total = U_Rs + U_parallel)
add_block('simulink/Math Operations/Sum', [model_name '/Sum_U_total'], ...
    'Position', [750, 150, 770, 170], 'Inputs', '++');

% Блок отображения результатов (Scope)
add_block('simulink/Sinks/Scope', [model_name '/Voltage_Scope'], 'Position', [820, 140, 850, 180]);

% 5. Соединение блоков стрелками (Потоками данных Simulink)
% Входной ток разветвляется на Rs и на параллельный контур (Sum_Currents)
add_line(model_name, 'Input_Current/1', 'Gain_Rs/1', 'autorouting', 'on');
add_line(model_name, 'Input_Current/1', 'Sum_Currents/1', 'autorouting', 'on');

% Выход Rs идет на финальный сумматор напряжения
add_line(model_name, 'Gain_Rs/1', 'Sum_U_total/1', 'autorouting', 'on');

% Прямая ветвь параллельного контура: Сумматор -> Интегратор -> Емкость -> Выход напряжения
add_line(model_name, 'Sum_Currents/1', 'Integrator_Cdl/1', 'autorouting', 'on');
add_line(model_name, 'Integrator_Cdl/1', 'Gain_InvCdl/1', 'autorouting', 'on');
add_line(model_name, 'Gain_InvCdl/1', 'Sum_U_total/2', 'autorouting', 'on');

% Обратная связь: Напряжение контура заводится в цепочку Варбурга
add_line(model_name, 'Gain_InvCdl/1', 'TF_Warburg/1', 'autorouting', 'on');
add_line(model_name, 'TF_Warburg/1', 'Bias_Rct/1', 'autorouting', 'on');
add_line(model_name, 'Bias_Rct/1', 'Reciprocal/1', 'autorouting', 'on');

% Вычитаем ток утечки через Rct+Zw из общего тока на входе емкости
add_line(model_name, 'Reciprocal/1', 'Sum_Currents/2', 'autorouting', 'on');
% Корректируем знак на сумматоре токов для правильной обратной связи (I_Cdl = I_in - I_branch)
set_param([model_name '/Sum_Currents'], 'Inputs', '+-');

% Выход общего напряжения на Scope
add_line(model_name, 'Sum_U_total/1', 'Voltage_Scope/1', 'autorouting', 'on');

% Выравнивание схемы
Simulink.BlockDiagram.arrangeSystem(model_name);
save_system(model_name);
disp('Математическая модель Рэндлса в Simulink успешно собрана!');
