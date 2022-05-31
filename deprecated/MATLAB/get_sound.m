%%
% README
%
% Algorithm.
%   let array [1, 4, 7, 10], if we want closet element from number 5
%
%   1. array - number: [-4, -1, 2, 5]
%   2. abs(array): [4, 1, 2, 5]
%   3. find min element: [ , (1),  , ]
%
%   So, second element 4 is closet from number 5
%   I use this algorithm to find closet Hz from charts.
%
% Data type.
%   Matlab vector(array) only takes 'same type' variables,
%   so I use cell, which start with '{', end with '}'.
%   Cell can take different types variables.
%

function [chart, name] = get_sound(hz)
    charts = [
        {82.4, 'E2'} 
        {87.3, 'F2'} 
        {92.5, 'G2b'} 
        {98.0, 'G2'} 
        {103.8, 'A2b'} 
        {110.0, 'A2'} 
        {116.3, 'B2b'} 
        {123.5, 'B2'} 
        {130.8, 'C3'} 
        {138.6, 'D3b'} 
        {146.8, 'D3'} 
        {155.4, 'E3b'} 
        {164.8, 'E3'} 
        {174.6, 'F3'} 
        {185.0, 'G3b'} 
        {196.0, 'G3'} 
        {207.6, 'A3b'} 
        {220.0, 'A3'} 
        {233.0, 'B3b'} 
        {246.9, 'B3'} 
        {261.6, 'C4'} 
        {277.0, 'D4b'} 
        {293.6, 'D4'} 
        {311.1, 'E4b'} 
        {329.8, 'E4'} 
        {349.2, 'F4'} 
        {369.9, 'G4b'} 
        {392.0, 'G4'} 
        {415.3, 'A4b'} 
        {440.0, 'A4'} 
        {466.1, 'B4b'} 
        {493.8, 'B4'} 
        {523.2, 'C5'} 
        {554.3, 'D5b'} 
        {587.3, 'D5'} 
        {622.6, 'E5b'} 
        {659.3, 'E5'} 
        {698.5, 'F5'} 
        {740.0, 'G5b'} 
        {784.0, 'G5'} 
        {830.8, 'A5b'} 
        {880.0, 'A5'} 
        {932.2, 'B5b'} 
        {987.7, 'B5'} 
        {1046.5, 'C6'} 
        {1108.7, 'D6b'} 
        {1174.7, 'D6'}
    ];
    [~, index] = min(abs(cell2mat(charts(:, 1)) - hz));
    chart = cell2mat(charts(index, 1));
    name = cell2mat(charts(index, 2));
end