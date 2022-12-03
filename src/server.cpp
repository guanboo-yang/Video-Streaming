#include <iostream>
#include <fstream>
#include <map>
#include <cstring>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netdb.h>
#include <fcntl.h>
#include <signal.h>
using namespace std;

#include "http.hpp"
#include "utils.hpp"

#define BUFF_SIZE 8192
#define ROOT      "dist"

class basic_server {
public:
    /* public attributes */
    int port;
    string ip;

    /* public methods */
    basic_server(int port);
    void loop();

protected:
    /* protected attributes */
    int max_fd;
    int server_fd;
    int max_conn_fd;
    fd_set read_fds, working_read_fds;
    char buf[BUFF_SIZE];

    /* protected methods */
    virtual void handle_read(int conn_fd);
    void close_conn(int conn_fd);
};

/* constructor */
basic_server::basic_server(int port) :
    port(port) {
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) ERR_EXIT("socket error\n")
    /* bind the socket to the port */
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
    /* get the hostname and ip of the server */
    char hostname[64] = {0};
    if (gethostname(hostname, sizeof(hostname)) == -1)
        ERR_EXIT("gethostname error\n")
    struct hostent *host = gethostbyname(hostname);
    if (host == NULL) ERR_EXIT("gethostbyname error\n")
    ip = inet_ntoa(*(struct in_addr *) host->h_addr_list[0]);
    // for (int i = 0; host->h_addr_list[i]; i++)
    //     cerr << "ip: " << inet_ntoa(*(struct in_addr *) host->h_addr_list[i]) << endl;
    max_fd = server_fd;
    max_conn_fd = FD_SETSIZE;
    FD_ZERO(&read_fds);
    FD_SET(server_fd, &read_fds);
    cerr << "Server created at " << ip << ":" << port << " (" << server_fd << ")" << endl;
    cerr << "---------------------------------------" << endl;
}

/* main loop */
void basic_server::loop() {
    working_read_fds = read_fds;
    int ret = select(max_fd + 1, &working_read_fds, NULL, NULL, NULL);
    if (ret == -1) ERR_EXIT("select error\n")
    /* new connection */
    if (FD_ISSET(server_fd, &working_read_fds)) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        int conn_fd = accept(server_fd, (struct sockaddr *) &client_addr, &client_len);
        if (conn_fd == -1) ERR_EXIT("accept error\n")
        FD_SET(conn_fd, &read_fds);
        if (conn_fd > max_fd) max_fd = conn_fd;
        cerr << "\033[32mNew connection from " << inet_ntoa(client_addr.sin_addr) << ":" << ntohs(client_addr.sin_port) << " (" << conn_fd << ")\033[0m" << endl;
        cerr << "---------------------------------------" << endl;
    }
    /* read from existing connections */
    for (int conn_i = 0; conn_i <= max_fd; conn_i++) {
        if (conn_i == server_fd) continue;
        if (FD_ISSET(conn_i, &working_read_fds)) {
            handle_read(conn_i);
            cerr << "---------------------------------------" << endl;
        }
    }
}

/* close a connection */
void basic_server::close_conn(int conn_fd) {
    close(conn_fd);
    FD_CLR(conn_fd, &read_fds);
    cerr << "\033[31mConnection closed (" << conn_fd << ")\033[0m" << endl;
}

/* handle read from a connection (to be implemented) */
void basic_server::handle_read(int conn_fd) {
    memset(buf, 0, sizeof(buf));
    int ret = recv(conn_fd, buf, sizeof(buf), 0);
    if (ret == -1) {
        cerr << "recv error: " << strerror(errno) << endl;
        close_conn(conn_fd);
        return;
    }
    if (ret == 0) {
        close_conn(conn_fd);
        return;
    }
    cerr << "Read " << ret << " bytes (" << conn_fd << ")" << endl;
    return;
}

class http_server : public basic_server {
    /* using basic_server constructor */
    using basic_server::basic_server;

protected:
    void handle_read(int conn_fd);

    http_request parse_request();
    int handle_get(int conn_fd, http_request &req);
    void send_string(int conn_fd, string res);
    void send_error(int conn_fd, http_request &req, int code, string msg, string desc);
    string get_content_type(string file_type);
};

/* handle read from a connection */
void http_server::handle_read(int conn_fd) {
    basic_server::handle_read(conn_fd);
    http_request req = parse_request();
    if (req.method == "GET")
        handle_get(conn_fd, req);
    return;
}

/* parse a request */
http_request http_server::parse_request() {
    http_request req;
    string method, path, version;
    map<string, string> headers;
    string header, key, value;
    char *_header;
    method = strtok(buf, " ");
    path = strtok(NULL, " ");
    version = strtok(NULL, "\r\n");
    while (true) {
        _header = strtok(NULL, "\r\n");
        if (_header == NULL) break;
        header = _header;
        key = header.substr(0, header.find(": "));
        value = header.substr(header.find(": ") + 2);
        headers[key] = value;
    }
    req.method = method;
    req.path = path;
    req.version = version;
    req.headers = headers;
    return req;
}

/* handle GET request */
int http_server::handle_get(int conn_fd, http_request &req) {
    http_response res;
    res.version = req.version;
    string file = ROOT + req.path;
    // for SPA
    if (file.find('.') == string::npos) {
        file = ROOT;
        file += "/index.html";
    }
    cerr << "File path: " << file << endl;
    if (access(file.c_str(), F_OK) == -1) {
        cerr << "File not found" << endl;
        send_error(conn_fd, req, NOT_FOUND);
        return 0;
    }
    ifstream fin(file, ios::binary);
    if (!fin) {
        cerr << "File open error" << endl;
        send_error(conn_fd, req, INTERNAL_SERVER_ERROR);
        return 0;
    }
    string file_type = file.substr(file.find_last_of('.') + 1);
    res.headers["Content-Type"] = get_content_type(file_type);
    fin.seekg(0, ios::end);
    int file_size = fin.tellg();
    fin.seekg(0, ios::beg);
    cerr << "File size: " << file_size << endl;
    res.status_code = 200;
    res.status_msg = "OK";
    res.headers["Content-Length"] = to_string(file_size);
    send_string(conn_fd, res.to_string());
    memset(buf, 0, sizeof(buf));
    while (fin.read(buf, BUFF_SIZE)) {
        send(conn_fd, buf, BUFF_SIZE, 0);
    }
    send(conn_fd, buf, fin.gcount(), 0);
    fin.close();
    return 0;
}

/* send a string */
void http_server::send_string(int conn_fd, string res) {
    send(conn_fd, res.c_str(), res.length(), 0);
}

/* send an error */
void http_server::send_error(int conn_fd, http_request &req, int code, string msg = "", string desc = "") {
    http_response res;
    res.version = req.version;
    res.status_code = code;
    res.status_msg = msg;
    res.headers["Content-Type"] = "text/html";
    string error_page = ROOT;
    error_page += "/error/" + to_string(code) + ".html";
    ifstream fin(error_page);
    if (fin.is_open()) {
        string line;
        while (getline(fin, line))
            res.body += line;
        fin.close();
    } else {
        res.body = desc;
    }
    res.headers["Content-Length"] = to_string(res.body.length());
    send_string(conn_fd, res.to_string());
    close_conn(conn_fd);
}

/* get content type */
string http_server::get_content_type(string file_type) {
    if (file_type == "html") return "text/html";
    else if (file_type == "css") return "text/css";
    else if (file_type == "js") return "text/javascript";
    else if (file_type == "png") return "image/png";
    else if (file_type == "ico") return "image/x-icon";
    else if (file_type == "webp") return "image/webp";
    else if (file_type == "svg") return "image/svg+xml";
    else if (file_type == "mp4") return "video/mp4";
    else return "application/octet-stream";
}

int main(int argc, char *argv[]) {
    if (argc != 2) ERR_EXIT("Usage: %s <port>", argv[0])
    /* ignore SIGPIPE */
    signal(SIGPIPE, SIG_IGN);
    int port_num = atoi(argv[1]);
    http_server server(port_num);
    /* start server */
    while (1) server.loop();
    return 0;
}
