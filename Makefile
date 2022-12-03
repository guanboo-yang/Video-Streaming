INCLUDE = -Iinc
TARGET = server

.PHONY: clean

all: $(TARGET)

server: src/server.cpp
	$(CXX) -std=c++11 $^ -o $@ $(INCLUDE)

clean:
	$(RM) $(TARGET)
