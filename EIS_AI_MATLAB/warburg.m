% 1. Исходные данные и расчет аналитического импеданса Варбурга
Aw = 50; % Коэффициент Варбурга, Ом*с^(-0.5)

% Частотный диапазон
f = logspace(-2, 4, 500); 
omega = 2 * pi * f; 

% Аналитическое выражение элемента Варбурга
Zw_exact = Aw * (1 - 1j) ./ sqrt(omega); 

% 2. Непрерывная аппроксимация методом фиттинга (invfreqs)
order = 5; 
[num_s, den_s] = invfreqs(Zw_exact, omega, order, order);
sys_s = tf(num_s, den_s);

% 3. Дискретизация системы (Z-преобразование)
Ts = 1e-5; % Шаг дискретизации (10 мкс)

% Перевод в дискретную форму методом Тастина (Tustin)
sys_z = c2d(sys_s, Ts, 'tustin');
[num_z, den_z] = tfdata(sys_z, 'v');

% 4. Создание новой модели Simulink
model_name = 'WarburgElementModel';
try
    close_system(model_name, 0); % Закрыть модель, если она уже открыта
catch
end
open_system(new_system(model_name));

% Настройка глобального решателя на фиксированный дискретный шаг
set_param(model_name, 'SolverType', 'Fixed-step', 'FixedStep', num2str(Ts));

% 5. Добавление дискретных блоков Simulink с явными векторами координат [Left, Top, Right, Bottom]
% Входной тестовый сигнал (дискретная синусоида)
add_block('simulink/Sources/Sine Wave', [model_name '/Input_Signal'], ...
    'Position', [100, 100, 140, 140], ...
    'SineType', 'Time based', ...
    'Frequency', '10', ...
    'SampleTime', num2str(Ts));

% ИЗОЛИРОВАННЫЙ БЛОК ЭЛЕМЕНТА ВАРБУРГА
add_block('simulink/Discrete/Discrete Filter', [model_name '/Discrete_Warburg'], ...
    'Position', [220, 100, 320, 140], ...
    'Numerator', mat2str(num_z), ...
    'Denominator', mat2str(den_z), ...
    'SampleTime', num2str(Ts));

% Блок отображения результатов (Дискретный Scope)
add_block('simulink/Sinks/Scope', [model_name '/Warburg_Scope'], ...
    'Position', [400, 100, 440, 140]);

% 6. Соединение блоков стрелками
add_line(model_name, 'Input_Signal/1', 'Discrete_Warburg/1', 'autorouting', 'on');
add_line(model_name, 'Discrete_Warburg/1', 'Warburg_Scope/1', 'autorouting', 'on');

% Автоматическое визуальное выравнивание, сохранение и открытие модели
Simulink.BlockDiagram.arrangeSystem(model_name);
save_system(model_name);
open_system(model_name);

disp('Модель изолированного элемента Варбурга успешно создана и открыта без ошибок!');
