#!/usr/bin/python3

import sys

# altura : altura de la torre
# disp : piezas disponibles
# Colores: Azul = 0, Rojo = 1 , Verde = 2;

datos = input().split()
m = int(datos[0]) # número de juguetes
n = int(datos[1]) # número de niños
s = int(datos[2]) # satisfación mínima
datos = input().split() 
disp = []         # disponibilidad por juguete
for i in range(m):
    disp.append(int(datos[i]))
datos = input().split() 
jtipo = []         # tipo por juguete
for i in range(m):
    jtipo.append(int(datos[i]))
jsat=[]
for i in range(n):
    datos = input().split() 
    sat1 = []
    for j in range(m):
        sat1.append(int(datos[j]))
    jsat.append(sat1)

#print(m)
#print(n)
#print(s)
    
def asig (i,j):
    return "asig_"+str(i)+"_"+str(j)

def nsat (i,j):
    return "nsat_"+str(i)+"_"+str(j)

def ntipo (i,j):
    return "ntipo_"+str(i)+"_"+str(j)

def setlogic(l):
    return "(set-logic "+ l +")"

def intvar(v):
    return "(declare-fun "+v+" () Int)"

def bool2int(b):
    return "(ite "+b+" 1 0 )"

def addimplies(a1,a2):
    return "(=> "+a1+" "+a2+" )"
def addand(a1,a2):
    return "(and "+a1+" "+a2+" )"
def addor(a1,a2):
    return "(or "+a1+" "+a2+" )"
def addnot(a):
    return "(not "+a+" )"

def addexists(a):
    if len(a) == 0:
        return "false"
    elif len(a) == 1:
        return a[0]
    else :
        x = a.pop()
        return "(or " + x + " " + addexists(a) + " )" 

def addeq(a1,a2):
    return "(= "+a1+" "+a2+" )" 
def addle(a1,a2):
    return "(<= "+a1+" "+a2+" )" 
def addge(a1,a2):
    return "(>= "+a1+" "+a2+" )" 
def addlt(a1,a2):
    return "(< "+a1+" "+a2+" )"
def addgt(a1,a2):
    return "(> "+a1+" "+a2+" )" 

def addplus(a1,a2):
    return "(+ "+a1+" "+a2+" )"

def addassert(a):
    return "(assert "+a+" )"

def addassertsoft(a,w):
    return "(assert-soft "+a+" :weight "+ w + " )"

def addsum(a):
    if len(a) == 0:
        return "0"
    elif len(a) == 1:
        return a[0]
    else :
        x = a.pop()
        return "(+ " + x + " " + addsum(a) + " )" 

def checksat():
    print("(check-sat)")
def getobjectives():
    print("(get-objectives)")
def getmodel():
    print("(get-model)")
def getvalue(l):
    print("(get-value " + l + " )")

################################
# generamos un fichero smtlib2
################################

print("(set-option :produce-models true)")
print(setlogic("QF_LIA"))

#declaración de variables de la solución
for i in range(n):
        print(intvar(asig(i,0))) #juguete asignado 0
        print(intvar(asig(i,1))) #juguete asignado 1
        print(intvar(nsat(i,0))) #satisfacción juguete 0
        print(intvar(nsat(i,1))) #satisfacción juguete 1
        print(intvar(ntipo(i,0))) #satisfacción juguete 0
        print(intvar(ntipo(i,1))) #satisfacción juguete 1
# fin declaración

#constraint forall (i in 0..n-1, j in 0..1) (0 <= asig_i_j);
#constraint forall (i in 0..n-1) (asig_i_j <= m-1);
for i in range(n): 
    for j in range(2): 
        print(addassert(addle("0",asig(i,j))))
        print(addassert(addle(asig(i,j),str(m-1))))
#end constraint

#constraint forall (i in 0..n-1, j in 0..1, k in 0..m-1) (asig_i_j = k => nsat_i_j = jsat[i,k]);
for i in range(n):
    for j in range(2):
        for k in range(m):
            print(addassert(addimplies(addeq(asig(i,j),str(k)),addeq(nsat(i,j),str(jsat[i][k])))))
#end constraint

#constraint forall (i in 0..n-1, j in 0..1, k in 0..m-1) (asig_i_j = k => ntipo_i_j = jtipo[k]);
for i in range(n):
    for j in range(2):
        for k in range(m):
            print(addassert(addimplies(addeq(asig(i,j),str(k)),addeq(ntipo(i,j),str(jtipo[k])))))
#end constraint

#Asignación no supera disponibilidad
#constraint forall (i in 0..m-1) ( sum (j in 0..n-1, k in 0..1) ( bool2int(asig[j,k]=i) ) <= disp[i] );
for i in range(m):
    suma = []
    for j in range(n):
        for k in range(2):
            suma.append(bool2int(addeq(asig(j,k),str(i))))
    print(addassert(addle(addsum(suma),str(disp[i]))))
#fin constraint

#Todos mínima satisfacción
#constraint forall (i in 0..n-1) (sum (j in 0..1)(nsat[i,j]) >= s);
for i in range(n):
    suma = []
    for j in range(2):
        suma.append(nsat(i,j))
    print(addassert(addge(addsum(suma),str(s))))
#fin constraint

#No dos tipos iguales
#constraint forall (i in 0..n-1) ( ntipo_i_0 != ntipo_i_1 );
for i in range(n):
    print(addassert(addnot(addeq(ntipo(i,0),ntipo(i,1)))))
                        
#Evitar redundancia de soluciones
#constraint forall (i in 0..n-1) ( asig_i_0 > asig_i_1 ); Podria ser 'todos distintos si hay mas de dos' o con max repes
for i in range(n):
    print(addassert(addlt(asig(i,0),asig(i,1))))
    
#optimization constraints
for i in range(n):
    for j in range(m):
        print(addassertsoft(addeq(asig(i,0),str(j)),str(jsat[i][j])))  
    for j in range(m):
        print(addassertsoft(addeq(asig(i,1),str(j)),str(jsat[i][j])))  

checksat()
#getobjectives()

suma = []
for i in range(n):
    suma.append(nsat(i,0))
    suma.append(nsat(i,1))

getvalue("("+addsum(suma)+")")

#getmodel()
for i in range(n):
    for j in range(2):
        getvalue("("+asig(i,j)+")")
exit(0)
