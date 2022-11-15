class EamuseLZ77:
    @staticmethod
    def decode(data):
        data_length = len(data)
        offset = 0
        output = []
        while offset < data_length:
            flag = data[offset]
            offset += 1
            for bit in range(8):
                if flag & (1 << bit):
                    output.append(data[offset])
                    offset += 1
                else:
                    if offset >= data_length:
                        break
                    lookback_flag = int.from_bytes(data[offset : offset + 2], "big")
                    lookback_length = (lookback_flag & 0x000F) + 3
                    lookback_offset = lookback_flag >> 4
                    offset += 2
                    if lookback_flag == 0:
                        break
                    for _ in range(lookback_length):
                        loffset = len(output) - lookback_offset
                        if loffset <= 0 or loffset >= len(output):
                            output.append(0)
                        else:
                            output.append(output[loffset])
        return bytes(output)

    # @staticmethod
    # def encode(data):
    #     return bytes(output)
