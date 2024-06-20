div = "\r\n\r\n"
crlf = "\r\n"


def resolve_message(message):
    messageList = message.split(div)
    top = messageList[0]
    message_type = messageList[1].split(":")[1]
    body = messageList[2].split(crlf)
    return top, message_type, body


def generate_message(top, message_type, body):
    header = f'message_type:{message_type}'
    message =  top + div + header + div + body
    return message
