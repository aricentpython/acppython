def print_received_data(data):
    temp_data = data.decode(encoding='utf-8')
    temp_data = temp_data.splitlines()
    while '' in temp_data:
        temp_data.remove('')

    return temp_data


http_request = b'GET / HTTP/1.1\r\nAccept: text/html, application/xhtml+xml, image/jxr, */*\r\n\r\nAccept-Language: ' \
               b'en-IN\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko' \
               b') Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063\r\nAccept-Encoding: gzip, deflate\r\nHost: ' \
               b'localhost:5555\r\nConnection: Keep-Alive\r\n\r\n'

print(http_request, '\n\n')

http_req_parsed = print_received_data(http_request)
print("\nlength of http_req_parsed is {}".format(len(http_req_parsed)))
print('\n', http_req_parsed)

http_request_dictionary = {}
for i, item in zip(range(0, len(http_req_parsed)), http_req_parsed):
    if i == 0:
        http_request_dictionary['request'] = item
    else:
        http_request_dictionary[(item.split(':', maxsplit=1))[0]] = (item.split(':', maxsplit=1))[1]
print('')
for key, value in http_request_dictionary.items():
    print("{} -> {}".format(key, value))

print('')
print(type(http_request_dictionary), '\n')
print((http_request_dictionary['request'].split())[0])
