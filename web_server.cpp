#include <iostream>
#include <fstream>
#include <map>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netdb.h>
#include <fcntl.h>
using namespace std;

#define BUFF_SIZE 8192
#define ROOT      "./src"

struct http_response {
    string status;
    string content_type;
    string content;
    int content_length;
};

#define ERR_EXIT(...)                 \
    {                                 \
        fprintf(stderr, __VA_ARGS__); \
        exit(1);                      \
    }

class http_server {
public:
    http_server(int _port) {
        port = _port;
        init_server();
        cerr << "Server created at " << ip << ":" << port << " (" << server_fd << ")" << endl;
    }

    void init_server() {
        server_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (server_fd == -1) ERR_EXIT("socket error\n")
        // bind the socket to the port
        struct sockaddr_in addr;
        bzero(&addr, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        addr.sin_addr.s_addr = htonl(INADDR_ANY);
        int tmp = 1;
        if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &tmp, sizeof(tmp)) == -1)
            ERR_EXIT("setsockopt error\n")
        if (::bind(server_fd, (struct sockaddr *) &addr, sizeof(addr)) == -1)
            ERR_EXIT("bind error\n")
        if (listen(server_fd, 1024) == -1)
            ERR_EXIT("listen error\n")
        // get the hostname and ip of the server
        char hostname[64] = {0};
        if (gethostname(hostname, sizeof(hostname)) == -1)
            ERR_EXIT("gethostname error\n")
        struct hostent *host = gethostbyname(hostname);
        if (host == NULL) ERR_EXIT("gethostbyname error\n")
        ip = inet_ntoa(*(struct in_addr *) host->h_addr_list[0]);

        max_fd = server_fd;
        max_conn_fd = FD_SETSIZE;
        FD_ZERO(&read_fds);
        FD_SET(server_fd, &read_fds);
        return;
    }

    void loop() {
        // working_read_fds = read_fds;
        memcpy(&working_read_fds, &read_fds, sizeof(fd_set));
        int ret = select(max_fd + 1, &working_read_fds, NULL, NULL, NULL);
        if (ret == -1) ERR_EXIT("select error\n")
        // new connection
        if (FD_ISSET(server_fd, &working_read_fds)) {
            struct sockaddr_in client_addr;
            socklen_t client_len = sizeof(client_addr);
            int conn_fd = accept(server_fd, (struct sockaddr *) &client_addr, &client_len);
            if (conn_fd == -1) ERR_EXIT("accept error\n")
            FD_SET(conn_fd, &read_fds);
            if (conn_fd > max_fd) max_fd = conn_fd;
            cerr << "\033[32mNew connection from " << inet_ntoa(client_addr.sin_addr) << ":" << ntohs(client_addr.sin_port) << " (" << conn_fd << ")\033[0m" << endl;
        }
        // read from existing connections
        for (int conn_i = 0; conn_i <= max_fd; conn_i++) {
            if (conn_i == server_fd) continue;
            if (FD_ISSET(conn_i, &working_read_fds)) {
                memset(buf, 0, sizeof(buf));
                int ret = recv(conn_i, buf, sizeof(buf), 0);
                if (ret == -1) {
                    cerr << "recv error: " << strerror(errno) << endl;
                    close_conn(conn_i);
                    continue;
                }
                if (ret == 0) {
                    close_conn(conn_i);
                    continue;
                }
                cerr << "Read " << ret << " bytes (" << conn_i << ")" << endl;
                handle_request(conn_i);
            }
        }
    }

private:
    int port;
    int max_fd;
    int server_fd;
    int max_conn_fd;
    string ip;
    fd_set read_fds, working_read_fds;
    char buf[BUFF_SIZE];
    http_response response;

    void close_conn(int conn_fd) {
        close(conn_fd);
        FD_CLR(conn_fd, &read_fds);
        cerr << "\033[31mConnection closed (" << conn_fd << ")\033[0m" << endl;
    }

    void send_response(int conn_fd, string response) {
        send(conn_fd, response.c_str(), response.length(), 0);
    }

    void handle_request(int conn_fd) {
        string method, path, version;
        method = strtok(buf, " ");
        path = strtok(NULL, " ");
        version = strtok(NULL, "\r\n");
        map<string, string> headers;
        char *_header;
        string header, key, value;
        while (true) {
            _header = strtok(NULL, "\r\n");
            if (_header == NULL) break;
            header = _header;
            key = header.substr(0, header.find(": "));
            value = header.substr(header.find(": ") + 2);
            headers[key] = value;
        }
        cerr << method << " " << path << " " << version << endl;
        if (method == "GET") handle_get(conn_fd, path);
        return;
    }

    int handle_get(int conn_fd, string path) {
        string file = ROOT + path;
        if (path == "/") file += "index.html";
        cerr << "File path: " << file << endl;
        string file_type = file.substr(file.find_last_of('.') + 1);
        response.content_type = get_content_type(file_type);
        if (access(file.c_str(), F_OK) == -1) {
            send(conn_fd, "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n", 44, 0);
            close_conn(conn_fd);
            return 0;
        }
        ifstream fin(file, ios::binary);
        if (!fin) {
            cerr << "File open error" << endl;
            send(conn_fd, "HTTP/1.1 500 Internal Server Error\r\nContent-Length: 0\r\n\r\n", 55, 0);
            close_conn(conn_fd);
            return 0;
        }
        fin.seekg(0, ios::end);
        int file_size = fin.tellg();
        fin.seekg(0, ios::beg);
        cerr << "File size: " << file_size << endl;
        send_response(conn_fd, "HTTP/1.1 200 OK\r\n" + response.content_type + "Content-Length: " + to_string(file_size) + "\r\n\r\n");
        memset(buf, 0, sizeof(buf));
        while (fin.read(buf, BUFF_SIZE)) {
            send(conn_fd, buf, BUFF_SIZE, 0);
        }
        send(conn_fd, buf, fin.gcount(), 0);
        fin.close();
        return 0;
    }

    string get_content_type(string file_type) {
        // html, css, js, png, ico, webp, svg, bin
        if (file_type == "html") return "Content-Type: text/html\r\n";
        else if (file_type == "css") return "Content-Type: text/css\r\n";
        else if (file_type == "js") return "Content-Type: text/javascript\r\n";
        else if (file_type == "png") return "Content-Type: image/png\r\n";
        else if (file_type == "ico") return "Content-Type: image/x-icon\r\n";
        else if (file_type == "webp") return "Content-Type: image/webp\r\n";
        else if (file_type == "svg") return "Content-Type: image/svg+xml\r\n";
        else return "Content-Type: application/octet-stream\r\n";
    }
};

// signal handler closes the server
void sig_handler(int signo) {
    cerr << "Closing server..." << endl;
    exit(0);
}

int main(int argc, char *argv[]) {
    int port_num = atoi(argv[1]);
    http_server server(port_num);
    while (1) server.loop();
    return 0;
}
