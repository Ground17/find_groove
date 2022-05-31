function score_sort = get_score(score, bps)
	score_found = [32 24 16 12 8 6 4 3 2 1];
	score32 = 1/(bps*8);
	score_length = score/score32;
	[~, index] = min(abs((score_found(:) - score_length))); % Find Minimum Difference Case
	score_sort = score_found(index);
end