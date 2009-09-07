"""Tests. They want YOU!!

Basic functionality.
>>> c = _pylibmc.client([test_server])
>>> c.set("test_key", 123)
True
>>> c.get("test_key")
123
>>> c.get("test_key_2")
>>> c.delete("test_key")
True
>>> c.get("test_key")
>>>

Now this section is because most other implementations ignore zero-keys.
>>> c.get("")
>>> c.set("", "hi")
False
>>> c.delete("")
False
>>>

Multi functionality.
>>> c.set_multi({"a": 1, "b": 2, "c": 3})
[]
>>> c.get_multi("abc").keys() == ["a", "c", "b"]
True
>>> c.delete_multi("abc")
[]
>>> c.get_multi("abc").keys() == []
True
>>> c.set_multi(dict(zip("abc", "def")), key_prefix="test_")
[]
>>> list(sorted(c.get_multi("abc", key_prefix="test_").iteritems()))
[('a', 'd'), ('b', 'e'), ('c', 'f')]
>>> c.get("test_a")
'd'
>>> c.delete_multi("abc", key_prefix="test_")
[]
>>> bool(c.get_multi("abc", key_prefix="test_"))
False

Zero-key-test-time!
>>> c.get_multi([""])
{}
>>> c.delete_multi([""])
['']
>>> c.set_multi({"": "hi"})
['']

Timed stuff. The reason we, at UNIX times, set it two seconds in the future and
then sleep for >3 is that memcached might round the time up and down and left
and yeah, so you know...
>>> from time import sleep, time
>>> c.set("hi", "steven", 1)
True
>>> c.get("hi")
'steven'
>>> sleep(1.1)
>>> c.get("hi")
>>> c.set("hi", "loretta", int(time()) + 2)
True
>>> c.get("hi")
'loretta'
>>> sleep(3.1)
>>> c.get("hi")
>>>

Now for keys with funny types.
>>> c.set(1, "hi")
Traceback (most recent call last):
  ...
TypeError: argument 1 must be string or read-only buffer, not int
>>> c.get(1)
Traceback (most recent call last):
  ...
TypeError: key must be an instance of str
>>> c.set_multi({1: True})
Traceback (most recent call last):
  ...
TypeError: key must be an instance of str
>>> c.get_multi([1, 2])
Traceback (most recent call last):
  ...
TypeError: key must be an instance of str

Also test some flush all.
>>> c.set("hi", "guys")
True
>>> c.get("hi")
'guys'
>>> c.flush_all()
True
>>> c.get("hi")
>>>

Get and set booleans. Note that a boolean turns into an integer, mostly because
that's how python-memcached handles it. (Most likely because Python considers
the bool type to be an integer.)
>>> c.set("test", True)
True
>>> c.get("test")
1
"""

import _pylibmc
import socket

test_server = (_pylibmc.server_type_tcp, "localhost", 11211)

def get_version(addr):
    (type_, host, port) = addr
    if (type_ != _pylibmc.server_type_tcp):
        raise NotImplementedError("test server can only be on tcp for now")
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send("version\r\n")
        version = s.recv(4096)
        s.close()
        if not version.startswith("VERSION ") or not version.endswith("\r\n"):
            raise ValueError("unexpected version return: %r" % (version,))
        else:
            version = version[8:-2]
        return version

def is_alive(addr):
    try:
        return bool(get_version(addr))
    except (ValueError, socket.error):
        return False

if __name__ == "__main__":
    if not is_alive(test_server):
        raise SystemExit("Test server (%r) not alive." % (test_server,))
    import doctest
    n_fail, n_run = doctest.testmod()
    print "Ran", n_run, "tests with", n_fail, "failures."