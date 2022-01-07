# -*- coding: utf-8 -*-
"""
Created on Jan 1 01:25:53 2022
@author: ASUS
"""

"""

    Production产生式存放：
        A->a | b
        {A:['a','b']}
    
    firstset集存在,follow集同理
    first(A) = (a,b),则{'A':[a,b]}
    
    table表（M表）例如：M[A,(] = "A->(abc"
    {'A':{'(':["A->(abc"]}}
  
    测试样例
    S->Qc|c
    Q->Rb|b
    R->Sa|a

    S->S+S|S-S|S*S|S/S| (S) | I

    S->TS'
    S'->+TS'|ε
    T->FT'
    T'->*FT'|ε
    F->(S)|i

    A->ab1 | ab2 | Dc | Ac |Acc  ==>消除左递归新生成的生成式，还有可能存在最左公因子
    D->ad                             #消除所以消除左递归新的终结符为A',最左公因子用A''
    

    A->aB|abD|abDE ==》这种情况公因子怎么提取。。

    S->ac|abd|cc|cce

    S->LA
    L->i:|ε
    A->i=e
    
    注：本分析器接收的文法开始符强制要求为S

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
        
        '''
        终结符（Tset），非终结符（NTset），文法开始符（S）(需要注意的是，本次实验必须要求文法开始符是字符S), 
        产生式（Production）, FIRST集（firstset），FOLLOW集（followset）, LL(1)分析表（Table）
        各个参数的数据存放形式：
        Tset：[]列表
        NTset:[]列表
        S: 'S' 字符串
        Production:{},例如：A->aA|b, 就是表示为{'A': ["aA","b"]}
        firstset: {}, 例如：fisrt(A):(a,b),就是表示为{‘A’:["a","b"]}
        followset:{},同firstset一样
        Table:{}嵌套字典，例如：M[A,a] = (A->a)，那么就是表示为{'A':{'a':['A->a']}}
        '''
    
    #消除形如S->S,或者无法到达终态的，或者无法被到达的状态的产生式
    def removeUselessAndHarmful(self):
        pass
    
    # 消除一切左递归
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
                    # 本来不需要替换的，保留
                    self.Production[Ai] = list(
                        filter((lambda x: x not in rmList), self.Production[Ai]))
                    # 追加新替换的式子进来
                    # extend,append函数没有返回值的，所以不能list().extend()，否则返回None
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
                    newList.append('ε')         # 追加空字，哑f西no
                    self.Production[newNT] = newList    # 加进产生式的字典中
                j = j+1

            i = i+1
        """
        特殊判断，第一个非终结符对应的产生式本身是直接左递归，
        注意是第一个非终结符，因为上面的两层循环判断了除第一个非终结符的情况了
        """
        LeftRecursionProduction = [
            x for x in self.Production[self.NTset[0]] if x.startswith(self.NTset[0])]
        notLeftRecursionProduction = [
            x for x in self.Production[self.NTset[0]] if not x.startswith(self.NTset[0])]
        if LeftRecursionProduction:
            newNT = 'S'+"'"
            if newNT not in self.NTset:         # 新的终结符判断是否存在，不存在插入
                self.NTset.append(newNT)
            if notLeftRecursionProduction:
                self.Production['S'] = [
                    x+newNT for x in notLeftRecursionProduction]
            else:
                self.Production['S'] = [newNT]
            newList = [x.replace(x[0], '', 1) +
                       newNT for x in LeftRecursionProduction]
            newList.append('ε')         # 追加空字，哑f西no
            self.Production[newNT] = newList    # 加进产生式的字典中

        # 去除多余的生成式,dfs
        """
        fromkeys方法注意：
        如果每个key的value都为同一个对象，
        则操作该key的value时，所有的key的value都会改变
        """
        judge = dict.fromkeys(self.NTset, 0)        # 字典，非终结符做key,0做valu
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
                        judge[ch] = 1       # 标志为访问过
                    i = i+1
        for key, values in judge.items():
            if values == 0:
                self.Production.pop(key)        # 去除产生式
                self.NTset.remove(key)          # 去除非终结符

    # 消除最左公因子
    """
    算法思想：将每个非终结符的产生式右部，也就是多个字符串，按照首个字符分类，
    然后进行转换，新转换生成的新非终结符的产生式更新到self实例中，进行转换。
    """

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
                            # 提取非公因子的部分,replace函数需要指定替换的次数，bug error
                            newList.append(v.replace(v[0], '', 1))
                    if len(newList) != 0:
                        self.Production[newNt] = newList            # 添加新的产生式右部
                        self.NTset.append(newNt)                    # 添加新的非终结符
                else:
                    # 注意这里value为列表，所以value[0]为所求
                    oldList.append(value[0])

            self.Production[item] = oldList

    def createFirst(self):
        for nt in self.NTset:
            if nt not in self.firstset.keys():
                self.firstset[nt] = []
            for eachPro in self.Production[nt]:
                if eachPro[0] in self.Tset or eachPro[0] == 'ε':                          # A->a
                    self.firstset[nt].append(eachPro[0])
                    self.firstset[nt] = list(set(self.firstset[nt]))
                else:                                                # A->B...
                    if eachPro[0] in self.firstset.keys():
                        # 将Y1集除空字追加到X
                        R_addto_L = [
                            x for x in self.firstset[eachPro[0]] if x != 'ε']

                        self.firstset[nt].extend(R_addto_L)
                        self.firstset[nt] = list(
                            set(self.firstset[nt]))    # 去重

                        if 'ε' in self.Production[eachPro[0]]:  # 第一个Y1存在ε
                            after_Y1_str = eachPro[1:]
                            if not after_Y1_str:    # 为空，即是A->B 这种情况，且B含有空字，需要追加空字
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
                                if len(existNULL_Y) == len(after_Y1_str):       # Y1后面的Y都有空字，加
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
                        if newindex == len(item)-1:  # 非终结符刚刚好在末尾,规则3
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
                                # first集去除空字加到follow

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
                    # print("{}->{},非终结符为：{}".format(key,item,nt))
                    # print("规则为：",self.followset)
        # print("==========", self.followset['S'])

    def createFollowSet(self):
        for nt in self.NTset:
            self.followset[nt] = []
        self.followset["S"].append('#')
        while True:
            """            
            # 判断坑了我5小时。。。
            # 不能f1 = self.followset 执行函数  f2 = self.followset，
            # 然后判断f1 == f2？
            # f1随着self.followset变化而变化？？未解决！
            """
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

        """
        ERROR fromkeys少用！！
        # cdict = dict.fromkeys(ckey, [])             # 初始化子字典 一维
        # self.Table = dict.fromkeys(self.NTset, cdict)    # Table表     二维
        """
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
                # first集存在空字(产生式中有空字)
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
        lines = [x.strip() for x in f.readlines() if not x.isspace()]
        for line in lines:
            line = line.split('->', 1)              # 分割
            line = [x.strip() for x in line]        # 去除空白符
            line[1] = line[1].split('|')            # 分割
            line[1] = [x.strip() for x in line[1]]
            if line[0] not in Production.keys():    # 判断非终结符是否存在
                addDict = {line[0]: line[1]}
                Production.update(addDict)
            else:
                Production[line[0]].extend(line[1])  # 存在，追加
            # 11 -> 11|221 产生式
            # {'11': ['11', '221']}
    NTset = list(set(Production.keys()))            # 字典的key作为非终结符
    NTset.remove('S')
    NTset.append('S')                               # 保证文法开始符在最后，消除左递归方便点
    # 遍历字典的values，判断每个字符如果不是非终结符，那么就是终结符,使用集合推导式，
    Tset = list(set([c for item in Production.values()
                     for ch in item for c in ch if c not in NTset and c != 'ε' and c != "'"]))
    return Tset, NTset, S, Production

def show_info():
    tkinter.messagebox.showinfo('版权及作者信息', 'LL(1)分析器 V1.0.2\nSCNU18级计科 Oliver')
    
#消除无用规则
def btn0(LB_txt1,x):
    LB_txt1.delete(1, tkinter.END)# 清空列表框
    x.removeUselessAndHarmful()
    

# “打开文件”按键函数
def btn1(LB_txt1, x):
    LB_txt1.delete(1, tkinter.END)# 清空列表框
    filename = tkinter.filedialog.askopenfilename()
    x.Tset, x.NTset, x.S, x.Production = readFile(filename)
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            LB_txt1.insert(tkinter.END, line)

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
        if key in x.NTset:          # 防止用户没进行消除左递归操作就生成first集
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
        if key in x.NTset:          # 防止用户没进行消除左递归,消除左因子操作就生成follow集
            str_followset_right = ""
            for v in values:
                str_followset_right =  str_followset_right + v + ", "
            str_follow = "follow({}) : ( {} )".format(key,str_followset_right)
            LB_follow.insert(tkinter.END,str_follow)

# 给定输入串，输出该输入串的分析过程
def is_legal(input_text,x):
    input_str = input_text.get()  # input_text为输入框对象
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
    colindex = 0   # gui 表格的行数
    a = input_str[i]        # 当前输入符号
    top = stack[len(stack)-1]
    """
    str1,str2都是相同的，但是懒得改了...
    """
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
                    str3 = input_str[i:]    # 注意这里是i，不是i+1
                    str4 = "匹配，弹出栈顶符号{}并读出输入串的下一个输入符号{}".format(top,input_str[i])
                    insert_tablelist = [str1,str2,str3,str4]
                    table_table.insert('',colindex,values=insert_tablelist)
                    colindex = colindex+1
                    continue
                # else:
                #     print("succeed")
                #     return True
        else:
            table_item = x.Table[top][a]
            # print("查表为",table_item)
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
                else:       # 空字不压入
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
    str4 = "匹配，分析成功！"
    insert_tablelist = [str1,str2,str3,str4]
    table_table.insert('',colindex,values=insert_tablelist)
    print("成功！！！")

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
    
    '''
    #输入框说明
    input_text_info=tkinter.Text(root)
    input_text_info.insert('end','请在此输入需要匹配的串')
    '''
    
    # 输入框
    input_text = tkinter.Entry(root, bd=3, width=54)
    input_text.insert('end','请在此输入需要匹配的串')
    
    # btn width 85, height 35
    Btn_0 = tkinter.Button(root, command=lambda: btn0(LB_txt1, x), text="消除无用及\n有害规则", activebackground="blue", activeforeground="white", bd=4, width=10,height=2)
    Btn_1 = tkinter.Button(root, command=lambda: btn1(LB_txt1, x), text="打开文件", activebackground="blue", activeforeground="white", bd=4, width=10,height=2)
    Btn_2 = tkinter.Button(root, command=lambda: btn2(LB_txt2, x), text="消除左递归", activebackground="blue", activeforeground="white", bd=4, width=10,height=2)
    Btn_3 = tkinter.Button(root, command=lambda: btn3(LB_txt3, x), text="消除左公因子", activebackground="blue",activeforeground="white", bd=4, width=10,height=2)
    Btn_4 = tkinter.Button(root, command=lambda: btn4(LB_first,x),text="生成first集", activebackground="blue", activeforeground="white", bd=4, width=10, height=2)
    Btn_5 = tkinter.Button(root, command=lambda: btn5(LB_follow,x),text="生成follow集", activebackground="blue",activeforeground="white", bd=4, width=10,height=2)
    Btn_6 = tkinter.Button(root, command=lambda: btn6(x), text="生成Table表", activebackground="blue",activeforeground="white", bd=4, width=10,height=2)
    Btn_7 = tkinter.Button(root, command=lambda: is_legal(input_text,x),text="判定栈情况", activebackground="blue",activeforeground="white", bd=4, width=10,height=2)

    # 绝对布局
    #input_text_info.place(x=200,y=480)
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
    print(x.Table)


if __name__ == "__main__":
    GUI()

