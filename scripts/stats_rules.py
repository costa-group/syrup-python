import os


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

def main():

    normal_dir = "../../logs/"
    opt_dir = "../../logs-optimize/"
    #no_yul_dir = "../logs-noyul"


    files = os.listdir(normal_dir)

    content = ["Contract,normal-constant,normal-r1,normal-r2,opt-constant,opt-r1,opt-r2,lines-normal,lines-opt,gas-normal,gas-opt,higher-constant,higher-r1,higher-r2,higher,max-lines,max-gas"]#nooyul-constant,noyul-r1,noyul-r2
    for f in files:

        if f not in os.listdir(opt_dir):
            continue
        
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
        elif max_l == l3:
            max_l = "NOYUL"
        else:
            max_l = "OPT"

        max_g = max(g1,g2)#l3

        if max_g == g1:
            max_g = "NORMAL"
        elif max_g == g3:
            max_g = "NOYUL"
        else:
            max_g = "OPT"

            
        new_line = ",".join([f,str(n1),str(n2),str(n3),str(o1),str(o2),str(o3),str(l1),str(l2),str(g1),str(g2),m1,m2,m3,mt,max_l,max_g])#y1,y2,y3

        content.append(new_line)

    end_f = open("result_rules.csv","w")

    end_f.write("\n".join(content))
    end_f.close()

if __name__ == '__main__':
    main()
