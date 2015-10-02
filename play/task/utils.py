from hashlib import sha1


def hash_file(filepath, size):
    """"This function returns the SHA-1 hash
    of the file passed into it, doing it the way git does."""

    h = sha1()
    init_hash = "blob {size}\0".format(size=size)
    h.update(init_hash.encode('ascii'))

    with open(filepath, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)

    return h.hexdigest()
