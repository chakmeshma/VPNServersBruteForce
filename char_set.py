def get_chars(dz: bytes | bytearray | str):
    chars = set()

    for z in dz:
        chars.add(z)

    return chars
