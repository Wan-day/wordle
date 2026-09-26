#ifndef WORDLE_H
# define WORDLE_H
#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <unistd.h>
#include <fcntl.h> 
#include <stdlib.h>
#include <string.h>
#include <time.h>

# ifndef BUFFER_SIZE
#  define BUFFER_SIZE 64
# endif

typedef struct s_str_view
{
	char	*content;
	size_t	size;
}			t_view;

typedef struct s_word_file
{
	char	**words;
	int		size;
}			t_words;

typedef struct s_letter
{
	char	letter;
	int		state;
}			t_letter;

typedef enum e_letter_state
{
	GREEN,
	YELLOW,
	GRAY,
	WHITE
}			e_letter_state;

char	*get_next_line(int fd);

#endif
