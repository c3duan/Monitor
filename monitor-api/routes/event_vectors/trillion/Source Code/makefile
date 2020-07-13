# the compiler: gcc for C program, define as g++ for C++
CC = g++

# compiler flags:
#  -g    adds debugging information to the executable file
#  -Wall turns on most, but not all, compiler warnings
CFLAGS  = -Wall -g

# the build target executable:

all: UCR_DTW UCR_ED

UCR_DTW: UCR_DTW.cpp
	$(CC) $(CFLAGS) UCR_DTW.cpp -o UCR_DTW

UCR_ED: UCR_ED.cpp
	$(CC) $(CFLAGS) UCR_ED.cpp -o UCR_ED

clean:
	$(RM) UCR_DTW UCR_ED