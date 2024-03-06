from random import randint


digit_capacity = {
    "1": [-9, 9],
    "10": [-100, 100],
    "100": [-1000, 1000],
    "1000": [-10000, 10000]
}


def generate_numbers(quantity, d_c='1') -> list[int]:
    numbers: list[int] = [randint(*digit_capacity[d_c]) for _ in range(quantity)]
    return numbers


def edit_call(num):
    return str(f'quan_{num}')


def generate_dict_quan():
    dct = {}
    for i in range(2, 19):
        dct[f'quan_{i}'] = str(i)
    return dct