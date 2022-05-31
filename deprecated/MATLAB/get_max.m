function [maxSound, x, y] = get_max(sounds, range, threshold)
	maxSound = zeros(size(sounds));
	lengths = length(sounds);

	x = [];
	y = [];

	for i = 1:range:lengths
		s = i;
		e = s + range - 1;

		if e > lengths
			e = lengths;
		end

		[value, index] = max(sounds(s:e)); % get maximum [value, at index] of sound interval(s:e)

		if value > threshold % if this maximum value exceeds threshold:
			maxSound(index+s-1) = value;
			x(end+1) = index+s-1;
			y(end+1) = value;
		end
    end
end