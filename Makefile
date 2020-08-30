TARGET = lyrebird
LIBS = -lpulse -lpulse-simple -pthread -lrubberband
CC = gcc
CFLAGS = -g -Wall $(pkg-config --cflags libpulse)

OBJS = lyrebird.o pulse.o rubberband.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) $(CFLAGS) $(LIBS) -o $(TARGET)

%.o: %.c
	$(CC) $(CFLAGS) $(LIBS) -c $<

run: all
	./$(TARGET)

clean:
	rm *.o $(TARGET)
