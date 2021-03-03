clc;
clear;

% recorder = audiorecorder(44100, 16, 1);

% c = input('Will I Start? ');
% recorder.record();
% c = input('Will I Stop? ');
% recorder.stop();

% sounds = recorder.getaudiodata;
% Fs = 44100;

% sounds = sounds(:, 1); % use 1 channel of stereo channel

% figure(10);
% plot(sounds);

[sounds, Fs] = audioread('C:\Users\moonm\OneDrive\바탕 화면\MATLAB_music\도레미파솔라시도.mp3');
sounds = sounds(:, 1); % use 1 channel of stereo channel

%% 
% Set bpm of matronum
bpm = input('Set bpm: ');
if isempty(bpm)
    bpm = 150;
end
delay = 60/bpm;

%% 
% Set rest of matronum
amp = 7;
fs = 20500;  % sampling frequency
freq = 300; % metronome sound frequency level
duration = 0.01;
values = 0:1/fs:duration;
beat = amp*sin(2*pi*freq*values);

%%
% Play & Stop
%for i = 1:bpm % **change it to while & break if the user presses "stop"
%sound(beat);
%pause(delay);
%end

%%
% about global constants & variables

lengths = length(sounds); % sound length
secs = lengths/Fs; % sound length in real seconds
bps = bpm/60;

sounds_max = max(sounds);
range = 3500; % about Mung-ttuk coefficient
threshold = sounds_max/8;

margin = 0.1;
correct_constant = 3;

directory = 'C:\Users\moonm\OneDrive\바탕 화면\notes\';

[HighNoteImage, ~, HighNoteAlpha] = imread([directory 'high.png']);

[WholeNoteImage, ~, WholeNoteAlpha] = imread([directory 'whole_note.png']);
[DHalfNoteImage, ~, DHalfNoteAlpha] = imread([directory 'dotted_half_note.png']);
[HalfNoteImage, ~, HalfNoteAlpha] = imread([directory 'half_note.png']);
[DQuarterNoteImage, ~, DQuarterNoteAlpha] = imread([directory 'dotted_quarter_note.png']);
[QuarterNoteImage, ~, QuarterNoteAlpha] = imread([directory 'quarter_note.png']);
[DEighthNoteImage, ~, DEighthNoteAlpha] = imread([directory 'dotted_eighth_note.png']);
[EighthNoteImage, ~, EighthNoteAlpha] = imread([directory 'eighth_note.png']);
[DSixteenthNoteImage, ~, DSixteenthNoteAlpha] = imread([directory 'dotted_sixteenth_note.png']);
[SixteenthNoteImage, ~, SixteenthNoteAlpha] = imread([directory 'sixteenth_note.png']);

[WholeRestImage, ~, WholeRestAlpha] = imread([directory 'whole_rest.png']);
[DHalfRestImage, ~, DHalfRestAlpha] = imread([directory 'dotted_half_rest.png']);
[HalfRestImage, ~, HalfRestAlpha] = imread([directory 'half_rest.png']);
[DQuarterRestImage, ~, DQuarterRestAlpha] = imread([directory 'dotted_quarter_rest.png']);
[QuarterRestImage, ~, QuarterRestAlpha] = imread([directory 'quarter_rest.png']);
[DEighthRestImage, ~, DEighthRestAlpha] = imread([directory 'dotted_eighth_rest.png']);
[EighthRestImage, ~, EighthRestAlpha] = imread([directory 'eighth_rest.png']);
[DSixteenthRestImage, ~, DSixteenthRestAlpha] = imread([directory 'dotted_sixteenth_rest.png']);
[SixteenthRestImage, ~, SixteenthRestAlpha] = imread([directory 'sixteenth_rest.png']);

%%
% filter

% [n,fo,ao,w] = firpmord([700 800],[1 0],[0.01 0.01],Fs);
% b = firpm(n,fo,ao,w);

%%
% figure 1

% sounds = filter(b, 1, sounds);
% sounds = sounds * 3;

[maxSound, x, y] = get_max(sounds, range, threshold);

x = [0 x lengths]; % push first value(0), last value(lengths) to get peaks
y = [0 y 0]; % push first value(0), last value(0) to get peaks

polation = interp1(x, y, 1:lengths); % linear interpolation
polation_max = max(polation);
threshold_p = polation_max/3;

% figure(1);
% subplot(4, 1, 1);
% plot(sounds); xl = xlim; yl = ylim; % get limits of x, y axis
% subplot(4, 1, 2);
% plot(maxSound); xlim(xl); ylim(yl); % set limits of x, y, axis
% subplot(4, 1, 3);
% plot(polation); xlim(xl); ylim(yl); % set limits of x, y, axis
% subplot(4, 1, 4);
% findpeaks(polation); xlim(xl); ylim(yl);

%%
% figure 2
% sound frequency

% sounds = filter(b, 1, sounds);
% sounds = sounds * 3;

[~, loc] = findpeaks(polation);
loc(end+1) = lengths; % Because of better indexing. Not important sentence.
fprintf(['Total peaks: ' num2str(length(loc) - 1) '\n']);

indexArray = [];
for i = 1:length(loc) - 1
    y = sounds(max(1, loc(i)-400):min(lengths, loc(i+1)-400));

    N = length(y);
    Y = fft(y);
    Y = 2*Y(1:ceil(N/2));
    Y = abs(Y/N);
    f = Fs*(0:(N-1)/2)/N;
    
    subplot(length(loc)-1, 3, i*3-2);
    plot(y);
    title([num2str(i) ' original sounds']);
    
    subplot(length(loc)-1, 3, i*3-1);
    plot(f, Y);
    title([num2str(i) ' fft result']);
    
    % 50 means we divide to 50 intervals.
    % Also you can call 50 as 'Mung-ttuk coefficient'. It's same thing.
    % If you change this 50 value, peak detection result also changed.
    % 0.001 means threshold. Lower than 0.001 signals will be disregarded
    [fft_max, fft_x, fft_y] = get_max(Y, floor(length(Y)/500), max(abs(Y))/10);
    
    subplot(length(loc)-1, 3, i*3);
    plot(f, fft_max);
    title([num2str(i) ' fft max']);
    
   hz = 0;
    [~, index] = max(fft_y);
    for j = 1:length(fft_x)
        count = 0;
%         coefficient = 2;
        if j == index
            hz = f(fft_x(j));
            break; 
        else
            for k = j+1:length(fft_x)
                rate = f(fft_x(k)) / f(fft_x(j));
                int = round(rate);
                if int ~= 1 && abs(rate - int) < margin && int <= 7
%                   coefficient = coefficient + 1;
                    count = count + 1;
                end
            end
        end

%         if count / (length(fft_x) - j) > correct_percentage
%             hz = f(fft_x(j));
%             break;
%         end
        if length(fft_x) < correct_constant && count < correct_constant
            hz = f(fft_x(j));
            break;
        elseif count >= correct_constant
            hz = f(fft_x(j));
            break;
        end
    end
    
    fprintf(['\n  -- peak ' num2str(i) '\n']);
    if hz == 0
        fprintf(['can''t find peak\n']);
    else
        [chart, name] = get_sound(hz);
        indexArray(end+1) = mod(name(1)-'A'+5, 7)/2 + (name(2)-'1')*3.5 - 13.5;
        fprintf(['     Recoded hz is ' num2str(hz) '\n']);
        fprintf(['     predicted peak is ' num2str(chart) '(' name ').\n']);
    end    
end

%% 
% sound length

pk = loc;
th = []; 
polation_0 = polation - threshold_p;

for m = 1:1:lengths-1
    if polation_0(m)*polation_0(m+1)<0 && polation_0(m) > polation_0(m+1)
        th = [th m];
	end
end

pk_1 = ones(1,length(pk));
pk_label = [pk;pk_1];
th_0 = zeros(1,length(th));
th_label = [th;th_0];
mu = [pk_label th_label];
mu_sort = sortrows(mu', 1);

score = [];
score_sort = [];
if length([pk_1 th_0])-1 > 1
    for p = 1:1:length([pk_1 th_0])-1
        score = (mu_sort(p+1,1) - mu_sort(p,1)) / Fs;
        if mu_sort(p,2) == 1
            score_sort = [score_sort; get_score(score, bps) 1];
        end
        if mu_sort(p,2) == 0 && mu_sort(p+1,2) == 1
            score_sort = [score_sort; get_score(score, bps) 0];
        end     
    end
else
    msg = 'No peaks detected.';
    error(msg)
end
%%
% score display

figure(3);

width = 100;
widthMargin1 = width/100*3; %notes with tail
widthMargin2 = width/100*1.6; %notes without tail and without dot, rests without tail
widthMargin3 = width/100*2; %notes without tail and with dot, rests with dot

heightMargin = 20;

lineX = [0 width];
lineY = [];
for i = -2:2
    lineY = [lineY; [i i]];
end

ylim([-2-heightMargin 2+heightMargin]);
xlim([0 width]);
axis off;
line(repmat(lineX, 5, 1)', lineY', 'Color', 'black');
hold on;
highNotePlot = imagesc([0 widthMargin1], [2+1 -2-1], HighNoteImage);
highNotePlot.AlphaData = HighNoteAlpha;

startIndex = widthMargin1*1.2;

noteIndex = 1;
for i = 1:length(score_sort)
    if score_sort(i, 2) == 1
        if score_sort(i,1) == 32
            notePlot = imagesc([startIndex startIndex+widthMargin2], [indexArray(noteIndex)-.5+1 indexArray(noteIndex)-.5], WholeNoteImage);
            notePlot.AlphaData = WholeNoteAlpha;
        elseif score_sort(i,1) == 24
            notePlot = imagesc([startIndex startIndex+widthMargin3], [indexArray(noteIndex)-.5+4 indexArray(noteIndex)-.5], DHalfNoteImage);
            notePlot.AlphaData = DHalfNoteAlpha;
        elseif score_sort(i,1) == 16
            notePlot = imagesc([startIndex startIndex+widthMargin2], [indexArray(noteIndex)-.5+4 indexArray(noteIndex)-.5], HalfNoteImage);
            notePlot.AlphaData = HalfNoteAlpha;
        elseif score_sort(i,1) == 12
            notePlot = imagesc([startIndex startIndex+widthMargin3], [indexArray(noteIndex)-.5+4 indexArray(noteIndex)-.5], DQuarterNoteImage);
            notePlot.AlphaData = DQuarterNoteAlpha;
        elseif score_sort(i,1) == 8
            notePlot = imagesc([startIndex startIndex+widthMargin2], [indexArray(noteIndex)-.5+4 indexArray(noteIndex)-.5], QuarterNoteImage);
            notePlot.AlphaData = QuarterNoteAlpha;
        elseif score_sort(i,1) == 6
            notePlot = imagesc([startIndex startIndex+widthMargin1], [indexArray(noteIndex)-.5+4 indexArray(noteIndex)-.5], DEighthNoteImage);
            notePlot.AlphaData = DEighthNoteAlpha;
        elseif score_sort(i,1) == 4
            notePlot = imagesc([startIndex startIndex+widthMargin1], [indexArray(noteIndex)-.5+4 indexArray(noteIndex)-.5], EighthNoteImage);
            notePlot.AlphaData = EighthNoteAlpha;
        elseif score_sort(i,1) == 3
            notePlot = imagesc([startIndex startIndex+widthMargin1], [indexArray(noteIndex)-.5+4 indexArray(noteIndex)-.5], DSixteenthNoteImage);
            notePlot.AlphaData = DSixteenthNoteAlpha;
        elseif score_sort(i,1) == 2
            notePlot = imagesc([startIndex startIndex+widthMargin1], [indexArray(noteIndex)-.5+4 indexArray(noteIndex)-.5], SixteenthNoteImage);
            notePlot.AlphaData = SixteenthNoteAlpha;
        end
    
        if abs(indexArray(noteIndex)) >= 3
            line([startIndex-widthMargin1/32*7 startIndex+widthMargin1/32*25], [indexArray(noteIndex) indexArray(noteIndex)], 'Color', 'black', 'LineWidth', 1.2);
        end

        noteIndex = noteIndex + 1;
    else
        if score_sort(i,1) == 32
            notePlot = imagesc([startIndex startIndex+widthMargin2], [1 .5], WholeRestImage);
            notePlot.AlphaData = WholeRestAlpha;
        elseif score_sort(i,1) == 24
            notePlot = imagesc([startIndex startIndex+widthMargin3], [.5 0], DHalfRestImage);
            notePlot.AlphaData = DHalfRestAlpha;
        elseif score_sort(i,1) == 16
            notePlot = imagesc([startIndex startIndex+widthMargin2], [.5 0], HalfRestImage);
            notePlot.AlphaData = HalfRestAlpha;
        elseif score_sort(i,1) == 12
            notePlot = imagesc([startIndex startIndex+widthMargin3], [1.5 -1.5], DQuarterRestImage);
            notePlot.AlphaData = DQuarterRestAlpha;
        elseif score_sort(i,1) == 8
            notePlot = imagesc([startIndex startIndex+widthMargin2], [1.5 -1.5], QuarterRestImage);
            notePlot.AlphaData = QuarterRestAlpha;
        elseif score_sort(i,1) == 6
            notePlot = imagesc([startIndex startIndex+widthMargin3], [1 -1], DEighthRestImage);
            notePlot.AlphaData = DEighthRestAlpha;
        elseif score_sort(i,1) == 4
            notePlot = imagesc([startIndex startIndex+widthMargin2], [1 -1], EighthRestImage);
            notePlot.AlphaData = EighthRestAlpha;
        elseif score_sort(i,1) == 3
            notePlot = imagesc([startIndex startIndex+widthMargin3], [1 -2], DSixteenthRestImage);
            notePlot.AlphaData = DSixteenthRestAlpha;
        elseif score_sort(i,1) == 2
            notePlot = imagesc([startIndex startIndex+widthMargin2], [1 -2], SixteenthRestImage);
            notePlot.AlphaData = SixteenthRestAlpha;
        end
    end
        
    startIndex = startIndex + widthMargin1*0.8;
end
