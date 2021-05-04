#!/usr/bin/python3

import os
import sys
print(sys.path.append(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/../ethir")
from parser_asm import parse_asm
import rbr_isolate_block
from syrup_optimization import get_sfs_dict
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/../backend")
from python_syrup import execute_syrup_backend

def generate_sfs_block(bytecodes, stack_size,cname,blockId):

    instructions = []
    for b in bytecodes:
        op = b.getDisasm()

        if op.startswith("PUSH") and op.find("tag")==-1:
            op = op+" 0x"+b.getValue()

        elif op.startswith("PUSH"):
            op = "PUSHTAG"+" "+b.getValue()
            
        instructions.append(op)
        
    block_ins = list(filter(lambda x: x not in ["JUMP","JUMPI","JUMPDEST","tag","INVALID"], instructions))
    print(block_ins)

    block_data = {}
    block_data["instructions"] = block_ins
    block_data["input"] = stack_size


    #TODO: añadir nuevas instrucciones
    exit_code = rbr_isolate_block.evm2rbr_compiler(contract_name = cname, syrup = True, block = block_data, sto = True, block_id = blockId)
    #TODO llamar a optimización

    sfs_dict = get_sfs_dict()

    # In order to obtain the dict in the format for syrup, we have
    # to access the values of the values, as first key corresponds to the
    # contract and the second to current block.
    print(blockId)
    sfs_block = sfs_dict['syrup_contract']
    print(sfs_block)
    execute_syrup_backend(None, sfs_block, block_name=blockId)



def optimize_asm(file_name):
    asm = parse_asm(file_name)

    for c in asm.getContracts():
        contract_name = c.getContractName().split("/")[-1]
        for identifier in c.getDataIds():
            blocks = c.getRunCodeOf(identifier)
            for block in blocks:
                generate_sfs_block(block.getInstructions(),block.getSourceStack(),contract_name,block.getBlockId())

if __name__ == '__main__':
    file_name = "salida"
    optimize_asm(file_name)
