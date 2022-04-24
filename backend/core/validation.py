import re


def is_admin(name: str) -> bool:
    return name in ['TONYPONY', 'aytero']


def validate_amount(msg: str) -> bool:
    try:
        amount = float(msg)
    except:
        return False
        # logger.rrr

    if amount <= 0:
        return False
    return True


def validate_charset(name):
    pattern = re.compile("^[А-Яа-я]+(( [А-Яа-я]+)|(-[А-Яа-я]+))*$")
    if pattern.match(name):
        return True
    return False


def validate_name(msg: str):
    # print("validating...\n")
    if len(msg) > 100 or len(msg) < 1:
        return False
    if not validate_charset(msg):
        return False
    return True


def levenstein(str1: str, str2: str):
    matrix = [[i + j if not i & j else 0 for j in range(len(str2) + 1)] \
              for i in range(len(str1) + 1)]
    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            if str1[i - 1] == str2[j - 1]:
                matrix[i][j] = matrix[i - 1][j - 1]
            else:
                matrix[i][j] = 1 + min(matrix[i-1][j], matrix[i-1][j-1], matrix[i][j-1])
    return matrix[len(str1)][len(str2)]


def name_in_names(name: str, names: list) -> str:
    for cur in names:
        if levenstein(name, cur) < len(cur) / 2.5:
            return cur
    return None
