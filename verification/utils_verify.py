
'''
It takes the name of a file containing the optimized version of a
block and extracts the id of the block from the name of the file.
'''

def get_block_id(file_name):

    p = file_name.find("block")
    end = file_name.find("_",p)

    block_id = file_name[p:end]

    print(block_id)
    return block_id


def is_integer(num):
    try:
        val = int(num)
        return True
    except:
        return False
