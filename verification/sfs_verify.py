import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/../ethir")
from utils_verify import *
import rbr_isolate_block
from utils import process_isolate_block
from ebso_optimization import get_sfs_dict

costabs_path = "/tmp/costabs/"
solutions_path = costabs_path + "solutions/"


'''
The jsons are going to be different. What needs to be the same are the
uninterpreted functions, and source and target stack.
'''

def are_equals(json_orig, json_opt):

    print("COMPARA")
    print(json_orig)
    print(json_opt)


    src_st = json_orig["src_ws"] == json_opt["src_ws"]
    tgt_st = json_orig["tgt_ws"] == json_opt["tgt_ws"]

    unint_func = len(json_opt["user_instrs"]) == len(json_orig["user_instrs"])
    for fun in json_opt["user_instrs"]:
        unint_func = unint_func and (fun in json_orig["user_instrs"])
    
    if (src_st and tgt_st and unint_func):
        print(True)
        return True
    else:
        return False

    



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
                    json_obj = sfs_dict[block_id]
                    input_stack = len(json_obj["src_ws"])
                    print("**********")
                    print("COMIENZA VERIFY: "+block_id)
                    print(input_stack)
                    x, y = process_isolate_block(solutions_path+f, input_stack)

                    block_data = {}
                    block_data["instructions"] = x
                    block_data["input"] = y

                    print(block_data)
                
                    cname_aux = source.split("/")[-1]
                    cname = cname_aux.strip().split(".")[0]
    
                    exit_code = rbr_isolate_block.evm2rbr_compiler(contract_name = cname, ebso = True, block = block_data)
                    json_opt = get_sfs_dict()
                    print("++++++++++++++")
                    print(json_opt)

                    if len(json_opt)>1:
                        print("[ERROR] Something fails with the optimized block.")
                    else:

                        result = are_equals(json_obj,json_opt[next(iter(json_opt.keys()))])

                        if result:
                            result = "Block "+block_id+" :VERIFIED" 
                            report+=result+"\n"
                    
                else:
                    report += "File for "+block_id+" is empty.\n"

            with open(costabs_path + "report_verification.txt", 'w') as f:
                f.write(report)
                
    else:
        print("There are not solutions generated. They cannot be verified.")




        


if __name__ == '__main__':
    verify_sfs({'block0':'prueba'})
