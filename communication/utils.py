import uuid


def is_uuid(text):
    try:
        uuid.UUID(str(text))
        return True
    except ValueError:
        return False


def explain_websocket_code(code):
    close_codes = {
        1000: "Successful operation / regular socket shutdown",
        1001: "Client is leaving (browser tab closing)",
        1002: "Endpoint received a malformed frame",
        1003: "Endpoint received an unsupported frame (e.g. binary-only endpoint received text frame)",
        1004: "Reserved",
        1005: "Expected close status, received none",
        1006: "No close code frame has been receieved",
        1007: "Endpoint received inconsistent message (e.g. malformed UTF-8)",
        1008: "Generic code used for situations other than 1003 and 1009",
        1009: "Endpoint won't process large frame",
        1010: "Client wanted an extension which server did not negotiate",
        1011: "Internal server error while operating",
        1012: "Server/service is restarting",
        1013: "Temporary server condition forced blocking client's request",
        1014: "Server acting as gateway received an invalid response",
        1015: "Transport Layer Security handshake failure",
        4000: "Kicked by new host",
    }
    if code in close_codes:
        return close_codes[code]
    return f"Unknown: {code}"
