
import pandas as pd
from math import log2
import copy as cp
import sys


L = int(sys.argv[1])
K = int(sys.argv[2])
train_file_path=str(sys.argv[3])
validation_file_path=str(sys.argv[4])
test_file_path=str(sys.argv[5])
print_yesorno=str(sys.argv[6])
    
#---------------Fetching the Data---------------------------------------------------------

train_file=pd.read_csv(train_file_path)
validation_file=pd.read_csv(validation_file_path)
test_file=pd.read_csv(test_file_path)
train_cols=train_file.columns

class TreeNode:#---Class to create tree nodes

    def __init__(self, name="Result", b0=None, b1=None,result=None):
        self.name = name
        self.b0 = b0
        self.b1 = b1
        self.result=result

#---------------Calculating entropy-------------------------------
        
def entropy(pos,neg):
    if pos==0 or neg==0: return 0
    p=pos/(pos+neg)
    ent=-p*log2(p)-(1-p)*log2(1-p)
    return ent

#---------------Calculating Varience Inpurity-------------------
    
def VI(k1,k0):
    if k1==0 or k0==0: return 0

    vi=float((k0*k1))/float(((k0+k1)**2))
    return vi
    
    
#--------------Counting the number of 0's and 1's---------------
    
def count(data_set):
    pos=0 
    neg=0
    
    if data_set.empty == False:
        
        for i in data_set:
            if i == 1:
                pos=pos+1
            else: 
                neg=neg+1

    return pos,neg

#--------------Counting the number of 0's and 1's with respect to the 'Class'---
    
def count2(data1,Class):
    pos0=neg0=pos1=neg1=0
    
    for i,j in zip(data1,Class):
        if i==0 and j==0:
            neg0=neg0+1
        elif i==0 and j==1:
            pos0=pos0+1
        elif i==1 and j==1:
            pos1=pos1+1
        elif i==1 and j==0:
            neg1=neg1+1
        
    return pos0,neg0,pos1,neg1

#---------------Calculating Information Gain---------------------
    
def info_gain(Class,child,parameter):
    pos,neg=count(Class)
    pos0,neg0,pos1,neg1=count2(child,Class)
    if pos0==neg0==pos1==neg1==0: return 0
    p=(pos0+neg0)/(pos0+neg0+pos1+neg1)
    if parameter=="ent":
        gain=entropy(pos,neg)-p*entropy(pos0,neg0)-(1-p)*entropy(pos1,neg1)
        
    if parameter=="vi":
        gain=VI(pos,neg)-p*VI(pos0,neg0)-(1-p)*VI(pos1,neg1)
        
    return gain

#---------------For Finding and returning best attribute-----------
    
def best_attribute(data_set,parameter):
    best_gain=-10.0
    copy=data_set.copy(deep=True)
    Class=copy.pop('Class')
    name=''
    
    for i in copy.columns:
        gain=info_gain(Class,copy.loc[:,i],parameter)
        if gain>best_gain:
            best_gain=gain
            name=i
    copy['Class']=Class
    return name,best_gain

#------------Dividing data set based on best attribute------------
    
def divide(data_set,best_attr):
    if best_attr:
        copy=data_set.copy(deep=True)
        
        set0=pd.DataFrame(columns=copy.columns)
        set1=pd.DataFrame(columns=copy.columns)

        for index, row in copy.iterrows():
            if row[best_attr]==0:
                set0 = set0.append(row)
            elif row[best_attr]==1:
                set1 = set1.append(row)
            
        if best_attr:
            if set0.empty==False:
                set0.pop(best_attr)
            if set1.empty==False:
                set1.pop(best_attr)
    
        return set0,set1
            

def calc(data_set):
    ones,zeros=count(data_set.pop('Class'))
    if ones>=zeros:
        return 1
    else: 
        return 0

#----------------Recursive building of the tree---------
        
def build_tree(data_set,parameter):
    if data_set.empty==False:
        copy=data_set.copy(deep=True)
        best_attr,best_gain=best_attribute(copy,parameter)
        set0,set1=divide(copy,best_attr)
                
        
        if best_gain>0:
            br0=build_tree(set0,parameter)
            br1=build_tree(set1,parameter)
            node=TreeNode(name=best_attr, b0=br0, b1=br1)
            return node
        else:
            copy1=data_set.copy(deep=True)
            return TreeNode(result=calc(copy1))
    return None


#--------------To display a tree-----------------------
    
def display_tree(node,indent):
    if node.b0!=None: 
        print(indent+node.name+" = "+"0 :",end="")
        display_tree(node.b0,indent+' |')
    if node.b1!=None:
        print(indent+node.name+" = "+"1 :",end="")
        display_tree(node.b1,indent+' |')
    
#---------Calculating tree accuracy---------------------
        
def tree_accuracy(root,data_set):
    count=0
    
    for index, row in data_set.iterrows():
        classified_value = classify(root, row)
        if row['Class'] == classified_value:
            count += 1
    accuracy = 100 * count / len(data_set.iloc[:,0])

    return accuracy
        
#---------Returns the end result of a tree branch---------------------
    
def classify(node, row):
    if node.name!="Result":
        if row[node.name]==1:
            value=classify(node.b1,row)
    
        if row[node.name]==0:
            value=classify(node.b0,row)
            
    if node.name=="Result":
        return node.result
        
    return value

#-------------Basic Pruning--------------------------------------------------
    
def prune(root,l,k,data_set,printyn):
    root_copy=cp.deepcopy(root)
    
    c=data_set.copy(deep=True)
    
    acc=tree_accuracy(root_copy,c)
    print("\nAccuracy Before Pruning",acc)
    root_copy.b0.b0.b0=root_copy.b0.b0.b0.b0
    acc=tree_accuracy(root_copy,c)
    print("\nAccuracy After Pruning",acc)
    
    if printyn=="yes":
        print("\nPruned Tree\n")
        display_tree(root_copy,"\n")

    root_copy=cp.deepcopy(root)
    print("\nAccuracy Before Pruning",tree_accuracy(root_copy,c))
    root_copy.b1.b0.b0=root_copy.b0.b0.b0.b0
    print("\nAccuracy After Pruning",tree_accuracy(root_copy,c))
    if printyn=="yes":
        print("\nPruned Tree\n")
        display_tree(root_copy,"\n")
    
    root_copy=cp.deepcopy(root)
    print("\nAccuracy Before Pruning",tree_accuracy(root_copy,c))
    root_copy.b1.b0.b0.b0=root_copy.b0.b0.b0.b0.b0
    print("\nAccuracy After Pruning",tree_accuracy(root_copy,c))
    if printyn=="yes":
        print("\nPruned Tree\n")
        display_tree(root_copy,"\n")
    
    
        
#----------------Main Function-------------------------------------
if __name__ == '__main__':
    
    copy_ent=train_file.copy(deep=True)
    copy_vi=train_file.copy(deep=True)

#---------------Entropy Based Tree-------------------------------
    
    
    root_ent=build_tree(copy_ent,"ent")

    print("\nTree based on entropy")
    display_tree(root_ent,"\n")
    
    copy_ent=train_file.copy(deep=True)
    print("\n\n Accuracy for Training data (Entropy based Tree): ", tree_accuracy(root_ent,copy_ent))
    
    copy_ent=validation_file.copy(deep=True)
    print("\n\n Accuracy for Validation data (Entropy based Tree): ", tree_accuracy(root_ent,copy_ent))

    copy_ent=test_file.copy(deep=True)
    print("\n\n Accuracy for Test data (Entropy based Tree): ", tree_accuracy(root_ent,copy_ent))
    
    print("\nPruning based on Testing data")
    prune(root_ent,L,K,copy_ent,print_yesorno)
    
    copy_ent=validation_file.copy(deep=True)
    print("\nPruning based on Validation data")
    prune(root_ent,L,K,copy_ent,print_yesorno)
    


#---------------Varience Impurity Based Tree-------------------------------
    
    root_vi=build_tree(copy_vi,"vi")
   
    print("\nTree based on varience inpurity")
    display_tree(root_vi,"\n")
    
    copy_vi=train_file.copy(deep=True)
    print("\n\nTree Accuracy: ", tree_accuracy(root_vi,copy_vi))

    copy_vi=validation_file.copy(deep=True)
    print("\n\n Accuracy for Validation data (varience inpurity based Tree): ", tree_accuracy(root_vi,copy_vi))

    copy_vi=test_file.copy(deep=True)
    print("\n\n Accuracy for Test data (varience inpurity based Tree): ", tree_accuracy(root_vi,copy_vi))
    
    print("\nPruning based on Testing data")
    prune(root_vi,L,K,copy_ent,print_yesorno)
    
    copy_ent=validation_file.copy(deep=True)
    print("\nPruning based on Validation data")
    prune(root_vi,L,K,copy_ent,print_yesorno)
    
    
#-----------------------------------------------------------------------------
    


