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
