import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/../ethir")

import opcodes

def count_constant_expressions(content):
    l = filter(lambda x: x.find("Evaluate expression")!=-1,content)
    return len(l)

def count_rules_type1(content):
    l = filter(lambda x: x.find("Simplification rule type 1")!=-1,content)
    return len(l)

def count_rules_type2(content):
    l = filter(lambda x: x.find("Simplification rule type 2")!=-1,content)
    return len(l)

def count_op_len_and_gas(content):
    l = filter(lambda x: x.find("OPT INFO")!=-1,content)
    vals = map(lambda x: x.split(":")[-1].strip(),l)
    lengths = map(lambda x: int(x.split(",")[0]),vals)
    gas = map(lambda x: int(x.split(",")[1]),vals)

    return sum(lengths),sum(gas)

def get_sol_name(filename):
    fl = filename.strip(".sol.log")
    return fl


def compute_info_normal(filename):
    csv_path = "../../most-called-per-contract/yul_normal/oms_10s/"

    # csv_path = "../../results-3105-per-contract/contracts45-normal/oms_10s/"
    # csv_path = "../../results-3105-per-contract/contracts678-normal/oms_10s/"
    
    f = open(csv_path+filename+"_results_oms.csv","r")

    lines = f.readlines()[1::]
    return compute_file(lines)
    
def compute_info_opt(filename):
    csv_path = "../../most-called-per-contract/yul_opt/oms_10s/"

    # csv_path = "../../results-3105-per-contract/contracts45-opt/oms_10s/"
    # csv_path = "../../results-3105-per-contract/contracts678-opt/oms_10s/"

    
    f = open(csv_path+filename+"_results_oms.csv","r")

    lines = f.readlines()[1::]
    return compute_file(lines)


def compute_info_noyul(filename):
    csv_path = "../../results-3105-per-contract/contracts678-noyul/oms_10s/"

    f = open(csv_path+filename+"_results_oms.csv","r")

    lines = f.readlines()[1::]
    return compute_file(lines)


def compute_file(lines):
    nl = 0
    g = 0
    for l in lines:
        elems = l.split(",")
        list_op = elems[9]

        op = list_op.split()

        i = 0
        while (i<len(op)):
            nl+=1
            g+= opcodes.get_syrup_cost(op[i].strip())
            
            if op[i].startswith("PUSH"):
                i+=1

            i+=1
            
    return (nl,g)


def main():

    normal_dir = "../../logs/"
    opt_dir = "../../logs-optimize/"
    #no_yul_dir = "../logs-noyul"


    files = os.listdir(normal_dir)

    content = ["Contract,normal-constant,normal-r1,normal-r2,opt-constant,opt-r1,opt-r2,lines-normal,lines-opt,gas-normal,gas-opt,higher-constant,higher-r1,higher-r2,higher,max-lines,max-gas"]#nooyul-constant,noyul-r1,noyul-r2


    content_gas = ["Contract,normal-lines,opt-lines,normal-syrup-lines,opt-syrup-lines,normal-gas,opt-gas,normal-syrup-gas,opt-syrup-gas"]

    for f in files:

        if f not in os.listdir(opt_dir):
            continue

        sname = get_sol_name(f)
        ls_normal,gs_normal = compute_info_normal(sname)
        ls_opt, gs_opt = compute_info_opt(sname)
        
        f1 = open(normal_dir+"/"+f,"r")
        f2 = open(opt_dir+"/"+f,"r")
        #f3 = open(no_yul_dir+"/"+f,"r")

        lines_normal = f1.readlines()
        lines_opt = f2.readlines()
        # lines_noyul = f3.readlines()

        n1 = count_constant_expressions(lines_normal)
        n2 = count_rules_type1(lines_normal)
        n3 = count_rules_type2(lines_normal)
        l1,g1 = count_op_len_and_gas(lines_normal)
        
        o1 = count_constant_expressions(lines_opt)
        o2 = count_rules_type1(lines_opt)
        o3 = count_rules_type2(lines_opt)
        l2,g2 = count_op_len_and_gas(lines_opt)
        
        # y1 = count_contant_expressions(lines_noyul)
        # y2 = count_rules_type1(lines_noyul)
        # y3 = count_rules_type2(lines_noyul)
        # l3,g3 = count_op_len_and_gas(lines_noyul)



        
        m1 = max(n1,o1)#y1

        if m1 == n1:
            m1 = "NORMAL"
        #elif m1 == y1:
        #   m1 = "NOYUL"
        else:
            m1 = "OPT"
        
        m2 = max(n2,o2)

        if m2 == n2:
            m2 = "NORMAL"
        #elif m2 == y2:
        #   m2 = "NOYUL"
        else:
            m2 = "OPT"

        m3 = max(n3,o3)
            
        if m3 == n3:
            m3 = "NORMAL"
        #elif m3 == y3:
        #   m3 = "NOYUL"
        else:
            m3 = "OPT"

        mt = max (n1+n2+n3,o1+o2+o3) #y1+y2+y3
        if mt == n1+n2+n3:
            mt = "NORMAL"

        # elif mt == y1+y2+y3:
        #     mt = "NOYUL"

        else:
            mt = "OPT"


        max_l = max(l1,l2)#l3

        if max_l == l1:
            max_l = "NORMAL"
        # elif max_l == l3:
        #     max_l = "NOYUL"
        else:
            max_l = "OPT"

        max_g = max(g1,g2)#l3

        if max_g == g1:
            max_g = "NORMAL"
        # elif max_g == g3:
        #     max_g = "NOYUL"
        else:
            max_g = "OPT"

            
        new_line = ",".join([f,str(n1),str(n2),str(n3),str(o1),str(o2),str(o3),str(l1),str(l2),str(g1),str(g2),m1,m2,m3,mt,max_l,max_g])#y1,y2,y3

        content.append(new_line)


        new_line2 = ",".join([f,str(l1),str(l2),str(ls_normal),str(ls_opt),str(g1),str(g2),str(gs_normal),str(gs_opt)])
        content_gas.append(new_line2)
        
    end_f = open("result_rules.csv","w")

    end_f.write("\n".join(content))
    end_f.close()

    end_f1 = open("results_len_and_gas.csv","w")
    end_f1.write("\n".join(content_gas))
    end_f1.close()
    
if __name__ == '__main__':
    main()
