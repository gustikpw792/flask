import re


def to_list(data, kriteria):
    list_of_lists = []
    table = data.split('\r\n')
    # print(table)
    for item in table:
        if kriteria in item:
            item_str = re.sub(' +', ",", item.lstrip())
            # print(item_str)
            comma_sep_list = item_str.split(',')
            # print(comma_sep_list)
            list_of_lists.append(comma_sep_list)
    return list_of_lists
