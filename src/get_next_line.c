#include "wordle.h"

static ssize_t	ft_find_n(t_view s_view)
{
	size_t	i;

	i = 0;
	while (i < s_view.size)
	{
		if (s_view.content[i] == '\n')
			return (i + 1);
		i++;
	}
	return (-1);
}

static char	*ft_strndup(char *s, ssize_t size)
{
	char	*result;
	ssize_t	len;
	ssize_t	i;

	i = 0;
	len = 0;
	while (len < size)
		len++;
	result = malloc((len + 1) * sizeof(char));
	if (result == NULL)
		return (NULL);
	while (s[i] && i < size)
	{
		result[i] = s[i];
		i++;
	}
	result[i] = '\0';
	return (result);
}

char	*ft_strnjoin(char *s1, char *s2, size_t size_of_s1, size_t size_of_s2)
{
	char	*result;
	size_t	i;

	i = 0;
	if (s1 == NULL)
		return (ft_strndup(s2, size_of_s2));
	if (s2 == NULL)
		return (ft_strndup(s1, size_of_s1));
	result = malloc ((size_of_s1 + size_of_s2) * sizeof(char));
	if (result == NULL)
		return (NULL);
	while (i < size_of_s1)
	{
		result[i] = s1[i];
		i++;
	}
	while (size_of_s2)
	{
		result[i++] = *(s2++);
		size_of_s2--;
	}
	free(s1);
	return (result);
}

static char	*ft_get_line(t_view *res)
{
	char	*temp;
	ssize_t	pos;
	char	*leak;

	temp = NULL;
	leak = NULL;
	pos = ft_find_n(*res);
	if (pos >= 0)
	{
		temp = ft_strndup(res->content, pos);
		leak = res->content;
		res->size -= pos;
		if (res->size == 0)
			res->content = NULL;
		else
			res->content = ft_strndup(&res->content[pos], res->size);
		free(leak);
	}
	else
	{
		temp = ft_strndup(res->content, res->size);
		free(res->content);
		res->content = NULL;
	}
	return (temp);
}

char	*get_next_line(int fd)
{
	static t_view	res;
	char			buf[BUFFER_SIZE];
	ssize_t			size_read;

	if (fd < 0 || BUFFER_SIZE <= 0)
		return (NULL);
	while (1)
	{
		if (res.content && ft_find_n(res) != -1)
			break ;
		size_read = read(fd, buf, BUFFER_SIZE);
		if (size_read < 0)
			return (NULL);
		else if (size_read == 0)
			break ;
		res.content = ft_strnjoin(res.content, buf, res.size, size_read);
		res.size += size_read;
	}
	if (res.content)
	{
		return (ft_get_line(&res));
	}
	return (NULL);
}
