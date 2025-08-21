clc
clear

model = "Randles";

% load_system(model);
open_system(model);
simIn = Simulink.SimulationInput(model);

% get_param('Randles/Sine Wave','dialogparameters') % получает все параметры компонента Step

freq = 100; % частота в Гц
gen_freq = freq*2*pi; % частота в рад/сек
sim_time = 5*1/freq; % время симуляции 2 периода колебаний
% задание времени симуляции
set_param(model, 'StopTime', string(sim_time));
% задание частоты генератора
set_param('Randles/Sine Wave', 'Frequency', int2str(gen_freq));

disp('Simulation run.');
out = sim(simIn);
disp('Simulation sucsess.');

y = transpose(out.simout.Data);
x = transpose(out.simout.Time);


x_len = length(x);
y_len = length(y);
fprintf("x_len: %d\n", x_len);
fprintf("y_len: %d\n", y_len);
% for i = 1:x_len
%     fprintf("x(%d) = %d\n", i, x(i+1)-x(i));
% end

% Рассчёт БПФ
fftx = fft(y);
L = x_len; % общее кол-во захваченных сэмплов
x_diff = diff(x); % разница времен м.у сэмплами
Ts = mean(x_diff); % приод дискретизации
Fs = 1/Ts; % частота дискретизации
Yabs = abs(fftx); % массив модулей fft
freq_ax = Fs/L*(0:L-1); % частоты по оси x.

tiledlayout(2,1);

ax1 = nexttile;
plot(ax1, freq_ax, Yabs, "LineWidth", 2);
title(ax1, 'FFT');
xlabel('f, Hz');
ylabel('Amplitude');
grid on

hold on

ax0 = nexttile;
plot(ax0, x, y);
title(ax0, 'Original signal');
xlabel('time');
ylabel('Ampl');

% ax2 = nexttile
% plot(imag(fftx));
% title(ax2, 'image');
% xlabel('freq');
% ylabel('imag');
% 
% ax3 = nexttile
% plot(abs(fftx));
% title(ax3, 'abs');
% xlabel('freq');
% ylabel('abs');
% 
% ax4 = nexttile
% plot(angle(fftx));
% title(ax4, 'angle');
% xlabel('freq');
% ylabel('angle');

hold off
% close_system(model); % закрывает симулинк