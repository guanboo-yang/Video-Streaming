#include <iostream>
using namespace std;

#define ERR_EXIT(...)                 \
    {                                 \
        fprintf(stderr, __VA_ARGS__); \
        exit(1);                      \
    }

class Logger {
public:
    /* print date and time before each log */
    static void print_time() {
        time_t t = time(NULL);
        cout << "[" << put_time(localtime(&t), "%F %T") << "] ";
    }

    /* use ostream to print log */
    template <typename T>
    ostream &operator<<(const T &t) {
        print_time();
        return cerr << t;
    }
};

Logger log;
