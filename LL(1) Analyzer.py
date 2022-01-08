# -*- coding: utf-8 -*-
"""
Created on Jan 1 01:25:53 2022
@author: ASUS
注：本分析器接收的文法开始符号强制要求为S
"""

import tkinter
import tkinter.filedialog
import tkinter.ttk
    
class LL1:
    def __init__(self, Tset, NTset, S, Production, firstset, followset, Table,work_process):
        self.Tset = Tset
        self.NTset = NTset
        self.S = S
        self.Production = Production
        self.firstset = firstset
        self.followset = followset
        self.Table = Table
        self.work_process=work_process

    #消除形如S->S,或者无法到达终态的，或者无法被到达的状态的产生式
    def removeUselessAndHarmful(self):
        Tset = self.Tset
        NTset = self.NTset
        production=self.Production
        
        #消除形如S->S的产生式
        for item in production.keys():
            #print(len(production[item]))
            if len(production[item])==0:
                #raise RuntimeError('产生式集出错')
                tkinter.messagebox.showerror('错误','扫描到空的产生式，已经删除')
                self.work_process.append('扫描产生式时发现错误')
                production.pop(item)
                
            elif len(production[item])==1:#值列表长为1且键值对内容一致，删除
                if str(production[item])==str(item):
                    self.work_process.append('删除无用产生式'+str(production[item]))
                    production.pop(item)
                    
            else:#键值对长度大于等于2时，进行遍历操作查找
                tempList=[]
                for datum in production[item]:
                    
                    if datum==item:
                        tempList.append(datum)
                        
                production[item]=list(set(tempList) ^ set(production[item]))
                self.work_process.append('删除无用产生式'+str(tempList))
                
        #消除含不可到达的产生式
        leftNTList=[]
        rightNTList=[]
        for item in production.keys():
            leftNTList.append(item)
            if len(production[item])==1:
                #print(len(production[item][0]))
                if len(production[item][0])==1:
                    if production[item][0]>='A' and production[item][0]<='U':
                        rightNTList.append(production[item][0])#值为单独一个且为非终结符时，直接添加值非终结符右值列表中
                else:
                    for d in production[item][0]:
                        if d>='A' and d<='U':
                            rightNTList.append(d)#值为单独一个且为非终结符时，直接添加值非终结符右值列表中
                
            else:
                for datum in production[item]:#若产生式右边列表有多个元素
                    for d in datum:
                        if d>='A' and d<='U':
                            rightNTList.append(d)
        #print(leftNTList)
        #print(rightNTList)
        #temp=list(set(leftNTList).intersection(set(rightNTList)))
        
        for item in rightNTList:
            if item not in leftNTList:#不在左值列表中，代表该非终结符无法被抵达
                for key, value in production.items():
                    if value[0] == item:
                        item=key
                self.work_process.append('产生式{}不可达，已弹出'.format(production[item]))
                production.pop(item)#弹出该产生式
        #print(production.keys())
        #print(production.values())
        
        #重新扫描得出rightNTset
        leftNTList=[]
        rightNTList=[]
        for item in production.keys():
            leftNTList.append(item)
            if len(production[item])==1:
                if len(production[item][0])==1:
                    if production[item][0]>='A' and production[item][0]<='U':
                        rightNTList.append(production[item][0])#值为单独一个且为非终结符时，直接添加值非终结符右值列表中
                else:
                    for d in production[item][0]:
                        if d>='A' and d<='U':
                            rightNTList.append(d)
                
            else:
                for datum in production[item]:#若产生式右边列表有多个元素
                    for d in datum:
                        if d>='A' and d<='U':
                            rightNTList.append(d)
        
        NTset=list(set(leftNTList).union(set(rightNTList)))
        NTset=list(set(NTset))
        NTset.remove('S')
        NTset.append('S') #保证文法开始符在最后，便于消除左递归
        
        #重新赋值 相当于return 操作都在函数的副本中 最后赋回比较安全
        self.Tset = Tset
        self.NTset = NTset
        self.Production = production
        
        
    # 消除所有左递归
    def removeLeftRecursion(self):
        i = 1
        while i <= len(self.NTset):
            j = 1
            while j <= i-1:
                # set转换为list，才能进行下标取值操作
                Ai = self.NTset[i-1]  # Ai非终结符
                Aj = self.NTset[j-1]  # Aj非终结符

                rmList = [x for x in self.Production[Ai] if x.startswith(Aj)] #startswith检查字符串是否以选定子串开头
                if rmList:
                    addList = [y+x.replace(Aj, "", 1) if y != 'ε' else x.replace(Aj, "", 1)
                               for x in rmList for y in self.Production[Aj]]
                    # 不需替换则保留
                    self.Production[Ai] = list(
                        filter((lambda x: x not in rmList), self.Production[Ai]))
                    # 追加新替换式子
                    # append函数没有返回值，所以不能list().extend()，否则返回None
                    self.Production[Ai].extend(addList)
                work_process="去除间接左递归"+str(self.Production)
                self.work_process.append(work_process)#记录工作进程

                # 消除直接左递归
                LeftRecursionProduction = [
                    x for x in self.Production[Ai] if x.startswith(Ai)]    # 左递归的产生式

                notLeftRecursionProduction = [
                    x for x in self.Production[Ai] if not x.startswith(Ai)]  # 不是左递归的产生式
                if LeftRecursionProduction:     # 含有左递归的产生式
                    newNT = Ai+"'"              # 新终结符，如 A,A'
                    if newNT not in self.NTset:
                        self.NTset.append(newNT)
                    if notLeftRecursionProduction:
                        self.Production[Ai] = [
                            x+newNT for x in notLeftRecursionProduction]
                    else:
                        self.Production[Ai] = [newNT]
                    newList = [
                        x.replace(x[0], '', 1)+newNT for x in LeftRecursionProduction]
                    newList.append('ε')         # 追加空串
                    self.Production[newNT] = newList    # 加进产生式的字典中
                j = j+1

            i = i+1
        #特殊情况的判断，第一个非终结符对应的产生式本身是直接左递归，上面的两层循环判断了除第一个非终结符是直接左递归的情况
        LeftRecursionProduction = [
            x for x in self.Production[self.NTset[0]] if x.startswith(self.NTset[0])]
        notLeftRecursionProduction = [
            x for x in self.Production[self.NTset[0]] if not x.startswith(self.NTset[0])]
        if LeftRecursionProduction:
            newNT = 'S'+"'"
            if newNT not in self.NTset:         #新的终结符判断是否已经存在，不存在则插入
                self.NTset.append(newNT)
            if notLeftRecursionProduction:
                self.Production['S'] = [
                    x+newNT for x in notLeftRecursionProduction]
            else:
                self.Production['S'] = [newNT]
            newList = [x.replace(x[0], '', 1) +
                       newNT for x in LeftRecursionProduction]
            newList.append('ε')         # 追加空串
            self.Production[newNT] = newList    # 追加进产生式的字典中

        # 去除多余的生成式,使用dfs
        judge = dict.fromkeys(self.NTset, 0)# 非终结符做key,0做value
        stack = []
        stack.append(self.S)
        judge[self.S] = 1       # 标志为已访问
        while(len(stack) > 0 and (0 in judge.values())):
            top = stack.pop()
            rightPro = self.Production[top]  # 产生式右部
            for item in rightPro:
                i = 0
                while i < len(item):
                    ch = ""
                    if item[i] in self.NTset:
                        ch += item[i]
                        if i != len(item)-1:
                            if item[i+1] == "'":
                                ch += "'"
                        if judge[ch] == 0:
                            stack.append(ch)
                        judge[ch] = 1       # 标记为访问过的
                    i = i+1
        for key, values in judge.items():
            if values == 0:
                self.Production.pop(key)        # 去除产生式
                self.NTset.remove(key)          # 去除非终结符

    # 消除最左公因子
    def removeLeftCommonFactor(self):
        for item in self.NTset:                 # 遍历每个非终结符的产生式
            diff = {}                           # 将相同首字符的分为一类
            for i in self.Production[item]:     # 遍历该非终结符的每个产生式
                if i[0] not in diff.keys():
                    diff[i[0]] = [i]
                else:
                    diff[i[0]].append(i)
            oldList = []                        # 原来非终结符产生式的右部
            newNt = item                        # 新产生的非终结符
            for key, value in diff.items():
                newList = []                    # 新产生的非终结符产生式的右部
                if len(value) > 1:              # 可以提取公因子
                    newNt += "'"                # 新的终结符
                    oldList.append(key+newNt)
                    for v in value:
                        if len(v) == 1:         # 提取公因子后为ε
                            newList.append('ε')
                        else:
                            # 提取非公因子的部分,replace函数需要指定替换的次数
                            newList.append(v.replace(v[0], '', 1))
                    if len(newList) != 0:
                        self.Production[newNt] = newList            # 添加新的产生式右部
                        self.NTset.append(newNt)                    # 添加新的非终结符
                else:
                    #这里value为列表，所以value[0]才是所求的
                    oldList.append(value[0])

            self.Production[item] = oldList

    def createFirst(self):
        for nt in self.NTset:
            if nt not in self.firstset.keys():
                self.firstset[nt] = []
            for eachPro in self.Production[nt]:
                if eachPro[0] in self.Tset or eachPro[0] == 'ε':# A->a
                    self.firstset[nt].append(eachPro[0])
                    self.firstset[nt] = list(set(self.firstset[nt]))
                else:                                                # A->B...
                    if eachPro[0] in self.firstset.keys():
                        # 将Y1集除空串追加到X
                        R_addto_L = [
                            x for x in self.firstset[eachPro[0]] if x != 'ε']

                        self.firstset[nt].extend(R_addto_L)
                        self.firstset[nt] = list(
                            set(self.firstset[nt]))    # 去重

                        if 'ε' in self.Production[eachPro[0]]:  # 第一个Y1存在ε
                            after_Y1_str = eachPro[1:]
                            if not after_Y1_str:    # 为空，即是A->B 这种情况，且B含有空串，需要追加空串
                                self.firstset[nt].append('ε')
                                self.firstset[nt] = list(
                                    set(self.firstset[nt]))
                            else:
                                index = 0
                                for ch in after_Y1_str:
                                    if 'ε' in self.Production[ch]:
                                        index = index+1
                                    else:
                                        break
                                existNULL_Y = after_Y1_str[0:index]
                                if len(existNULL_Y) == len(after_Y1_str):       # Y1后面的Y都有空串，将空串加入first集
                                    self.firstset[nt].append('ε')
                                    self.firstset[nt] = list(
                                        set(self.firstset[nt]))
                                for each_Y in existNULL_Y:
                                    Y_addto_X = [
                                        x for x in self.firstset[each_Y] if x != 'ε']
                                    self.firstset[nt].extend(Y_addto_X)
                                    self.firstset[nt] = list(
                                        set(self.firstset[nt]))

    def createFirstSet(self):
        while True:
            size1 = 0
            for item in self.firstset.values():
                size1 += len(item)
            # print(size1)
            self.createFirst()
            size2 = 0
            for item in self.firstset.values():
                size2 += len(item)
            if size1 == size2:
                break
        

    def createFollow(self):
        for nt in self.NTset:
            for key, values in self.Production.items():
                for item in values:
                    index = item.find(nt)
                    flag = 1
                    newnt = nt+"'"
                    if newnt in item:
                        flag = 0

                    if flag and index >= 0:
                        newindex = index + len(nt)-1
                        if newindex == len(item)-1:  # 非终结符刚刚好在末尾,使用规则3
                            self.followset[nt].extend(self.followset[key])
                            self.followset[nt] = list(set(self.followset[nt]))

                        # 非终结符后面有字符,item[newindex+1]表示所求follow集的非终结符后面的第一个字符
                        else:
                            nextNT = item[newindex+1]  # 后面的符号

                            if nextNT in self.Tset:  # 终结符
                                self.followset[nt].append(nextNT)
                                self.followset[nt] = list(
                                    set(self.followset[nt]))
                            else:
                                i = newindex + 2
                                while i < len(item):
                                    if item[i] == "'":
                                        nextNT += "'"
                                    else:
                                        break
                                    i = i+1
                                # 后面是非终结符
                                # first集去除空串加到follow
                                add_list = [
                                    x for x in self.firstset[nextNT] if x != 'ε']
                                self.followset[nt].extend(add_list)
                                self.followset[nt] = list(
                                    set(self.followset[nt]))
                                if 'ε' in self.firstset[nextNT]:
                                    self.followset[nt].extend(
                                        self.followset[key])
                                    self.followset[nt] = list(
                                        set(self.followset[nt]))
                                    
    def createFollowSet(self):
        for nt in self.NTset:
            self.followset[nt] = []
        self.followset["S"].append('#')
        while True:
            size1 = 0
            for item in self.followset.values():
                size1 += len(item)
            # print(size1)
            self.createFollow()
            size2 = 0
            for item in self.followset.values():
                size2 += len(item)
            if size1 == size2:
                break

    def createTable(self):
        ckey = self.Tset
        ckey.append("#")

        value = list()
        for k in self.NTset:            # 初始化一个嵌套字典
            for ck in ckey:
                if k in self.Table:
                    self.Table[k].update({ck: value})
                else:
                    self.Table.update({k: {ck: value}})
        for key, values in self.firstset.items():
            for value in values:
                if value != "ε":
                    if len(self.Production[key]) == 1:           # 该非终结符只有一个产生式
                        str_pro = "{}->{}".format(key, self.Production[key][0])
                        if len(self.Table[key][value]) == 0:
                            self.Table[key][value] = [str_pro]
                        else:
                            self.Table[key][value].append(str_pro)
                    else:
                        for i in self.Production[key]:          # 看首字符
                            if value[0] == i[0]:                # 产生式首字符和first集的每个元素首字符
                                str_pro = "{}->{}".format(key, i)
                                if len(self.Table[key][value]) == 0:
                                    self.Table[key][value] = [str_pro]
                                else:
                                    self.Table[key][value].append(str_pro)
                                break
                # first集存在空串(产生式中有空串)
                else:
                    for k in self.followset[key]:
                        str_pro = "{}->{}".format(key, 'ε')
                        if len(self.Table[key][k]) == 0:
                            self.Table[key][k] = [str_pro]
                        else:
                            self.Table[key][k].append(str_pro)


def readFile(filename):
    Tset = set()                # 终结符集
    NTset = set()               # 非终结符集
    S = 'S'                     # 文法开始符
    Production = dict()         # 产生式
    
    with open(filename, encoding='utf-8', mode='r') as f:
        lines = [x.strip() for x in f.readlines() if not x.isspace()]#strip移除字符串头尾的空格
        for line in lines:
            line = line.split('->', 1)              # 分割
            line = [x.strip() for x in line]        # 去除中间的空白符
            line[1] = line[1].split('|')            # 分割右部或式
            line[1] = [x.strip() for x in line[1]]
            
            temp=[x for x in line[1] if len(x)==1 if x>='A' and x<='U' and x!=line[0]]#右部的字母非终结符添加至temp
            
            
            if line[0] not in Production.keys():    # 判断非终结符是否已经在产生式的键中
                addDict = {line[0]: line[1]}
                Production.update(addDict)
            else:
                Production[line[0]].extend(line[1])  # 存在的情况下，直接追加value
                
    NTset = list(set(Production.keys()))            # 字典的key作为非终结符
    NTset = list(set(NTset).union(set(temp)))
    NTset.remove('S')
    NTset.append('S')                               # 保证文法开始符在最后，便于消除左递归
    # 遍历values，对每个字符进行判断，如果不是非终结符，则为终结符,使用集合推导式生成终结符集
    Tset = list(set([c for item in Production.values()
                     for ch in item for c in ch if c not in NTset and c != 'ε' and c != "'"]))
    
    return Tset, NTset, S, Production

def NTset2Show_form(LB_txt1,x):#将处理后的文法表达式重新刷新显示在文法产生式的框内
    for item in x.Production.keys():
        string1=""
        if len(x.Production[item])==1:
            string1=x.Production[item][0]
        else:
            for datum in x.Production[item]:
                string1+=datum+' | '
            string1=string1[:-2]
        string=str(item)+' -> '+string1
        LB_txt1.insert(tkinter.END,string)
        
def show_info():
    tkinter.messagebox.showinfo('版权及作者信息', 'LL(1)分析器 V1.0.2\nSCNU18级计科 Oliver')
    
#消除无用规则并刷新文法产生式框
def btn0(LB_txt1,x):
    LB_txt1.delete(1, tkinter.END)# 清空列表框
    x.removeUselessAndHarmful()
    NTset2Show_form(LB_txt1,x)
    print(x.Tset)
    print(x.NTset)
    print(x.Production)
    
# “打开文件”按键函数
def btn1(LB_txt1, x):
    LB_txt1.delete(1, tkinter.END)# 清空列表框
    filename = tkinter.filedialog.askopenfilename()
    x.Tset, x.NTset, x.S, x.Production = readFile(filename)
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            LB_txt1.insert(tkinter.END, line)
    print(x.Tset)
    print(x.NTset)
    print(x.Production)
    
# “消除左递归”按键函数
def btn2(LB_txt2, x):
    LB_txt2.delete(1, tkinter.END)
    x.removeLeftRecursion()
    for key, value in x.Production.items():
        for v in value:
            str_pro = "{}->{}".format(key, v)
            LB_txt2.insert(tkinter.END, str_pro)

# "消除左公因子"按键函数
def btn3(LB_txt3, x):
    LB_txt3.delete(1, tkinter.END)
    x.removeLeftCommonFactor()
    for key, value in x.Production.items():
        for v in value:
            str_pro = "{}->{}".format(key, v)
            LB_txt3.insert(tkinter.END, str_pro)

# "生成first集"的按键函数
def btn4(LB_first,x):
    LB_first.delete(1,tkinter.END)
    x.createFirstSet()
    for key,values in x.firstset.items():
        if key in x.NTset:          # 防止没进行消除左递归操作就生成first集
            str_firstset_right = ""
            for v in values:
                str_firstset_right = str_firstset_right + v + ", "
            str_first = "first({}) : ( {} )".format(key,str_firstset_right)
            LB_first.insert(tkinter.END,str_first)

# "生成follow集"的按键函数
def btn5(LB_follow,x):
    LB_follow.delete(1,tkinter.END)
    x.createFollowSet()
    for key,values in x.followset.items():
        if key in x.NTset:          # 防止没进行消除左递归,消除左因子操作就生成follow集
            str_followset_right = ""
            for v in values:
                str_followset_right =  str_followset_right + v + ", "
            str_follow = "follow({}) : ( {} )".format(key,str_followset_right)
            LB_follow.insert(tkinter.END,str_follow)

# 给定输入串，输出该输入串的分析过程
def is_legal(input_text,x):
    input_str = input_text.get()
    table_root = tkinter.Tk()
    table_root.title("输入串的判断情况")
    table_root.geometry('1200x500')

    # 创建表格
    table_table = tkinter.ttk.Treeview(table_root,height=200)

    # 定义列
    table_table["columns"] = ["符号栈", "当前输入符号", "输入串","说明"]
    table_table.pack()
    table_table.column("#0",width=0,anchor='center')
    # 设置列宽度  
    table_table.column("符号栈", width=200,anchor='center')
    table_table.column("当前输入符号", width=200,anchor='center')
    table_table.column("输入串", width=200,anchor='center')
    table_table.column("说明", width=600,anchor='center')
    # 设置列名
    table_table.heading("符号栈",text="符号栈")
    table_table.heading("当前输入符号",text="当前输入符号")
    table_table.heading("输入串",text="输入串")
    table_table.heading("说明",text="说明")

    stack = []
    stack.append("#")
    stack.append("S")
    input_str += "#"
    i = 0
    colindex = 0   # 表格的行数
    a = input_str[i]        # 当前输入符号
    top = stack[len(stack)-1]
    while stack[len(stack)-1] != "#":
        top = stack[len(stack)-1]
        cur_stack_str = "".join(stack)
        stack.pop()     # 弹出栈顶
        a = input_str[i]
        if a not in x.NTset and a not in x.Tset:
            str1 = cur_stack_str
            str2 = a
            str3 = input_str[i+1:]
            str4 = "ERROR"
            insert_tablelist = [str1,str2,str3,str4]
            table_table.insert('',colindex,values=insert_tablelist)
            print("Error!!")
            return False
        if top in x.Tset:
            if top == a:
                if a != "#":
                    i = i+1
                    insert_tablelist = []
                    str1 = cur_stack_str
                    str2 = a
                    str3 = input_str[i:]
                    str4 = "匹配，弹出栈顶符号{}并读出输入串的下一个输入符号{}".format(top,input_str[i])
                    insert_tablelist = [str1,str2,str3,str4]
                    table_table.insert('',colindex,values=insert_tablelist)
                    colindex = colindex+1
                    continue
            table_item = x.Table[top][a]
            if table_item:              # []或者['A->i']
                table_item = x.Table[top][a][0]
                table_item = table_item.split('->')[1]
                if table_item != 'ε':       # T'S 分离成 T' S
                    j = 0
                    table_item += '#'
                    insert_stack = []
                    while j < len(table_item)-1:
                        ch = table_item[j]             # 表示单个字符
                        if ch in x.Tset:
                            insert_stack.append(ch)
                            j = j+1
                        else:
                            while table_item[j+1] == "'" and j < len(table_item):
                                ch += "'"
                                j = j+1
                            j = j+1
                            insert_stack.append(ch)
                    insert_stack.reverse()          # 翻转，逆序入栈
                    stack.extend(insert_stack)
                    # gui 打印
                    str1 = cur_stack_str
                    str2 = a
                    str3 = input_str[i+1:]
                    str4 = "弹出栈顶符号{}，将M[{},{}]中{}的{}压入栈中".format(top,top,a,x.Table[top][a][0],"".join(insert_stack))
                    insert_tablelist = [str1,str2,str3,str4]
                    table_table.insert('',colindex,values=insert_tablelist)
                    # ######
                else:       # 空串不压栈
                    str1 = cur_stack_str
                    str2 = a
                    str3 = input_str[i+1:]
                    str4 = "弹出栈顶符号{}，因为M[{},{}]中为{}->'ε'，故不压入栈中".format(top,top,a,top)
                    insert_tablelist = [str1,str2,str3,str4]
                    table_table.insert('',colindex,values=insert_tablelist)

            else:   # 表中无此项
                return False
        colindex = colindex+1
    str1 = cur_stack_str
    str2 = a
    str3 = input_str[i+1:]
    str4 = "匹配成功"
    insert_tablelist = [str1,str2,str3,str4]
    table_table.insert('',colindex,values=insert_tablelist)

# "生成table表"的按键函数
def btn6(x):
    x.createTable()
    table_root = tkinter.Tk()
    table_root.title("table表")
    table_root.geometry('710x170')

    # 创建表格
    table_table = tkinter.ttk.Treeview(table_root)

    # 定义列
    column_list = x.Tset
    # print("非终结符：",column_list)
    table_table["columns"] = column_list
    table_table.pack()
    table_table.column("#0",width=100,anchor='center')
    # 设置列宽度，列名
    for i in column_list:
        table_table.column(i, width=100,anchor='center')
        table_table.heading(i, text=i)
    
    # 给表格添加数据
    i = 0
    for key,values in x.Table.items():
        column_tup = list()
        for v in values.values():
            if v:
                column_tup.append(v)
            else:
                column_tup.append("")
        table_table.insert('',i,text=key,values=column_tup)
        i = i+1
           
def show_work(x):
    string=""
    for item in x.work_process:
        string+=item+'\n'
    tkinter.messagebox.showinfo('工作过程',string)
    
# gui界面
def GUI():
    Tset = []
    NTset = []
    S = "S"
    Production = dict()
    firstset = {}
    followset = {}
    Table = {}
    work_process=[]
    x = LL1(Tset, NTset, S, Production, firstset,followset, Table, work_process)   #建立一个LL1实例

    root = tkinter.Tk()
    root.title("LL(1)分析器")
    root.geometry('600x530')
    root.resizable(0, 0)  # 禁止调整窗口尺寸
    
    #菜单栏及菜单    
    menubar = tkinter.Menu(root)
    advancedMenu = tkinter.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='高级', menu=advancedMenu)
    advancedMenu.add_command(label='关于', command=show_info)
    advancedMenu.add_command(label='退出', command=root.quit)
    advancedMenu.add_command(label='查看工作过程', command=lambda:show_work(x))
    
    # 词法文件框
    LB_txt1 = tkinter.Listbox(root, height=18, width=23, bd=3)
    LB_txt1.insert(0, "文法产生式:")
    
    # 消除左递归框
    LB_txt2 = tkinter.Listbox(root, bd=2.5, height=12, width=28)
    LB_txt2.insert(0, "无左递归的文法产生式：")

    # 消除左因子框
    LB_txt3 = tkinter.Listbox(root, bd=2.5, height=12, width=26)
    LB_txt3.insert(0, "无左因子的文法产生式：")

    # first集合框
    LB_first = tkinter.Listbox(root, bd=2.5, height=12, width=28)
    LB_first.insert(0, "FIRST集:")

    # follow集合框
    LB_follow = tkinter.Listbox(root, bd=2.5, height=12, width=26)
    LB_follow.insert(0, "FOLLOW集:")
    
    # 输入框
    input_text = tkinter.Entry(root, bd=3, width=54)
    
    # btn width 85, height 35
    Btn_0 = tkinter.Button(root, command=lambda: btn0(LB_txt1, x), text="消除无用及\n有害规则", activebackground="blue", activeforeground="white", bd=4, width=10,height=2)
    Btn_1 = tkinter.Button(root, command=lambda: btn1(LB_txt1, x), text="打开文件", activebackground="blue", activeforeground="white", bd=4, width=10,height=2)
    Btn_2 = tkinter.Button(root, command=lambda: btn2(LB_txt2, x), text="消除左递归", activebackground="blue", activeforeground="white", bd=4, width=10,height=2)
    Btn_3 = tkinter.Button(root, command=lambda: btn3(LB_txt3, x), text="消除左公因子", activebackground="blue",activeforeground="white", bd=4, width=10,height=2)
    Btn_4 = tkinter.Button(root, command=lambda: btn4(LB_first,x),text="生成first集", activebackground="blue", activeforeground="white", bd=4, width=10, height=2)
    Btn_5 = tkinter.Button(root, command=lambda: btn5(LB_follow,x),text="生成follow集", activebackground="blue",activeforeground="white", bd=4, width=10,height=2)
    Btn_6 = tkinter.Button(root, command=lambda: btn6(x), text="生成LL(1)\n分析表", activebackground="blue",activeforeground="white", bd=4, width=10,height=2)
    Btn_7 = tkinter.Button(root, command=lambda: is_legal(input_text,x),text="生成最左推导\n判断栈", activebackground="blue",activeforeground="white", bd=4, width=10,height=2)
    
    # 绝对布局
    input_text.place(x=190, y=480,height=30)
    LB_txt1.place(x=10, y=0)
    LB_txt2.place(x=190, y=0)
    LB_txt3.place(x=387, y=0)
    LB_first.place(x=190, y=230)
    LB_follow.place(x=387, y=230)
    Btn_0.place(x=90,y=330)
    Btn_1.place(x=5, y=330)
    Btn_2.place(x=5, y=380)
    Btn_3.place(x=90, y=380)
    Btn_4.place(x=5, y=430)
    Btn_5.place(x=90, y=430)
    Btn_6.place(x=5, y=480)
    Btn_7.place(x=90, y=480)
    root.config(menu=menubar)
    root.mainloop()
    
if __name__ == "__main__":
    GUI()

