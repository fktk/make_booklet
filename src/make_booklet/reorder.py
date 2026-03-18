def get_booklet_sequence(n):
    if n % 4 != 0:
        raise ValueError("Page count must be a multiple of 4")
    sequence = []
    num_sheets = n // 4
    for i in range(num_sheets):
        # Front
        sequence.append(n - 1 - 2 * i)
        sequence.append(2 * i)
        # Back
        sequence.append(2 * i + 1)
        sequence.append(n - 2 - 2 * i)
    return sequence
