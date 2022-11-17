CC = g++
TARGET = server

.PHONY: clean

all: $(TARGET)

server: web_server.cpp
	$(CC) -std=c++11 $^ -o $@

clean:
	rm -f $(TARGET)
