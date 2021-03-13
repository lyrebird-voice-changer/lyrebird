TARGET = lyrebird
LIBS = $(shell pkg-config --libs glib-2.0) -lpulse -lpulse-mainloop-glib -pthread -lrubberband -lm
CC = gcc
CFLAGS = -g -Wall $(shell pkg-config --cflags glib-2.0) -D_REENTRANT

OBJS = src/lyrebird.o src/pulse.o src/rubberband.o src/recording.o src/playback.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) $(CFLAGS) $(LIBS) -o $(TARGET)

%src/.o: src/%.c
	$(CC) $(CFLAGS) -c $<

run: all
	./$(TARGET)

clean:
	rm src/*.o $(TARGET)
