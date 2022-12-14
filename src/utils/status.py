from enum import Enum


class HttpStatus(Enum):
    def __init__(self, code: int, reason: str, description: str):
        self.code = code
        self.reason = reason
        self.description = description

    def __int__(self):
        return self.code

    def __str__(self):
        return f"{self.code} {self.reason}"

    CONTINUE = (100, "Continue", "Request received, please continue")
    SWITCHING_PROTOCOLS = (101, "Switching Protocols", "Switching to new protocol; obey Upgrade header")
    PROCESSING = (102, "Processing", "WebDAV; RFC 2518")
    EARLY_HINTS = (103, "Early Hints", "RFC 8297")

    OK = (200, "OK", "Request fulfilled, document follows")
    CREATED = (201, "Created", "Document created, URL follows")
    ACCEPTED = (202, "Accepted", "Request accepted, processing continues off-line")
    NON_AUTHORITATIVE = (203, "Non-Authoritative Information", "Request fulfilled from cache")
    NO_CONTENT = (204, "No Content", "Request fulfilled, nothing follows")
    RESET_CONTENT = (205, "Reset Content", "Clear input form for further input.")
    PARTIAL_CONTENT = (206, "Partial Content", "Partial content follows.")
    MULTI_STATUS = (207, "Multi-Status", "WebDAV; RFC 4918")
    ALREADY_REPORTED = (208, "Already Reported", "WebDAV; RFC 5842")
    IM_USED = (226, "IM Used", "RFC 3229")

    MULTIPLE_CHOICES = (300, "Multiple Choices", "Object has several resources -- see URI list")
    MOVED_PERMANENTLY = (301, "Moved Permanently", "Object moved permanently -- see URI list")
    FOUND = (302, "Found", "Object moved temporarily -- see URI list")
    SEE_OTHER = (303, "See Other", "Object moved -- see Method and URL list")
    NOT_MODIFIED = (304, "Not Modified", "Document has not changed since given time")
    USE_PROXY = (305, "Use Proxy", "You must use proxy specified in Location to access this resource.")
    TEMPORARY_REDIRECT = (307, "Temporary Redirect", "Object moved temporarily -- see URI list")
    PERMANENT_REDIRECT = (308, "Permanent Redirect", "Object moved permanently -- see URI list")

    BAD_REQUEST = (400, "Bad Request", "Bad request syntax or unsupported method")
    UNAUTHORIZED = (401, "Unauthorized", "No permission -- see authorization schemes")
    PAYMENT_REQUIRED = (402, "Payment Required", "No payment -- see charging schemes")
    FORBIDDEN = (403, "Forbidden", "Request forbidden -- authorization will not help")
    NOT_FOUND = (404, "Not Found", "Nothing matches the given URI")
    METHOD_NOT_ALLOWED = (405, "Method Not Allowed", "Specified method is invalid for this resource.")
    NOT_ACCEPTABLE = (406, "Not Acceptable", "URI not available in preferred format.")
    PROXY_AUTH_REQURIED = (407, "Proxy Authentication Required", "You must authenticate with this proxy before proceeding.")
    REQUEST_TIMEOUT = (408, "Request Timeout", "Request timed out; try again later.")
    CONFLICT = (409, "Conflict", "Request conflict.")
    GONE = (410, "Gone", "URI no longer exists and has been permanently removed.")
    LENGTH_REQUIRED = (411, "Length Required", "Client must specify Content-Length.")
    PRECONDITION_FAILED = (412, "Precondition Failed", "Precondition in headers is false.")
    REQUEST_TOO_LARGE = (413, "Request Entity Too Large", "Entity is too large.")
    URI_TOO_LONG = (414, "Request-URI Too Long", "URI is too long.")
    UNSUPPORTED_MEDIA = (415, "Unsupported Media Type", "Entity body in unsupported format.")
    RANGE_NOT_SATISFIABLE = (416, "Requested Range Not Satisfiable", "Cannot satisfy request range.")
    EXPECTATION_FAILED = (417, "Expectation Failed", "Expect condition could not be satisfied.")
    IM_A_TEAPOT = (418, "I'm a teapot", "RFC 2324")
    MISDIRECTED_REQUEST = (421, "Misdirected Request", "RFC 7540")
    UNPROCESSABLE_ENTITY = (422, "Unprocessable Entity", "WebDAV; RFC 4918")
    LOCKED = (423, "Locked", "WebDAV; RFC 4918")
    FAILED_DEPENDENCY = (424, "Failed Dependency", "WebDAV; RFC 4918")
    TOO_EARLY = (425, "Too Early", "RFC 8470")
    UPGRADE_REQUIRED = (426, "Upgrade Required", "RFC 2817")
    PRECONDITION_REQUIRED = (428, "Precondition Required", "RFC 6585")
    TOO_MANY_REQUESTS = (429, "Too Many Requests", "RFC 6585")
    HEADER_FIELDS_TOO_LARGE = (431, "Request Header Fields Too Large", "RFC 6585")
    UNAVAILABLE_FOR_LEGAL = (451, "Unavailable For Legal Reasons", "RFC 7725")

    INTERNAL_SERVER_ERROR = (500, "Internal Server Error", "Server got itself in trouble")
    NOT_IMPLEMENTED = (501, "Not Implemented", "Server does not support this operation")
    BAD_GATEWAY = (502, "Bad Gateway", "Invalid responses from another server/proxy.")
    SERVICE_UNAVAILABLE = (503, "Service Unavailable", "The server cannot process the request due to a high load")
    GATEWAY_TIMEOUT = (504, "Gateway Timeout", "The gateway server did not receive a timely response")
    HTTP_VERSION_NOT_SUP = (505, "HTTP Version Not Supported", "Cannot fulfill request.")
    VARIANT_ALSO_NEGOTIATES = (506, "Variant Also Negotiates", "RFC 2295")
    INSUFFICIENT_STORAGE = (507, "Insufficient Storage", "WebDAV; RFC 4918")
    LOOP_DETECTED = (508, "Loop Detected", "WebDAV; RFC 5842")
    NOT_EXTENDED = (510, "Not Extended", "RFC 2774")
    NETWORK_AUTH_REQUIRED = (511, "Network Authentication Required", "RFC 6585")
