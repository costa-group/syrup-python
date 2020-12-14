import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/../ethir")
from utils_verify import *
import rbr_isolate_block
from utils import process_isolate_block


costabs_path = "/tmp/costabs/"
solutions_path = costabs_path + "solutions/"


def verify_sfs(source, sfs_dict):

    report = ""
    
    if sfs_dict != {}:
        if not os.path.exists(solutions_path):
            print("[ERROR] Path "+solutions_path+" does not exist.")
        else:
            solution_files = filter(lambda x: x.find("disasm_opt")!=-1,os.listdir(solutions_path))
            for f in solution_files:

                block_id = get_block_id(f)
                if os.path.getsize(solutions_path+f)!=0:
                    
                    input_stack = len(sfs_dict[block_id]["src_ws"])
                    print("**********")
                    print(input_stack)
                    x, y = process_isolate_block(solutions_path+f, input_stack)

                    block_data = {}
                    block_data["instructions"] = x
                    block_data["input"] = y

                    print(block_data)
                
                    cname_aux = source.split("/")[-1]
                    cname = cname_aux.strip().split(".")[0]
    
                    exit_code = rbr_isolate_block.evm2rbr_compiler(contract_name = cname, ebso = True, block = block_data)

                else:
                    report += "File for "+block_id+" is empty."
                
    else:
        print("There are not solutions generated. They cannot be verified.")




        


if __name__ == '__main__':
    verify_sfs({'block0':'prueba'})
