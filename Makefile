TARGET = lyrebird
LIBS = -lpulse -lpulse-simple -pthread -lrubberband
CC = gcc
CFLAGS = -g -Wall $(pkg-config --cflags libpulse)

OBJS = src/lyrebird.o src/pulse.o src/rubberband.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) $(CFLAGS) $(LIBS) -o $(TARGET)

%src/.o: src/%.c
	$(CC) $(CFLAGS) $(LIBS) -c $<

run: all
	./$(TARGET)

clean:
	rm src/*.o $(TARGET)