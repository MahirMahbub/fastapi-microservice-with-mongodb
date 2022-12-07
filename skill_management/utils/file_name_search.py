import os


async def next_file_name(file_name_pattern, bucket_id, main_file_name):
    if not os.path.exists(bucket_id + main_file_name):
        return main_file_name
    i = 1
    while os.path.exists(bucket_id + file_name_pattern % i):
        i = i * 2
    left, right = (i // 2, i)
    while left + 1 < right:
        middle = (left + right) // 2
        left, right = (middle, right) if os.path.exists(bucket_id + file_name_pattern % middle) else (left, middle)

    return file_name_pattern % right