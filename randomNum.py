import random
import socket
import struct


IP = ('0.0.0.0', 25565)

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.bind(IP)
listener.listen(0)


def getRes():
	return """{
  "version": {
    "name": \""""+str(random.randint(int("1"+"0"*1023), int("9"*1024)))+"""\",
    "protocol": 757
  },
  "players": {
    "max": 0,
    "online": """+str(random.randint(int("1"+"0"*1020), int("9"*1021)))+""",
    "sample": [
      {
        "name": "Redstoyn33",
        "id": "4566e69f-c907-48ee-8d71-d7ba5aa00d20"
      }
    ]
  },
  "description": {
    "text": "Test"
  },
  "favicon": "data:image/png;base64,<data>"
}"""


def unpack_varint(s):
	d = 0
	for i in range(5):
		b = ord(s.recv(1))
		d |= (b & 0x7F) << 7*i
		if not b & 0x80:
			break
	return d


def pack_varint(d):
	o = b""
	while True:
		b = d & 0x7F
		d >>= 7
		o += struct.pack("B", b | (0x80 if d > 0 else 0))
		if d == 0:
			break
	return o


def unpack_str(s):
	size = unpack_varint(s)
	return s.recv(size).decode('utf8')


def pack_str(d):
	data = pack_varint(len(d))
	data += d.encode('utf8')
	return data


print("start")
while True:
	conn, address = listener.accept()
	t = f"--------- new connection from {address} ---------"
	print(t)
	try:
		l = unpack_varint(conn)
		idp = unpack_varint(conn)
	except Exception:
		print("error")
		continue
	print(f"packet: id = {idp}   len = {l}".center(len(t)))
	if idp != 0:
		conn.close()
		continue
	print(f"protocol = {unpack_varint(conn)}   addr = {unpack_str(conn)}:{int.from_bytes(conn.recv(2), 'big')}".center(
		len(t)))
	print(f"state = {unpack_varint(conn)}".center(len(t)))
	try:
		l = unpack_varint(conn)
		idp = unpack_varint(conn)
	except Exception:
		print("error")
		continue
	if idp != 0:
		conn.close()
		continue
	print("--- Request ---".center(len(t)))
	print(f"len = {l}   id = {idp}".center(len(t)))
	res = pack_str(getRes())
	resb = pack_varint(len(res)+1)+b'\x00'+res
	conn.send(resb)
	print("Response sent".center(len(t)))
	try:
		l = unpack_varint(conn)
		idp = unpack_varint(conn)
	except Exception:
		print("error")
		continue
	if idp != 1:
		conn.close()
		continue
	print("--- Ping ---".center(len(t)))
	data = conn.recv(8)
	conn.send(pack_varint(len(data)+1)+b'\x01'+data)
	print("--- Pong ---".center(len(t)))
	conn.close()
