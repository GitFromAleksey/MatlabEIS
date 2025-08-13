clc
clear

model = "Randles";

% load_system(model);
simIn = Simulink.SimulationInput(model);

% get_param('Randles/Sine Wave','dialogparameters') % получает все параметры компонента Step
% Assuming 'MyModel/Step' is the path to your Step block
% set_param('Randles/Step', 'StepTime', '1', 'InitialValue', '0', 'FinalValue', '5');
set_param('Randles/Sine Wave', 'Frequency', '100');

disp('Simulation run.');
out = sim(simIn);
disp('Simulation sucsess.');

y = out.simout.Data;
x = out.simout.Time;



x_len = length(x);
y_len = length(y);
fprintf("x_len: %d\n", x_len);
fprintf("y_len: %d\n", y_len);
% for i = 1:x_len
%     fprintf("x(%d) = %d\n", i, x(i+1)-x(i));
% end

fftx = fft2(x);

tiledlayout(5,1)
ax1 = nexttile
plot(ax1, x,y);
title(ax1, 'x,y');
xlabel('x');
xlabel('y');

hold on
ax1 = nexttile
plot(real(fftx));
title(ax1, 'real');
xlabel('freq');
ylabel('real');

ax2 = nexttile
plot(imag(fftx));
title(ax2, 'image');
xlabel('freq');
ylabel('imag');

ax3 = nexttile
plot(abs(fftx));
title(ax3, 'abs');
xlabel('freq');
ylabel('abs');

ax4 = nexttile
plot(angle(fftx));
title(ax4, 'angle');
xlabel('freq');
ylabel('angle');

hold off
% close_system(model); % закрывает симулинк