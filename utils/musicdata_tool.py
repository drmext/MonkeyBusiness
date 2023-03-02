import argparse
import ctypes
import ujson as json
import sys
import struct


def read_string(infile, length, encoding="cp932"):
    string_data = infile.read(length)
    try:
        return string_data.decode(encoding).strip("\0")
    except UnicodeDecodeError:
        # Cannot decode truncated string with half of a multibyte sequence appended (0x83)
        return string_data[:-1].decode(encoding).strip("\0")


def write_string(outfile, input, length, fill="\0", encoding="cp932"):
    string_data = input[:length].encode(encoding)
    outfile.write(string_data)

    if len(input) < length:
        outfile.write("".join([fill] * (length - len(string_data))).encode(encoding))


def reader(data_ver, infile, song_count):
    song_entries = []

    for i in range(song_count):
        title = read_string(infile, 0x40)
        title_ascii = read_string(infile, 0x40)
        genre = read_string(infile, 0x40)
        artist = read_string(infile, 0x40)

        (
            texture_title,
            texture_artist,
            texture_genre,
            texture_load,
            texture_list,
        ) = struct.unpack("<IIIII", infile.read(20))
        font_idx, game_version = struct.unpack("<IH", infile.read(6))
        other_folder, bemani_folder, splittable_diff = struct.unpack(
            "<HHH", infile.read(6)
        )

        if data_ver >= 27:
            (
                SPB_level,
                SPN_level,
                SPH_level,
                SPA_level,
                SPL_level,
                DPB_level,
                DPN_level,
                DPH_level,
                DPA_level,
                DPL_level,
            ) = struct.unpack("<BBBBBBBBBB", infile.read(10))
        else:
            (
                SPN_level,
                SPH_level,
                SPA_level,
                DPN_level,
                DPH_level,
                DPA_level,
                SPB_level,
                DPB_level,
            ) = struct.unpack("<BBBBBBBB", infile.read(8))
            SPL_level = 0
            DPL_level = 0

        if data_ver == 80:
            unk_sect1 = infile.read(0x146)
        elif data_ver >= 27:
            unk_sect1 = infile.read(0x286)
        else:
            unk_sect1 = infile.read(0xA0)

        song_id, volume = struct.unpack("<II", infile.read(8))

        if data_ver >= 27:
            (
                SPB_ident,
                SPN_ident,
                SPH_ident,
                SPA_ident,
                SPL_ident,
                DPB_ident,
                DPN_ident,
                DPH_ident,
                DPA_ident,
                DPL_ident,
            ) = struct.unpack("<BBBBBBBBBB", infile.read(10))
        else:
            (
                SPN_ident,
                SPH_ident,
                SPA_ident,
                DPN_ident,
                DPH_ident,
                DPA_ident,
                SPB_ident,
                DPB_ident,
            ) = struct.unpack("<BBBBBBBB", infile.read(8))
            SPL_ident = 48
            DPL_ident = 48

        bga_delay = ctypes.c_short(struct.unpack("<H", infile.read(2))[0]).value

        if data_ver <= 26 or data_ver == 80:
            unk_sect2 = infile.read(2)

        bga_filename = read_string(infile, 0x20)

        if data_ver == 80:
            unk_sect3 = infile.read(2)

        afp_flag = struct.unpack("<I", infile.read(4))[0]

        if data_ver >= 22:
            afp_data = []
            for x in range(10):
                afp_data.append(infile.read(0x20).hex())
        else:
            afp_data = []
            for x in range(9):
                afp_data.append(infile.read(0x20).hex())

        if data_ver >= 26:
            unk_sect4 = infile.read(4)

        entries = {
            "song_id": song_id,
            "title": title,
            "title_ascii": title_ascii,
            "genre": genre,
            "artist": artist,
            "texture_title": texture_title,
            "texture_artist": texture_artist,
            "texture_genre": texture_genre,
            "texture_load": texture_load,
            "texture_list": texture_list,
            "font_idx": font_idx,
            "game_version": game_version,
            "other_folder": other_folder,
            "bemani_folder": bemani_folder,
            "splittable_diff": splittable_diff,
            "SPB_level": SPB_level,
            "SPN_level": SPN_level,
            "SPH_level": SPH_level,
            "SPA_level": SPA_level,
            "SPL_level": SPL_level,
            "DPB_level": DPB_level,
            "DPN_level": DPN_level,
            "DPH_level": DPH_level,
            "DPA_level": DPA_level,
            "DPL_level": DPL_level,
            "volume": volume,
            "SPB_ident": SPB_ident,
            "SPN_ident": SPN_ident,
            "SPH_ident": SPH_ident,
            "SPA_ident": SPA_ident,
            "SPL_ident": SPL_ident,
            "DPB_ident": DPB_ident,
            "DPN_ident": DPN_ident,
            "DPH_ident": DPH_ident,
            "DPA_ident": DPA_ident,
            "DPL_ident": DPL_ident,
            "bga_filename": bga_filename,
            "bga_delay": bga_delay,
            "afp_flag": afp_flag,
            "afp_data": afp_data,
        }

        #        if data_ver == 80:
        #            unk = {
        #            'unk_sect1': unk_sect1.hex(),
        #            'unk_sect2': unk_sect2.hex(),
        #            'unk_sect3': unk_sect3.hex(),
        #            'unk_sect4': unk_sect4.hex(),
        #            }
        #        elif data_ver < 80 and data_ver >= 27:
        #            unk = {
        #            'unk_sect1': unk_sect1.hex(),
        #            'unk_sect4': unk_sect4.hex(),
        #            }
        #        elif data_ver == 26:
        #            unk = {
        #            'unk_sect1': unk_sect1.hex(),
        #            'unk_sect2': unk_sect2.hex(),
        #            'unk_sect4': unk_sect4.hex(),
        #            }
        #        elif data_ver <= 25:
        #            unk = {
        #            'unk_sect1': unk_sect1.hex(),
        #            'unk_sect2': unk_sect2.hex(),
        #            }
        #
        #        entries.update(unk)

        song_entries.append(entries)

    return song_entries


def writer(data_ver, outfile, data):
    DATA_VERSION = data_ver
    MAX_ENTRIES = data_ver * 1000 + 1000
    CUR_STYLE_ENTRIES = MAX_ENTRIES - 1000

    # Write header
    outfile.write(b"IIDX")
    if data_ver == 80:
        outfile.write(struct.pack("<IHHI", DATA_VERSION, len(data), 0, MAX_ENTRIES))
    else:
        outfile.write(struct.pack("<IHHI", DATA_VERSION, len(data), MAX_ENTRIES, 0))

    # Write song index table
    exist_ids = {}
    for i in range(len(data)):
        exist_ids[data[i]["song_id"]] = i

    cur_song = 0
    for i in range(MAX_ENTRIES):
        if i in exist_ids:
            outfile.write(struct.pack("<H", cur_song))
            cur_song += 1
        elif i >= CUR_STYLE_ENTRIES:
            outfile.write(struct.pack("<H", 0x0000))
        else:
            outfile.write(struct.pack("<H", 0xFFFF))

    # Write song entries
    for k in sorted(exist_ids.keys()):
        song_data = data[exist_ids[k]]

        write_string(outfile, song_data["title"], 0x40)
        write_string(outfile, song_data["title_ascii"], 0x40)
        write_string(outfile, song_data["genre"], 0x40)
        write_string(outfile, song_data["artist"], 0x40)

        outfile.write(
            struct.pack(
                "<IIIII",
                song_data["texture_title"],
                song_data["texture_artist"],
                song_data["texture_genre"],
                song_data["texture_load"],
                song_data["texture_list"],
            )
        )
        outfile.write(
            struct.pack("<IH", song_data["font_idx"], song_data["game_version"])
        )
        outfile.write(
            struct.pack(
                "<HHH",
                song_data["other_folder"],
                song_data["bemani_folder"],
                song_data["splittable_diff"],
            )
        )

        if data_ver >= 27:
            outfile.write(
                struct.pack(
                    "<BBBBBBBBBB",
                    song_data["SPB_level"],
                    song_data["SPN_level"],
                    song_data["SPH_level"],
                    song_data["SPA_level"],
                    song_data["SPL_level"],
                    song_data["DPB_level"],
                    song_data["DPN_level"],
                    song_data["DPH_level"],
                    song_data["DPA_level"],
                    song_data["DPL_level"],
                )
            )
        else:
            outfile.write(
                struct.pack(
                    "<BBBBBBBB",
                    song_data["SPN_level"],
                    song_data["SPH_level"],
                    song_data["SPA_level"],
                    song_data["DPN_level"],
                    song_data["DPH_level"],
                    song_data["DPA_level"],
                    song_data["SPB_level"],
                    song_data["DPB_level"],
                )
            )

        if data_ver == 80:
            outfile.write(
                bytes.fromhex(
                    "0000000000000100000002000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030000000400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000300000004000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
                )
            )
        elif data_ver >= 27:
            outfile.write(
                bytes.fromhex(
                    "00000000000001000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000300000004000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
                )
            )
        else:
            outfile.write(
                bytes.fromhex(
                    "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
                )
            )

        outfile.write(struct.pack("<II", song_data["song_id"], song_data["volume"]))

        if data_ver >= 27:
            outfile.write(
                struct.pack(
                    "<BBBBBBBBBB",
                    song_data["SPB_ident"],
                    song_data["SPN_ident"],
                    song_data["SPH_ident"],
                    song_data["SPA_ident"],
                    song_data["SPL_ident"],
                    song_data["DPB_ident"],
                    song_data["DPN_ident"],
                    song_data["DPH_ident"],
                    song_data["DPA_ident"],
                    song_data["DPL_ident"],
                )
            )
        else:
            outfile.write(
                struct.pack(
                    "<BBBBBBBB",
                    song_data["SPN_ident"],
                    song_data["SPH_ident"],
                    song_data["SPA_ident"],
                    song_data["DPN_ident"],
                    song_data["DPH_ident"],
                    song_data["DPA_ident"],
                    song_data["SPB_ident"],
                    song_data["DPB_ident"],
                )
            )

        outfile.write(struct.pack("<h", song_data["bga_delay"]))

        if data_ver <= 26 or data_ver == 80:
            outfile.write(bytes.fromhex("0000"))

        write_string(outfile, song_data["bga_filename"], 0x20)

        if data_ver == 80:
            outfile.write(bytes.fromhex("0000"))

        outfile.write(struct.pack("<I", song_data["afp_flag"]))

        if data_ver >= 22:
            for afp_data in song_data["afp_data"]:
                outfile.write(bytes.fromhex(afp_data))
            if len(song_data["afp_data"]) == 9:
                outfile.write(
                    bytes.fromhex(
                        "0000000000000000000000000000000000000000000000000000000000000000"
                    )
                )
        elif len(song_data["afp_data"]) == 10 and data_ver <= 21:
            for afp_data in song_data["afp_data"][:9]:
                outfile.write(bytes.fromhex(afp_data))
        elif len(song_data["afp_data"]) == 9 and data_ver <= 21:
            for afp_data in song_data["afp_data"]:
                outfile.write(bytes.fromhex(afp_data))

        if data_ver >= 26:
            outfile.write(bytes.fromhex("00000000"))


def course_reader(infile, total_entries):
    course_entries = []

    for i in range(total_entries):
        is_DP, course_num, stages = struct.unpack("<HIH", infile.read(8))

        stage_num = []
        for i in range(0x20):
            extract = struct.unpack("<I", infile.read(4))
            if extract[0] != 0xFFFFFFFF:
                stage_num.extend(extract)

        song_id = []
        for i in range(0x20):
            extract = struct.unpack("<I", infile.read(4))
            if extract[0] != 0xFFFFFFFF:
                song_id.extend(extract)

        song_diff = []
        for i in range(0x20):
            extract = struct.unpack("<I", infile.read(4))
            if extract[0] != 0xFFFFFFFF:
                song_diff.extend(extract)

        course_entries.append(
            {
                "is_DP": is_DP,
                "course_num": course_num,
                "stages": stages,
                "stage_num": stage_num,
                "song_id": song_id,
                "song_diff": song_diff,
            }
        )

    return course_entries


def course_writer(outfile, data, data_ver):
    TOTAL_ENTRIES = len(data)

    # Write header
    outfile.write(b"IIDXDANE")
    outfile.write(struct.pack("<III", data_ver, TOTAL_ENTRIES, 0))

    # Write course entries
    for song_data in data:
        outfile.write(
            struct.pack(
                "<HIH", song_data["is_DP"], song_data["course_num"], song_data["stages"]
            )
        )

        stage = 0

        for i in range(0x20):
            if i in range(song_data["stages"]):
                outfile.write(struct.pack("<I", stage))
                stage += 1
            else:
                outfile.write(struct.pack("<I", 0xFFFFFFFF))

        for i in range(0x20):
            if i in range(song_data["stages"]):
                outfile.write(struct.pack("<I", song_data["song_id"][i]))
                stage += 1
            else:
                outfile.write(struct.pack("<I", 0xFFFFFFFF))

        for i in range(0x20):
            if i in range(song_data["stages"]):
                outfile.write(struct.pack("<I", song_data["song_diff"][i]))
                stage += 1
            else:
                outfile.write(struct.pack("<I", 0xFFFFFFFF))


read_handlers = {
    0x14,  # TRICORO
    0x15,  # SPADA
    0x16,  # PENDUAL
    0x17,  # COPULA
    0x18,  # SINOBUZ
    0x19,  # CANNON BALLERS
    0x1A,  # ROOTAGE
    0x1B,  # HEROIC VERSE
    0x1C,  # BISTROVER
    0x1D,  # CASTHOUR
    0x1E,  # RESIDENT
    0x1F,  # ???
    0x50,  # INFINITAS
}

write_handlers = {
    0x14,  # TRICORO
    0x15,  # SPADA
    0x16,  # PENDUAL
    0x17,  # COPULA
    0x18,  # SINOBUZ
    0x19,  # CANNON BALLERS
    0x1A,  # ROOTAGE
    0x1B,  # HEROIC VERSE
    0x1C,  # BISTROVER
    0x1D,  # CASTHOUR
    0x1E,  # RESIDENT
    0x1F,  # ???
    0x50,  # INFINITAS
}


def extract_file(input, output, in_memory=False):
    with open(input, "rb") as infile:
        if infile.read(4) != b"IIDX":
            print("Invalid", input)
            exit(-1)

        infile.seek(4, 0)
        data_ver = int.from_bytes(infile.read(4), "little")

        if data_ver == 80:
            available_entries, unk4, total_entries = struct.unpack(
                "<HHI", infile.read(8)
            )
        else:
            available_entries, total_entries, unk4 = struct.unpack(
                "<HIH", infile.read(8)
            )

        song_ids = {}
        for i in range(total_entries):
            song_id = struct.unpack("<H", infile.read(2))[0]

            if song_id != 0xFFFF and (len(song_ids) == 0 or song_id != 0):
                song_ids[i] = song_id

        if data_ver in read_handlers:
            output_data = reader(data_ver, infile, available_entries)
            output_data = {
                "data_ver": data_ver,
                "data": output_data,
            }

            if in_memory:
                return output_data

            json.dump(
                output_data,
                open(output, "w", encoding="utf8"),
                indent=4,
                ensure_ascii=False,
                escape_forward_slashes=False,
            )
        else:
            print("Couldn't find a handler for this data version")
            exit(-1)

    return []


def create_file(input, output, data_version):
    data = json.load(open(input, "r", encoding="utf8"))
    data_ver = data.get("data_ver", data_version)

    if not data_ver:
        print("Couldn't find data version")
        exit(-1)

    if data_ver in write_handlers:
        writer(data_ver, open(output, "wb"), data["data"])
    else:
        print("Couldn't find a handler for this data version")
        exit(-1)


def convert_file(input, output, data_version):
    with open(input, "rb") as infile:
        if infile.read(4) != b"IIDX":
            print("Invalid", input)
            exit(-1)

        data_ver, available_entries, total_entries, unk4 = struct.unpack(
            "<IHIH", infile.read(12)
        )

        song_ids = {}
        for i in range(total_entries):
            song_id = struct.unpack("<H", infile.read(2))[0]

            if song_id != 0xFFFF and (len(song_ids) == 0 or song_id != 0):
                song_ids[i] = song_id

        if data_ver in read_handlers:
            output_data = reader(data_ver, infile, available_entries)
            writer(data_ver, open(output, "wb"), output_data)
        else:
            print("Couldn't find a handler for this input data version")
            exit(-1)


def merge_files(input, basefile, output, diff=False):
    with open(input, "rb") as infile:
        if infile.read(4) != b"IIDX":
            print("Invalid", input)
            exit(-1)

        data_ver, available_entries, total_entries, unk4 = struct.unpack(
            "<IHIH", infile.read(12)
        )

        song_ids = {}
        for i in range(total_entries):
            song_id = struct.unpack("<H", infile.read(2))[0]

            if song_id != 0xFFFF and (len(song_ids) == 0 or song_id != 0):
                song_ids[i] = song_id

        if data_ver in read_handlers:
            old_data = reader(data_ver, infile, available_entries)
        else:
            print("Couldn't find a handler for this input data version")
            exit(-1)

    with open(basefile, "rb") as infile:
        if infile.read(4) != b"IIDX":
            print("Invalid", basefile)
            exit(-1)

        data_ver, available_entries, total_entries, unk4 = struct.unpack(
            "<IHIH", infile.read(12)
        )

        song_ids = {}
        for i in range(total_entries):
            song_id = struct.unpack("<H", infile.read(2))[0]

            if song_id != 0xFFFF and (len(song_ids) == 0 or song_id != 0):
                song_ids[i] = song_id

        if data_ver in read_handlers:
            new_data = reader(data_ver, infile, available_entries)
        else:
            print("Couldn't find a handler for this input data version")
            exit(-1)

    # Create list of
    exist_ids_new = {}
    for song_data in new_data:
        exist_ids_new[song_data["song_id"]] = True

    for song_data in old_data:
        if song_data["song_id"] not in exist_ids_new:
            new_data.append(song_data)

    writer(data_ver, open(output, "wb"), new_data)

    if diff:
        new_data.clear()

        for song_data in old_data:
            if song_data["song_id"] not in exist_ids_new:
                new_data.append(song_data)

        writer(data_ver, open(output[:-4] + "_diff.bin", "wb"), new_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Input file", required=True)
    parser.add_argument("--output", help="Output file", required=True)
    parser.add_argument(
        "--extract", help="Extraction mode", default=False, action="store_true"
    )
    parser.add_argument(
        "--create", help="Creation mode", default=False, action="store_true"
    )
    parser.add_argument(
        "--convert", help="Conversion mode", default=False, action="store_true"
    )
    parser.add_argument(
        "--merge", help="Merge mode", default=False, action="store_true"
    )
    parser.add_argument(
        "--data-version",
        help="Force a data version (usedful for converts)",
        default=None,
        type=int,
    )
    parser.add_argument(
        "--diff", help="Create diff file with merge", default=False, action="store_true"
    )
    args = parser.parse_args()

    if (
        args.create == False
        and args.extract == False
        and args.convert == False
        and args.merge == False
    ):
        print("You must specify either --extract or --create or --convert or --merge")
        exit(-1)

    if args.convert == True:
        if args.data_version == None:
            print("You must specify a target --data-version with --convert")
            exit(-1)
        elif args.data_version not in write_handlers:
            print("Don't know how to handle specified data version")
            exit(-1)

    if args.extract:
        extract_file(args.input, args.output)

    elif args.create:
        create_file(args.input, args.output, args.data_version)

    elif args.convert:
        convert_file(args.input, args.output, args.data_version)

    elif args.merge:
        merge_files(args.input, args.output, args.output, args.diff)
