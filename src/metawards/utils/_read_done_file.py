
__all__ = ["read_done_file"]


def read_done_file(filename: str):
    """This function reads the 'done_file' from 'filename' returning the list
       of seeded nodes
    """
    try:
        nodes_seeded = []

        with open(filename, "r") as FILE:
            line = FILE.readline()

            # each line has a single number, which is the seed
            nodes_seeded.append(float(line.strip()))

        return nodes_seeded

    except Exception as e:
        raise ValueError(f"Possible corruption of {filename}: {e}")
