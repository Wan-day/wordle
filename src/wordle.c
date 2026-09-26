#include "wordle.h"

static int	count_lines(const char *filename)
{
	int		fd;
	int		line_count;
	
	fd = open(filename, O_RDONLY);
	line_count = 0;
	while (get_next_line(fd) > 0)
		line_count++;
	return (line_count);
}

t_words	*read_words_file(char *filename)
{
	int		fd;
	int		i;
	int		size;
	char	*line;
	t_words	*words;

	fd = open(filename, O_RDONLY);
	size = count_lines(filename);
	words = calloc(1, sizeof(t_words));
	words->size = size;
	words->words = calloc(size, sizeof(char *));
	i = 0;
	while ((line = get_next_line(fd)) > 0)
	{
		words->words[i] = strdup((const char*)line);
		i++;
		free(line);
	}
	close(fd);
	return (words);
}

char	*select_main_word(t_words *words)
{
	int	random;

	srand(time(NULL));
	random = rand() % words->size;
	return(words->words[random]);
}

t_letter	*build_alphabet()
{
	char		letter;
	t_letter	*alphabet;
	int			i;

	i = 0;
	alphabet = calloc('z' - 'a' + 1, sizeof(t_letter));
	letter = 'a';
	while (letter <= 'z')
	{
		alphabet[i].letter = letter;
		alphabet[i].state = WHITE;
		letter++;
		i++;
	}
	return (alphabet);
}

int	is_valid_word(t_letter *player_guess, t_words *words)
{
	char	word[6];

	for (int i = 0; i < 5; i++)
		word[i] = player_guess[i].letter;
	word[5] = '\0';
	for (int i = 0; i < words->size; i++)
	{
		if (!(strncmp(word, words->words[i], 5)))
			return 0;
	}
	return 1;
}

int	contains_letter(char letter, char *word)
{
	for (int i = 0; i < 5; i++)
	{
		if (letter == word[i])
			return (1);
	}
	return (0);
}

t_letter	*check_player_answer(t_letter *player_guess, t_words *words, char *correct_word)
{
	t_letter	*result;

	if (!is_valid_word(player_guess, words))
		return NULL;
	result = calloc(5, sizeof(t_letter));
	for (int letter_pos = 0; letter_pos < 5; letter_pos++)
	{
		result[letter_pos].letter = player_guess[letter_pos].letter;
		if ((player_guess[letter_pos].letter) == correct_word[letter_pos])
			result[letter_pos].state = GREEN;
		else if (contains_letter((player_guess[letter_pos].letter), correct_word))
			result[letter_pos].state = YELLOW;
		else
			result[letter_pos].state = GRAY;
	}
	return (result);
}
