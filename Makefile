TARGET = server

.PHONY: clean

all: server api

server: src/main.py
	python3 src/main.py

api: src/api_server.py
	python3 src/api_server.py
