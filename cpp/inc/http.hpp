#define CONTINUE            100, "Continue", "Request received, please continue"
#define SWITCHING_PROTOCOLS 101, "Switching Protocols", "Switching to new protocol; obey Upgrade header"
#define PROCESSING          102, "Processing", "WebDAV; RFC 2518"
#define EARLY_HINTS         103, "Early Hints", "Used to return some response headers before final HTTP message"

#define OK               200, "OK", "Request fulfilled, document follows"
#define CREATED          201, "Created", "Document created, URL follows"
#define ACCEPTED         202, "Accepted", "Request accepted, processing continues off-line"
#define NON_AUTHOR       203, "Non-Authoritative Information", "Request fulfilled from cache"
#define NO_CONTENT       204, "No Content", "Request fulfilled, nothing follows"
#define RESET_CONTENT    205, "Reset Content", "Clear input form for further input."
#define PARTIAL_CONTENT  206, "Partial Content", "Partial content follows."
#define MULTI_STATUS     207, "Multi-Status", "WebDAV; RFC 4918"
#define ALREADY_REPORTED 208, "Already Reported", "WebDAV; RFC 5842"
#define IM_USED          226, "IM Used", "RFC 3229"

#define MULTIPLE_CHOICES   300, "Multiple Choices", "Object has several resources -- see URI list"
#define MOVED_PERMANENTLY  301, "Moved Permanently", "Object moved permanently -- see URI list"
#define FOUND              302, "Found", "Object moved temporarily -- see URI list"
#define SEE_OTHER          303, "See Other", "Object moved -- see Method and URL list"
#define NOT_MODIFIED       304, "Not Modified", "Document has not changed since given time"
#define USE_PROXY          305, "Use Proxy", "You must use proxy specified in Location to access this resource."
#define SWITCH_PROXY       306, "Switch Proxy", "Subsequent requests should use the specified proxy."
#define TEMPORARY_REDIRECT 307, "Temporary Redirect", "Object moved temporarily -- see URI list"
#define PERMANENT_REDIRECT 308, "Permanent Redirect", "Object moved permanently -- see URI list"

#define BAD_REQUEST             400, "Bad Request", "Bad request syntax or unsupported method"
#define UNAUTHORIZED            401, "Unauthorized", "No permission -- see authorization schemes"
#define PAYMENT_REQUIRED        402, "Payment Required", "No payment -- see charging schemes"
#define FORBIDDEN               403, "Forbidden", "Request forbidden -- authorization will not help"
#define NOT_FOUND               404, "Not Found", "404 Not Found"
#define METHOD_NOT_ALLOWED      405, "Method Not Allowed", "Specified method is invalid for this resource."
#define NOT_ACCEPTABLE          406, "Not Acceptable", "URI not available in preferred format."
#define PROXY_AUTH_REQURIED     407, "Proxy Authentication Required", "You must authenticate with this proxy before proceeding."
#define REQUEST_TIMEOUT         408, "Request Timeout", "Request timed out; try again later."
#define CONFLICT                409, "Conflict", "Request conflict."
#define GONE                    410, "Gone", "URI no longer exists and has been permanently removed."
#define LENGTH_REQUIRED         411, "Length Required", "Client must specify Content-Length."
#define PRECONDITION_FAILED     412, "Precondition Failed", "Precondition in headers is false."
#define REQUEST_TOO_LARGE       413, "Request Entity Too Large", "Entity is too large."
#define URI_TOO_LONG            414, "Request-URI Too Long", "URI is too long."
#define UNSUPPORTED_MEDIA       415, "Unsupported Media Type", "Entity body in unsupported format."
#define RANGE_NOT_SATISFIABLE   416, "Requested Range Not Satisfiable", "Cannot satisfy request range."
#define EXPECTATION_FAILED      417, "Expectation Failed", "Expect condition could not be satisfied."
#define IM_A_TEAPOT             418, "I'm a teapot", "RFC 2324"
#define MISDIRECTED_REQUEST     421, "Misdirected Request", "RFC 7540"
#define UNPROCESSABLE_ENTITY    422, "Unprocessable Entity", "WebDAV; RFC 4918"
#define LOCKED                  423, "Locked", "WebDAV; RFC 4918"
#define FAILED_DEPENDENCY       424, "Failed Dependency", "WebDAV; RFC 4918"
#define TOO_EARLY               425, "Too Early", "RFC 8470"
#define UPGRADE_REQUIRED        426, "Upgrade Required", "RFC 2817"
#define PRECONDITION_REQUIRED   428, "Precondition Required", "RFC 6585"
#define TOO_MANY_REQUESTS       429, "Too Many Requests", "RFC 6585"
#define HEADER_FIELDS_TOO_LARGE 431, "Request Header Fields Too Large", "RFC 6585"
#define UNAVAILABLE_FOR_LEGAL   451, "Unavailable For Legal Reasons", "RFC 7725"

#define INTERNAL_SERVER_ERROR   500, "Internal Server Error", "Server got itself in trouble"
#define NOT_IMPLEMENTED         501, "Not Implemented", "Server does not support this operation"
#define BAD_GATEWAY             502, "Bad Gateway", "Invalid responses from another server/proxy."
#define SERVICE_UNAVAILABLE     503, "Service Unavailable", "The server cannot process the request due to a high load"
#define GATEWAY_TIMEOUT         504, "Gateway Timeout", "The gateway server did not receive a timely response"
#define HTTP_VERSION_NOT_SUP    505, "HTTP Version Not Supported", "Cannot fulfill request."
#define VARIANT_ALSO_NEGOTIATES 506, "Variant Also Negotiates", "RFC 2295"
#define INSUFFICIENT_STORAGE    507, "Insufficient Storage", "WebDAV; RFC 4918"
#define LOOP_DETECTED           508, "Loop Detected", "WebDAV; RFC 5842"
#define NOT_EXTENDED            510, "Not Extended", "RFC 2774"
#define NETWORK_AUTH_REQUIRED   511, "Network Authentication Required", "RFC 6585"

struct http_request {
    string method;
    string path;
    string version;
    map<string, string> headers;
    string body;
    string to_string() {
        string res = method + " " + path + " " + version + "\r\n";
        for (auto &header : headers) {
            res += header.first + ": " + header.second + "\r\n";
        }
        res += "\r\n";
        res += body;
        return res;
    }
};

struct http_response {
    string version;
    int status_code;
    string status_msg;
    map<string, string> headers;
    string body;
    string to_string() {
        string res = version + " " + ::to_string(status_code) + " " + status_msg + "\r\n";
        for (auto &header : headers)
            res += header.first + ": " + header.second + "\r\n";
        res += "\r\n";
        res += body;
        return res;
    }
};
