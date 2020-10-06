import os
import shutil

def select_n(total, n, source_path, target_path) :
    delta = int(total/n)
    copy_next = 0
    counter = 0
    count_blocks = 0
    
    for f in os.listdir(source_path):
        if counter == copy_next :
            copy_next = copy_next + delta
            shutil.copyfile(source_path + "/" + f, target_path + "/" + f)
            count_blocks = count_blocks + 1
        counter = counter + 1
    print("Total " + str(count_blocks))

if __name__ == '__main__' :

    # select for rebuttal
    # total = 72450
    # n = 2000
    # source_path = "/home/maria/opti/opti-eval/ebso-comparison/all"
    # target_path = "/home/maria/opti/opti-eval/rebuttal-experiments/data"
    # select_n(total, n, source_path, target_path)

    total = 61216
    n = 280
    source_path = "/home/maria/opti/opti-eval/ebso-comparison/data/disasm_blks"
    target_path = "/home/maria/Public/subset_ebso"

    select_n(total, n, source_path, target_path)
