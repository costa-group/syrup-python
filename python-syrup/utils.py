# Miscellanea

def add_bars_to_string(string):
    if type(string) == str:
        return '|' + str(string) + '|'
    else:
        return string