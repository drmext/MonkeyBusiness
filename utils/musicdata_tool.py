import argparse
import json
import struct


def read_string(infile, length, encoding="cp932"):
    return infile.read(length).decode(encoding, errors="ignore").rstrip("\0")


def write_string(outfile, input, length, encoding="cp932"):
    string_data = input[:length].encode(encoding)
    outfile.write(string_data)
    outfile.write(b"\0" * (length - len(string_data)))


def reader(version, infile, song_count):
    all_song_entries = []

    for i in range(song_count):
        if version >= 32 and version != 80:
            title = read_string(infile, 0x100, encoding="utf-16-le")
            title_ascii = read_string(infile, 0x40)
            genre = read_string(infile, 0x80, encoding="utf-16-le")
            artist = read_string(infile, 0x100, encoding="utf-16-le")
            subtitle = read_string(infile, 0x100, encoding="utf-16-le")
        else:
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
        if version >= 32 and version != 80:
            texture_subtitle = struct.unpack("<I", infile.read(4))[0]
        font_idx, game_version = struct.unpack("<IH", infile.read(6))
        if version >= 32 and version != 80:
            (
                other_folder,
                bemani_folder,
                beginner_rec_folder,
                iidx_rec_folder,
                bemani_rec_folder,
                splittable_diff,
                unk_unused,
            ) = struct.unpack("<HHHHHHH", infile.read(14))
        else:
            other_folder, bemani_folder, splittable_diff = struct.unpack("<HHH", infile.read(6))

        if version >= 27:
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

        if version == 80:
            unk_sect1 = infile.read(0x146)
        elif version >= 27:
            unk_sect1 = infile.read(0x286)
        else:
            unk_sect1 = infile.read(0xA0)

        song_id, volume = struct.unpack("<II", infile.read(8))

        if version >= 27:
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

        bga_delay = struct.unpack("<h", infile.read(2))[0]

        if version <= 26 or version == 80:
            unk_sect2 = infile.read(2)

        bga_filename = read_string(infile, 0x20)

        if version == 80:
            unk_sect3 = infile.read(2)

        afp_flag = struct.unpack("<I", infile.read(4))[0]

        afp_data = [read_string(infile, 0x20) for _ in range(10 if version >= 22 else 9)]

        if version >= 26:
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

        if version >= 32 and version != 80:
            new_version_entries = {
                "subtitle": subtitle,
                "texture_subtitle": texture_subtitle,
                "beginner_rec_folder": beginner_rec_folder,
                "iidx_rec_folder": iidx_rec_folder,
                "bemani_rec_folder": bemani_rec_folder,
                "unk_unused": unk_unused,
            }
            entries.update(new_version_entries)

        all_song_entries.append(entries)

    return all_song_entries


def writer(version, outfile, data):
    cur_style_entries = version * 1000
    max_entries = cur_style_entries + 1000
    entries_struct_format = "<i" if version >= 32 and version != 80 else "<h"

    # Write header
    outfile.write(b"IIDX")
    if version >= 32:
        outfile.write(struct.pack("<IHHI", version, len(data), 0, max_entries))
    else:
        outfile.write(struct.pack("<IHHI", version, len(data), max_entries, 0))

    # Write song index table
    exist_ids = {}
    for i in range(len(data)):
        exist_ids[data[i]["song_id"]] = i

    current_song = 0
    for i in range(max_entries):
        if i in exist_ids:
            outfile.write(struct.pack(entries_struct_format, current_song))
            current_song += 1
        elif i >= cur_style_entries:
            outfile.write(struct.pack(entries_struct_format, 0))
        else:
            outfile.write(struct.pack(entries_struct_format, -1))

    # Write song entries
    for k in sorted(exist_ids):
        song_data = data[exist_ids[k]]

        if version >= 32 and version != 80:
            write_string(outfile, song_data["title"], 0x100, encoding="utf-16-le")
            write_string(outfile, song_data["title_ascii"], 0x40)
            write_string(outfile, song_data["genre"], 0x80, encoding="utf-16-le")
            write_string(outfile, song_data["artist"], 0x100, encoding="utf-16-le")
            write_string(outfile, song_data.get("subtitle", ""), 0x100, encoding="utf-16-le")
        else:
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
        if version >= 32 and version != 80:
            outfile.write(struct.pack("<I", song_data.get("texture_subtitle", 0)))
        outfile.write(struct.pack("<IH", song_data["font_idx"], song_data["game_version"]))
        if version >= 32 and version != 80:
            outfile.write(
                struct.pack(
                    "<HHHHHHH",
                    song_data["other_folder"],
                    song_data["bemani_folder"],
                    song_data.get("beginner_rec_folder", 0),
                    song_data.get("iidx_rec_folder", 0),
                    song_data.get("bemani_rec_folder", 0),
                    song_data["splittable_diff"],
                    song_data.get("unk_unused", 0),
                )
            )
        else:
            outfile.write(
                struct.pack(
                    "<HHH",
                    song_data["other_folder"],
                    song_data["bemani_folder"],
                    song_data["splittable_diff"],
                )
            )

        if version >= 27:
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

        if version == 80:
            outfile.write(bytes.fromhex(f"{1:014}{2:08}{3:0248}{4:08}{3:0120}{4:08}{0:0246}"))
        elif version >= 32:
            outfile.write(bytes.fromhex(f"{0:01292}"))
        elif version >= 27:
            outfile.write(bytes.fromhex(f"{1:014}{2:08}{3:0248}{4:08}{0:01014}"))
        else:
            outfile.write(bytes.fromhex(f"{0:0320}"))

        outfile.write(struct.pack("<II", song_data["song_id"], song_data["volume"]))

        if version >= 27:
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

        if version <= 26 or version == 80:
            outfile.write(bytes.fromhex("00" * 2))

        write_string(outfile, song_data["bga_filename"], 0x20)

        if version == 80:
            outfile.write(bytes.fromhex("00" * 2))

        outfile.write(struct.pack("<I", song_data["afp_flag"]))

        for idx in range(10 if version >= 22 else 9):
            try:
                write_string(outfile, song_data["afp_data"][idx], 0x20)
            except IndexError:
                write_string(outfile, "", 0x20)

        if version >= 26:
            outfile.write(bytes.fromhex("00" * 4))


handlers = {
    20,  # TRICORO
    21,  # SPADA
    22,  # PENDUAL
    23,  # COPULA
    24,  # SINOBUZ
    25,  # CANNON BALLERS
    26,  # ROOTAGE
    27,  # HEROIC VERSE
    28,  # BISTROVER
    29,  # CASTHOUR
    30,  # RESIDENT
    31,  # EPOLIS
    32,  # PINKY CRUSH
    80,  # INFINITAS
}


def extract_file(input, output, in_memory=False):
    with open(input, "rb") as infile:
        if infile.read(4) != b"IIDX":
            raise SystemExit(f"Input file ({input}) is not valid")

        version = struct.unpack("<I", infile.read(4))[0]
        entries_struct_format = "<i" if version >= 32 and version != 80 else "<h"

        if version >= 32:
            available_entries, unk4, total_entries = struct.unpack("<HHI", infile.read(8))
        else:
            available_entries, total_entries, unk4 = struct.unpack("<HIH", infile.read(8))

        existing_song_ids = {}
        for i in range(total_entries):
            song_id = struct.unpack(entries_struct_format, infile.read(struct.calcsize(entries_struct_format)))[0]

            if song_id != struct.pack(entries_struct_format, -1) and (len(existing_song_ids) == 0 or song_id != 0):
                existing_song_ids[i] = song_id

        if version in handlers:
            output_data = reader(version, infile, available_entries)
            output_data = {
                "data_ver": version,
                "data": output_data,
            }

            if in_memory:
                return output_data

            with open(output, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=4, ensure_ascii=False)

        else:
            raise SystemExit("Couldn't find a handler for this data version")

    return []


def create_file(input, output, placeholder):
    with open(input, "r", encoding="utf-8") as f:
        data = json.load(f)
        version = data.get("data_ver", placeholder)

    if not version:
        raise SystemExit("Couldn't find data version")

    if version in handlers:
        with open(output, "wb") as f:
            writer(version, f, data["data"])
    else:
        raise SystemExit("Couldn't find a handler for this data version")


def merge_files(input, basefile, output, diff=False):
    old_data = extract_file(input, None, in_memory=True)
    new_data = extract_file(basefile, None, in_memory=True)

    new_song_ids = {song_data["song_id"] for song_data in new_data["data"]}
    merged_songs = [song_data for song_data in old_data["data"] if song_data["song_id"] not in new_song_ids]

    new_data["data"].extend(merged_songs)
    with open(output, "wb") as f:
        writer(new_data["data_ver"], f, new_data["data"])

    if diff:
        with open(output[:-4] + "_diff.bin", "wb") as f:
            writer(new_data["data_ver"], f, merged_songs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Input file", required=True)
    parser.add_argument("--output", help="Output file", required=True)
    parser.add_argument("--extract", help="Extraction mode", default=False, action="store_true")
    parser.add_argument("--create", help="Creation mode", default=False, action="store_true")
    parser.add_argument("--merge", help="Merge mode", default=False, action="store_true")
    parser.add_argument("--diff", help="Create _diff.bin output with merge", default=False, action="store_true")
    args = parser.parse_args()

    if not any([args.extract, args.create, args.merge]):
        raise SystemExit("You must specify either --extract or --create or --merge")

    if args.extract:
        extract_file(args.input, args.output)

    elif args.create:
        create_file(args.input, args.output, None)

    elif args.merge:
        merge_files(args.input, args.output, args.output, args.diff)
