clc
clear

Fs = 1000;          % частота сэмплирования(дискретизации)
T = 1/Fs;             % период сэмплирования(дискретизации)
L = 100;              % общее кол-во захваченных сэмплов
t = (0:L-1)*T;        % метки времени сэмплов

% Амплитуды гармоник
Af0 = -0.8;
f1 = 50;
Af1 = -0.7;
f2 = 120;
Af2 = 1;

% Генерация исходного сигнала
S = Af0 + Af1*sin(2*pi*f1*t) + Af2*sin(2*pi*f2*t);

% Добавление шума
X = S; % + 2*randn(size(t));


% Рассчёт FFT

Y = fft(X);
freq_ax = Fs/L*(0:L-1); % частоты по оси x. 
                        % Fs/L(L/T) - общее кол-во захваченных сэмплов
Yabs = abs(Y);          % амплитуды по оси Y

% Амплитуда при 50 Гц
% disp(Yabs(76));
% disp(freq_ax(76));

% Потроение графиков

figure;
tiledlayout(3,1)

ax0 = nexttile
plot(ax0, t, S);
title(ax0, 'Исходный сигнал');
xlabel('t, s');
ylabel('Amplitude');
grid on

hold on
ax1 = nexttile
plot(ax1, t, X);
title(ax1, 'Зашумлённый сигнал');
xlabel('t, s');
ylabel('Amplitude');
grid on

hold on
ax2 = nexttile
plot(ax2, freq_ax, Yabs);
title(ax2, 'FFT');
xlabel('f, Hz');
ylabel('Amplitude');
grid on

hold off

% Следущий график
figure;
tiledlayout(4,1)

ax_real = nexttile
plot(ax_real, freq_ax, real(Y));
title(ax_real, 'FFT real');
xlabel('f, Hz');
ylabel('Amplitude');
grid on

ax_imag = nexttile
plot(ax_imag, freq_ax, imag(Y));
title(ax_imag, 'FFT imag');
xlabel('f, Hz');
ylabel('Amplitude');
grid on

ax_abs = nexttile
plot(ax_abs, freq_ax, Yabs);
title(ax_abs, 'FFT ABS');
xlabel('f, Hz');
ylabel('Amplitude');
grid on

ax_angle = nexttile
phase_radians = angle(Y);
% phase_degrees = rad2deg(phase_radians);
theta = phase_radians;
plot(ax_angle, freq_ax, theta);
title(ax_angle, 'FFT Angle');
xlabel('f, Hz');
ylabel('Angle');
grid on
