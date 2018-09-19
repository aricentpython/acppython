import socket
import sys
import _thread
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime



def web_page(path):
    print("web_page::path: {}".format(path), '\n')
    content = ''
    if path['uri'] == '/':
        # content = "Welcome to our Web Page"
        # content = '<h1>Welcome to our Web Page</h1>'
        content = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; " \
                                   "charset=utf-8\"></head><body><h1>Aricent Web Server</h1>" \
                                   "<h2>Welcome to our Web Page</h2></body></html>"
    return content


def parse_request_line(http_request_line):
    request_dictionary = {}
    parsed_request_line = str(http_request_line).split()
    request_dictionary['method'] = parsed_request_line[0]
    request_dictionary['uri'] = parsed_request_line[1]
    request_dictionary['http_ver'] = parsed_request_line[2]
    # print("method: {}, URI: {}, http_ver: {}".format(request_dictionary['method'], request_dictionary['uri'],
    #                                                  request_dictionary['http_ver']))
    return request_dictionary


def prepare_response(response):
    response_format = ['status-line', 'general-header', 'response-header', 'entity-header', 'message-body']
    response_string = ''

    print("prepare_response::response: {}".format(response), '\n')
    response['general-header'] = response['general-header'] + '\r\nConnection: close' + '\r\nContent-Type: text/html'

    for item in response_format:
        if item in response:
            if response_string == '':
                response_string = response[item] + '\r\n'
            elif item == 'message-body':
                response_string = response_string + '\r\n' + response[item] + '\r\n'
            else:
                response_string = response_string + response[item] + '\r\n'

    print("prepare_response::response_string: {}".format(response_string), '\n')
    return response_string


def prepare_datetime():
    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)


def go_get_method(parsed_request_line, http_request):
    response = {}
    print("go_get_method::parsed_request_line: {}".format(parsed_request_line), '\n')
    status_line = parsed_request_line['http_ver'] + ' '
    response['message-body'] = web_page(parsed_request_line)
    # response['general-header'] = 'Date: ' + datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z")
    response['general-header'] = 'Date: ' + prepare_datetime()

    if response['message-body'] != '':
        status_line = status_line + '200 OK'
        if parsed_request_line['method'] == 'HEAD':
            del response['message-body']
    else:
        status_line = status_line + '404 NOT FOUND'
        if parsed_request_line['method'] != 'HEAD':
            response['message-body'] = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; " \
                                   "charset=utf-8\"></head><body><h2>Aricent Web Server</h2><div>404 - " \
                                   "path NOT FOUND</div></body></html>"
    response['status-line'] = status_line
    return response


def go_head_method(http_request):
    return


def go_put_method(http_request):
    return


def go_post_method(http_request):
    return


def method_not_implemented(parsed_request_line):
    response = {}
    status_line = parsed_request_line['http_ver'] + " 501 Not Implemented"
    response['message-body'] = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; " \
                               "charset=utf-8\"></head><body><h2>Aricent Web Server</h2><div>501 - " \
                               "Not Implemented</div></body></html>"
    response['general-header'] = 'Date: ' + prepare_datetime()
    response['general-header'] = response['general-header'] + '\r\nConnection: close' + '\r\nContent-Type: text/html'
    response['status-line'] = status_line

    return response


def parse_received_data(data):
    http_data = data.decode(encoding='utf-8')
    http_data = http_data.splitlines()

    while '' in http_data:
        http_data.remove('')

    http_request_dictionary = {}
    for i, item in zip(range(0, len(http_data)), http_data):
        if i == 0:
            http_request_dictionary['request'] = item
            # http_request_dictionary['request'] = item.split()
        else:
            http_request_dictionary[(item.split(':', maxsplit=1))[0]] = (item.split(':', maxsplit=1))[1]

    return http_request_dictionary


def send_response(client_socket, prepared_response):
    client_socket.sendall(prepared_response.encode(encoding='utf-8'))
    client_socket.close()


def threaded_client(client_socket):
    # client_socket.send(str.encode('Welcome.. Type your Info.\r\n'))

    while True:

        try:
            data = client_socket.recv(2048)
        except ConnectionResetError:
            print("*** Connection Closed ***")
            client_socket.close()
            break
        except:
            print("*** Connection is Broken ***")
            client_socket.close()
            break

        print("Data received from client: {}".format(data))
        # formatted_data = parse_received_data(data)

        if not data:
            print("\n**NO DATA PRESENT**\n")
            print("*** closing the Connection ***")
            client_socket.close()
            break

        if b"\xff" not in data:
            http_req_parsed = parse_received_data(data)
            print("http_req_parsed: {}".format(http_req_parsed), '\n')
            parsed_http_request_line = parse_request_line(http_req_parsed['request'])
            del http_req_parsed['request']

            print("http_req_parsed: {}".format(http_req_parsed), '\n')
            print("parsed_http_request_line: {}".format(parsed_http_request_line), '\n')

            if parsed_http_request_line['method'] == 'GET':
                response = go_get_method(parsed_http_request_line, http_req_parsed)
            elif parsed_http_request_line['method'] == 'HEAD':
                # Implement HEAD Method
                response = go_get_method(parsed_http_request_line, http_req_parsed)
            # elif (request_line.split())[0] == 'PUT':
            #     # Implement HEAD Method
            #     go_put_method(http_req_parsed)
            # elif (request_line.split())[0] == 'POST':
            #     # Implement HEAD Method
            #     go_post_method(http_req_parsed)
            else:
                response = method_not_implemented(parsed_http_request_line)

            prepared_response = prepare_response(response)
            print("1. prepared_response: {}".format(prepared_response), '\n')

        send_response(client_socket, prepared_response)


# main function start hear
host = ''
port = 5555
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.bind((host, port))
    sock.listen(5)
except socket.error as e:
    print(str(e))


print("waiting for a connection...")

while True:
    client_sock, addr = sock.accept()
    print("Connected to: {} : {}".format(addr[0], addr[1]))
    _thread.start_new_thread(threaded_client, (client_sock, ))
