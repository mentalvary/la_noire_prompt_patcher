from pathlib import Path
import shutil
import struct
import sys


def main(args):
    try:
        out_wad_pc = Path(args[0] if args else "out.wad.pc")
        extract_dir = out_wad_pc.with_name(out_wad_pc.name + ".extracted")
        out_wad_pc_backup = out_wad_pc.with_name(out_wad_pc.name + ".bak")
        if not out_wad_pc_backup.exists():
            print(f"Creating backup at {out_wad_pc_backup}...")
            shutil.copy(out_wad_pc, out_wad_pc_backup)

        print(f"Unpacking {out_wad_pc} to {extract_dir}...")
        unpack_wad(out_wad_pc, extract_dir)
        print("\nType a new text for each of the following:")
        replace_prompts(extract_dir / "out" / "attribute" / "root.atb.pc")
        print(f"\nRepacking {extract_dir} to {out_wad_pc}...")
        pack_wad(extract_dir, out_wad_pc)
        shutil.rmtree(extract_dir)
        print("All done!")
    except Exception as e:
        print(e, file=sys.stderr)

    input("Press Enter to close this...")


def unpack_wad(filename, out_dir):
    with open(filename, "rb") as file:
        num_files, start_of_names = read_wad_infos(file)
        name_pos = start_of_names
        for i in range(0, num_files):
            file_start = 4 + 8 + 12 * i
            pos = read_uint(file, file_start)
            size = read_uint(file, file_start + 4)
            name_pos = extract_wad_file(
                name_pos,
                pos,
                size,
                file,
                out_dir,
            )


def extract_wad_file(name_pos, data_pos, data_size, file, out_dir):
    name, name_pos = read_wad_filename(file, name_pos)
    data = read_bytes(file, data_pos, data_size)

    full_path = Path(out_dir) / Path(name)
    # print(full_path)
    full_path.parent.mkdir(parents=True, exist_ok=True)
    dump_bytes(full_path, data)

    return name_pos


def pack_wad(dir, filename):
    with open(filename, "rb") as file:
        buffer = [bytearray(file.read())]

        num_files, start_of_names = read_wad_infos(file)
        name_pos = start_of_names

        for i in range(0, num_files):
            file_start = 4 + 8 + 12 * i
            # FIXME: read these from buffer, as the positions will change if files
            # with changed sizes are packed. At the moment this is bugged if more than one
            # file changes in size. Everything should be read from and written to buffer
            pos = read_uint(file, file_start)
            size = read_uint(file, file_start + 4)
            name_pos = replace_wad_file(
                name_pos,
                pos,
                size,
                file,
                dir,
                buffer,
                i,
                num_files,
            )

    with open(filename, "wb") as file:
        file.write(buffer[0])


def replace_wad_file(
    name_pos,
    data_pos,
    data_size,
    file,
    dir,
    buffer: list[bytearray],
    file_index,
    num_files,
):
    name, name_pos = read_wad_filename(file, name_pos)

    full_path = Path(dir) / Path(name)

    new_data = slurp_bytes(full_path)
    new_data_size = len(new_data)

    size_diff = new_data_size - data_size
    same_data = (size_diff == 0) and (new_data == read_bytes(file, data_pos, data_size))
    if not same_data:
        # print(f"replacing {full_path}")
        buffer[0] = buffer[0][:data_pos] + new_data + buffer[0][data_pos + data_size :]
        overwrite_uint(buffer, 8 + file_index * 12 + 8, new_data_size)

    if size_diff != 0:
        # Shift file positions of all other files coming after this one
        for k in range(0, num_files):
            file_start = 4 + 8 + 12 * k
            file_pos = read_uint(file, file_start)
            if file_pos > data_pos:
                overwrite_uint(buffer, file_start, file_pos + size_diff)

    return name_pos


def read_wad_filename(file, name_pos):
    name_len = read_ushort(file, name_pos)
    name_pos += 2
    name = read_string(file, name_pos, name_len)
    name_pos += name_len
    return name, name_pos


def read_wad_infos(file):
    num_files = read_uint(file, 4)
    start_of_names = read_uint(
        file,
        4 + 8 + 12 * (num_files - 1),
    ) + read_uint(
        file,
        8 + 8 + 12 * (num_files - 1),
    )
    return num_files, start_of_names


def replace_prompts(path):
    with open(path, "rb") as file:
        buffer = bytearray(file.read())

    def replace(prefix):
        nonlocal buffer
        str_pos = buffer.index(prefix)
        len_pos = str_pos - 2
        str_len = buffer[len_pos]
        current_str = buffer[str_pos + len(prefix) : str_pos + str_len].decode("ascii")

        new_str = input(f"{current_str} -> ")
        if not new_str:
            return

        new_str_bytes = prefix + new_str.encode("ascii")

        buffer = buffer[:str_pos] + new_str_bytes + buffer[str_pos + str_len :]
        buffer[len_pos] = len(new_str_bytes)

    replace(b"[ACCEPT|TRUTH] ")
    replace(b"[SQUARE|DOUBT] ")
    replace(b"[TRIANGLE|LIE] ")

    with open(path, "wb") as file:
        file.write(buffer)


def read_uint(file, pos):
    file.seek(pos)
    return unpack("I", file.read(4))


def overwrite_uint(buffer, pos, val):
    bytes = struct.pack("I", val)
    for i in range(0, len(bytes)):
        buffer[0][pos + i] = bytes[i]
    # buffer[0] = buffer[0][:pos] + bytes + buffer[0][pos + len(bytes) :]


def read_ushort(file, pos):
    file.seek(pos)
    return unpack("H", file.read(2))


def read_string(file, pos, len):
    file.seek(pos)
    return file.read(len).decode("ascii")


def read_bytes(file, pos, len):
    file.seek(pos)
    return file.read(len)


def slurp_bytes(path):
    with open(path, "rb") as file:
        return file.read()


def dump_bytes(path, bytes):
    with open(path, "wb") as file:
        file.write(bytes)


def unpack(fmt, bts):
    return struct.unpack(fmt, bts)[0]


if __name__ == "__main__":
    main(sys.argv[1:])
