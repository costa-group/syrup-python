# Miscellanea methods

# We add a | | to string variables, as these variables are usually
# of the form s(i) and SMT-Lib cannot accept those names. If it
# is numeric, no bars are added.
def add_bars_to_string(string):
    if type(string) == str:
        return '|' + str(string) + '|'
    else:
        return string