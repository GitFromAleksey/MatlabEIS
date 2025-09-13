clc
clear

model = "Randles";

% load_system(model);
open_system(model);
simIn = Simulink.SimulationInput(model);

% get_param('Randles/Sine Wave','dialogparameters') % получает все параметры компонента Step

freq_start = 1;
freq_stop  = 10000;
freq_step  = 10;

arr_size = (freq_stop/freq_step); % рассчёт размера массива результатов измерения
result = zeros(1, arr_size); % массив импедансов для ряда частот
frequencies = zeros(1, arr_size); % массив частот для измерения результатов
cnt = 1; % счётчик массива результата измерений импеданса

if freq_start == 0 % защита от ввода нулевой частоты
    freq_start = 1;
end

% Цикл рассчёта импеданса
for freq = freq_start : freq_step : freq_stop

% freq = 1000; % частота в Гц
gen_freq = freq*2*pi; % частота в рад/сек
sim_time = 2*1/freq; % время симуляции 2 периода колебаний

fprintf('-----------------------------------------------------------\n');
fprintf('Частота: %f\n', freq);
fprintf('Время симуляции: %f\n', sim_time);

% задание времени симуляции
set_param(model, 'StopTime', string(sim_time));
% задание частоты генератора
set_param('Randles/Sine Wave', 'Frequency', string(gen_freq));
set_param('Randles/Pulse Generator', 'Period', string(1/freq));

disp('Simulation run...');
out = sim(simIn);
disp('Simulation sucsess.');

% Транспонирование матриц для удобства
Y = transpose(out.simout.Data);
t = transpose(out.simout.Time);

t_len = length(t);
Y_len = length(Y);
fprintf("Кол-во сэмплов: %d\n", t_len);
% fprintf("y_len: %d\n", Y_len);

% Рассчёт БПФ
Y_fft = fft(Y);
L = t_len;              % общее кол-во захваченных сэмплов
x_diff = diff(t);       % разница времен м.у сэмплами
Ts = mean(x_diff);      % приод дискретизации
Fs = 1/Ts;              % частота дискретизации
Yabs = abs(Y_fft);      % массив модулей fft
freq_ax = Fs/L*(0:L-1); % массив частот по оси x.

% Поиск амплитуды сигнала
for i = 1:1:L
    if ((freq*0.9) < freq_ax(i)) && (freq_ax(i) < (freq*1.1))
        result(cnt) = Y_fft(i);
        frequencies(cnt) = freq_ax(i);
        cnt = cnt + 1;
        fprintf('Amplitude: %f\n', Yabs(i));
        break
    end 
end % for freq = 1:1:L

% Построение графиков
tiledlayout(2,1);

%  Амплитуда/частота
ax1 = nexttile;
plot(ax1, freq_ax, Yabs, "LineWidth", 2);
title(ax1, 'FFT');
xlabel('f, Hz');
ylabel('Amplitude');
grid on

hold on

% Исходный сигнал
ax0 = nexttile;
plot(ax0, t, Y);
title(ax0, 'Original signal');
xlabel('time');
ylabel('Ampl');

hold off
pause(0.1);
% close_system(model); % закрывает симулинк
end % for freq = 100:1000:100

figure;
ax_res = nexttile;
% График найквиста
plot(ax_res, real(result), -imag(result), "LineWidth", 2);
title(ax_res, 'Impedance Nyquist');
xlabel(ax_res, 'real(Z)');
ylabel(ax_res, '-imag(Z)');
grid on

figure;
ax_res1 = nexttile;
% Логарифмический график амплитуда/частота
hold on
loglog(ax_res1, frequencies, abs(result), "LineWidth", 2);
loglog(ax_res1, frequencies, real(result), "LineWidth", 2);
loglog(ax_res1, frequencies, imag(result), "LineWidth", 2);
hold off
title(ax_res1, 'Impedance log axies');
xlabel(ax_res1, 'f, Hz');
ylabel(ax_res1, 'Amplitude');
legend(ax_res1, 'abs', 'real', 'imag');
grid on


fprintf('Симуляция окончена!!!\n');