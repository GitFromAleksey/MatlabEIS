function freq_arr = freq_arr_gen(freq_start, octava_num)

% freq_start = 1;
freq_end = octava_num;
freq_cur = freq_start;

result = [];
result_index = 1;
while (freq_cur < freq_end)

    octava = freq_cur*2;
    % fprintf("octava: %f, freq_cur: %f\n", octava, freq_cur);
    for f = freq_cur:(octava-freq_cur)/12:octava
        % fprintf("%f,", f);
        result(result_index) = f;
        result_index = result_index + 1;
    end
    % fprintf("\n");
    freq_cur = octava;
end
% disp(result);
freq_arr = result;

end

% freq_start = 1;
% freq_end = 8;
% freq_cur = freq_start;
% 
% result = [];
% result_index = 1;
% while (freq_cur < freq_end)
% 
%     octava = freq_cur*2;
%     fprintf("octava: %f, freq_cur: %f\n", octava, freq_cur);
%     for f = freq_cur:(octava-freq_cur)/12:octava
%         % fprintf("%f,", f);
%         result(result_index) = f;
%         result_index = result_index + 1;
%     end
%     fprintf("\n");
%     freq_cur = octava;
% end
% disp(result);