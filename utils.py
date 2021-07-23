import hashlib


def calc_hash(filename):
    m = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(1024 * 1024)
            if len(chunk) == 0:
                break
            m.update(chunk)
    return m.hexdigest()
