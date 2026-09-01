% 1. Исходные данные
Rs  = 10;    
Cdl = 1e-5;  
Rct = 100;   
Aw  = 50;    

f = logspace(-2, 4, 500); 
omega = 2 * pi * f; 

% 2. Аппроксимация ИСКЛЮЧИТЕЛЬНО элемента Варбурга Zw(s)
Zw_exact = Aw * (1 - 1j) ./ sqrt(omega); 
order_w = 5; 
[num_w_s, den_w_s] = invfreqs(Zw_exact, omega, order_w, order_w);
sys_w_s = tf(num_w_s, den_w_s);

% Параметры дискретизации
Ts = 1e-5; 

% Дискретизация только блока Варбурга Zw(z)
sys_w_z = c2d(sys_w_s, Ts, 'tustin');
[num_w_z, den_w_z] = tfdata(sys_w_z, 'v');

% 3. Создание новой модели Simulink
model_name = 'RandlesWithSeparateWarburg';
try close_system(model_name, 0); catch; end
open_system(new_system(model_name));
set_param(model_name, 'SolverType', 'Fixed-step', 'FixedStep', num2str(Ts));

% 4. Добавление блоков Simulink [Left, Top, Right, Bottom]
% Входной ток
add_block('simulink/Sources/Step', [model_name '/Input_Current'], 'Position', [100, 150, 130, 180], 'SampleTime', num2str(Ts));

% Ветвь Rs (Gain)
add_block('simulink/Math Operations/Gain', [model_name '/Gain_Rs'], 'Position', [180, 80, 220, 120], 'Gain', num2str(Rs));

% Дискретный интегратор (Используем точное имя с дефисом 'Discrete-Time Integrator')
add_block('simulink/Discrete/Discrete-Time Integrator', [model_name '/Integrator_Cdl'], ...
    'Position', [480, 150, 520, 190], 'SampleTime', num2str(Ts));

% Блок ОТДЕЛЬНОГО элемента Варбурга
add_block('simulink/Discrete/Discrete Filter', [model_name '/Discrete_Warburg'], ...
    'Position', [280, 220, 360, 260], ...
    'Numerator', mat2str(num_w_z), 'Denominator', mat2str(den_w_z), 'SampleTime', num2str(Ts));

% Математическая обвязка для разделения блоков
add_block('simulink/Math Operations/Gain', [model_name '/Gain_Rct_Cdl'], ...
    'Position', [280, 150, 320, 190], 'Gain', num2str(1/Rct));

add_block('simulink/Math Operations/Gain', [model_name '/Gain_Cdl_Inv'], ...
    'Position', [560, 150, 600, 190], 'Gain', num2str(1/Cdl));

add_block('simulink/Math Operations/Sum', [model_name '/Sum1'], 'Position', [180, 150, 210, 180], 'Inputs', '+-');
add_block('simulink/Math Operations/Sum', [model_name '/Sum2'], 'Position', [400, 150, 430, 180], 'Inputs', '++');
add_block('simulink/Math Operations/Sum', [model_name '/Sum_U_total'], 'Position', [660, 120, 690, 150], 'Inputs', '++');

% Осциллограф
add_block('simulink/Sinks/Scope', [model_name '/Voltage_Scope'], 'Position', [730, 120, 760, 150]);

% 5. Соединение блоков (Потоки сигналов)
add_line(model_name, 'Input_Current/1', 'Gain_Rs/1', 'autorouting', 'on');
add_line(model_name, 'Input_Current/1', 'Sum1/1', 'autorouting', 'on');
add_line(model_name, 'Gain_Rs/1', 'Sum_U_total/1', 'autorouting', 'on');

add_line(model_name, 'Sum1/1', 'Gain_Rct_Cdl/1', 'autorouting', 'on');
add_line(model_name, 'Sum1/1', 'Discrete_Warburg/1', 'autorouting', 'on');

add_line(model_name, 'Gain_Rct_Cdl/1', 'Sum2/1', 'autorouting', 'on');
add_line(model_name, 'Discrete_Warburg/1', 'Sum2/2', 'autorouting', 'on');

add_line(model_name, 'Sum2/1', 'Integrator_Cdl/1', 'autorouting', 'on');
add_line(model_name, 'Integrator_Cdl/1', 'Gain_Cdl_Inv/1', 'autorouting', 'on');

add_line(model_name, 'Gain_Cdl_Inv/1', 'Sum_U_total/2', 'autorouting', 'on');
add_line(model_name, 'Gain_Cdl_Inv/1', 'Sum1/2', 'autorouting', 'on'); 

add_line(model_name, 'Sum_U_total/1', 'Voltage_Scope/1', 'autorouting', 'on');

% Визуальное выравнивание, сохранение и открытие
Simulink.BlockDiagram.arrangeSystem(model_name);
save_system(model_name);
open_system(model_name);
disp('Дискретная модель Рэндлса с изолированным Варбургом успешно собрана!');
