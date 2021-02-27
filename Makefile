TARGET = lyrebird
LIBS = -lglib-2.0 -lpulse -lpulse-mainloop-glib -pthread -lrubberband 
CC = gcc
CFLAGS = -g -Wall -I/usr/include/glib-2.0 -I/usr/lib/glib-2.0/include -D_REENTRANT

OBJS = src/lyrebird.o src/pulse.o src/rubberband.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) $(CFLAGS) $(LIBS) -o $(TARGET)

%src/.o: src/%.c
	$(CC) $(CFLAGS) -c $<

run: all
	./$(TARGET)

clean:
	rm src/*.o $(TARGET)
