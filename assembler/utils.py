from bitstring import Bits

def resize_bits(bits: Bits, length: int, is_signed: bool = False, except_on_overflow: bool = True) -> Bits:
    if(bits.length > length):
        resize = Bits(bits[-length:])
        if except_on_overflow and is_signed and resize.int != bits.int:
            raise ValueError('Signed integer \'{}\' is too large to be represented as a {}-bit signed integer.'.format(bits.int, length))
        elif except_on_overflow and not is_signed and resize.uint != bits.uint:
            raise ValueError('Unsigned integer \'{}\' is too large to be represented as a {}-bit unsigned integer.'.format(bits.uint, length))
        else:
            return resize
    elif(bits.length < length):
        ext = ('1' if bits[0] and is_signed else '0') * (length - bits.length)
        return Bits(bin=(ext + bits.bin))
    else:
        return bits # no resize needed