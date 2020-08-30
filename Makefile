TARGET = lyrebird
LIBS = -lpulse
CC = gcc
CFLAGS = -g -Wall

OBJS = lyrebird.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) $(CFLAGS) $(LIBS) -o $(TARGET)

%.o: %.c
	$(CC) $(CFLAGS) -c $<

run: all
	./$(TARGET)

clean:
	rm *.o $(TARGET)
