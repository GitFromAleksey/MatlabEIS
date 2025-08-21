clc
clear

model = "Randles";

% load_system(model);
open_system(model);
simIn = Simulink.SimulationInput(model);

% get_param('Randles/Sine Wave','dialogparameters') % получает все параметры компонента Step

arr_size = (10000/200)
result = zeros(1, arr_size);
frequencies = zeros(1, arr_size);
cnt = 1;
for freq = 100:200:10000

% freq = 1000; % частота в Гц
gen_freq = freq*2*pi; % частота в рад/сек
sim_time = 5*1/freq; % время симуляции 2 периода колебаний

fprintf('-----------------------------------------------------------\n');
fprintf('Частота: %f\n', freq);
fprintf('Время симуляции: %f\n', sim_time);

% задание времени симуляции
set_param(model, 'StopTime', string(sim_time));
% задание частоты генератора
set_param('Randles/Sine Wave', 'Frequency', string(gen_freq));

disp('Simulation run...');
out = sim(simIn);
disp('Simulation sucsess.');

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
Yabs = abs(Y_fft);       % массив модулей fft
freq_ax = Fs/L*(0:L-1); % частоты по оси x.

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

ax1 = nexttile;
plot(ax1, freq_ax, Yabs, "LineWidth", 2);
title(ax1, 'FFT');
xlabel('f, Hz');
ylabel('Amplitude');
grid on

hold on

ax0 = nexttile;
plot(ax0, t, Y);
title(ax0, 'Original signal');
xlabel('time');
ylabel('Ampl');

hold off
% close_system(model); % закрывает симулинк
end % for freq = 100:1000:100

figure;
ax_res = nexttile;
% plot(ax_res, frequencies, imag(result), "LineWidth", 2);
plot(ax_res, real(result), -imag(result), "LineWidth", 2);
title(ax_res, 'Result');
xlabel(ax_res, 'real(Z)');
ylabel(ax_res, 'imag(Z)');
grid on


fprintf('Симуляция окончена!!!\n');