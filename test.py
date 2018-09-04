from requests import post, get
import random

host = "http://localhost:8088"

def randomMAC():
  mac = [ 0x00, 0x16, 0x3e,
    random.randint(0x00, 0x7f),
    random.randint(0x00, 0xff),
    random.randint(0x00, 0xff)
  ]
  return ':'.join(map(lambda x: "%02x" % x, mac))

data = {
  "mac": randomMAC(),
  "epay": 540814,
  "key": "sdfsdfsdf"
}
r = post(host + "/data/stb/", json = data)
print(r.text)


r = get(host + "/data/stb/")
print(r.text)