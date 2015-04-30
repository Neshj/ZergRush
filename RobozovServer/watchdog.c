#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/reboot.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include "report.h"


void handler(int sig, siginfo_t * si, void * unused)
{
	printf("Child died.\n");
	if (reboot(42) < 0)
	{
		perror("Unable to reboot");
	}
}

#define MAX_ARG_SIZE 32

int main(int argc, char ** argv, char ** envs)
{
	struct sigaction sa;

	sa.sa_flags = SA_SIGINFO;
	sigemptyset(&sa.sa_mask);
	sa.sa_sigaction = handler;

	if (argc < 2)
	{
		printf("Usage: %s <Child process> [args list...]\n", argv[0]);

		return 0;
	}

	if (sigaction(SIGCHLD, &sa, NULL) < 0)
	{
		perror("Error in sigaction");

		return -1;
	}

	if (sigaction(SIGINT, &sa, NULL) < 0)
	{
		perror("Error in sigaction");

		return -1;
	}

	if (fork() == 0)
	{
		char ** args;
		int i;

		args = malloc(sizeof(char *) * (argc));

		/* Build args array to pass to child process*/
		for (i = 0; i < argc - 1; i++)
		{
			/* Allocate memory for the argument */
			args[i] = malloc(MAX_ARG_SIZE + 1);

			/* Copy it's content */
			strncpy(args[i], argv[1 + i], MAX_ARG_SIZE);

			/* NULL terminate it */
			args[MAX_ARG_SIZE] = '\0';

			printf("Arg: %s\n", args[i]);
		}

		/* Last array object must be NULL */
		args[argc - 1] = NULL;

		/* Call process */
		if (execve(argv[1], args, envs) < 0)
		{
			perror("Error in execve");

			return -1;
		}
		return 0;
	}

	wait(NULL);
}
