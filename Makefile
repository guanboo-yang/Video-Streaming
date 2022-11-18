CC = g++
TARGET = server

.PHONY: clean

all: $(TARGET)

server: src/server.cpp
	$(CC) -std=c++11 $^ -o $@

clean:
	rm -f $(TARGET)
