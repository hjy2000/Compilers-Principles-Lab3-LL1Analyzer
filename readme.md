    数据结构 ：
    终结符（Tset），非终结符（NTset），文法开始符（S）， 产生式（Production）, 
    FIRST集（firstset），FOLLOW集（followset）, LL(1)分析表（Table）,工作过程表(work_process)
    
    各个参数的数据存放形式：
    Tset：[]列表
    NTset:[]列表
    S: 'S' 字符串
    Production:{},例如：A->aA|b, 就是表示为{'A': ["aA","b"]}
    firstset: {}, 例如：fisrt(A):(a,b),就是表示为{‘A’:["a","b"]}
    followset:{},同firstset一样
    Table:{}嵌套字典，例如：M[A,a] = (A->a)，那么就是表示为{'A':{'a':['A->a']}} ，若M[A,(] = "A->(abc" 则表示为{'A':{'(':["A->(abc"]}}
    work_process:[]列表，用于存储工作过程
    
    测试样例：
    （1）
    S->Qc|c
    Q->Rb|b
    R->Sa|a
    （2）
    S->S+S|S-S|S*S|S/S| (S)
    （3）
    S->TS'
    S'->+TS'|ε
    T->FT'
    T'->*FT'|ε
    F->(S)|i
    （4）
    A->ab1 | ab2 | Dc | Ac |Acc 消除左递归新生成的生成式，还有可能存在最左公因子，故消除左递归新的终结符为A',最左公因子用A''
    D->ad                           
    （5）
    A->aB|abD|abDE
    （6）
    S->ac|abd|cc|cce
    （7）
    S->LA
    L->i:|ε
    A->i=e
