# Copyright (C) 2022 Allen Yuqing Yang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from danger_analysis import traverse
from get_pdg import get_node_computed_value_e
from pdg_js.build_pdg import get_data_flow
# TODO
# 1. add the tainted variable set
# 2. add resolving for variable names
# 3. add function map
# There could be function calls that we do not know whether sanitizes, but it is okay. 

# !!! we think of functions involving tainted params as used first please
# in_cond will let the lookup abort for memberexpression in cond
# consider_pureobj will take .extraData also as tainted
def look_for_involve_data(node):
    flag=False
    if node.name in ('IfStatement','ForStatement','WhileStatement','ConditionalExpression'):
        flag=look_for_idcheck(node)
        if flag:
            # print('checked')
            return False
    elif node.name in ['Identifier','MemberExpression']:
        v=get_node_computed_value_e(node)
        if v==None:
            
            return False
        if (type(v)==str and "referrerInfo.extraData" in v and not v.endswith('extraData')):
            
            return True

    for child in node.children:
        flag=look_for_involve_data(child)
        if flag:
            return True
    return flag
def look_for_data_use(node,tainted_vars,consider_pureobj=False, in_cond=False):
    flag=False
    pure=False
    

    if node.name in ['Identifier', 'MemberExpression']:
        v=get_node_computed_value_e(node)
        if v==None:
            return False,False

        if (type(v)==str and "referrerInfo.extraData" in v):
            # return True, False
            if consider_pureobj:
                if v.endswith("referrerInfo.extraData"):
                    if not in_cond:
                        return True,True
                else:
                    
                    return True, False
            else:
                if not v.endswith("referrerInfo.extraData"):
                    
                    return True, False
        
                

        for taintedvar in tainted_vars:
            if type(v)==str and v.startswith(taintedvar):
                if not tainted_vars[taintedvar]:
                    return True, False
                if consider_pureobj:
                    if v==taintedvar:
                        return True, True
                    else:
                        # print(node.get_loc(),v,taintedvar)

                        return True, False
                elif taintedvar!=v:
                    return True, False
    #elif node.type=='ObjectExpression':
    # if node.name=='MemberExpression' and in_cond:
    #     return False, False
        # if did not find the tainted value in the memberexpr, skip the rest of the children of memberexpr
    for child in node.children:
        flag,pure=look_for_data_use(child,tainted_vars,consider_pureobj=consider_pureobj,in_cond=in_cond)

        if flag:
            return flag,pure
    return flag,pure

# def look_for_param_use(node,params,consider_pureobj=False,check_caller=False):

def look_for_param_use_all(node,func,param_used,in_cond=False):
    if node.name in ['Identifier', 'MemberExpression']:
        v=get_node_computed_value_e(node)
        
        if v!=None:
            for index in func.params:
                #{name tainted, tainted_pure}
                item=func.params[index]
                taintedvar=item['name']
                if taintedvar==None:
                    continue
                # if param_used or data_used:
                #     continue 
                if type(v)==str and v.startswith(taintedvar):  
                    param_used=True
                # elif
                    # if v==taintedvar:
                    #     pure=True
                    # elif taintedvar!=v:
                    #     pure=False
    
    #elif node.type=='ObjectExpression':
    if node.name=='MemberExpression' and in_cond:
        return param_used
        # if did not find the tainted value in the memberexpr, skip the rest of the children of memberexpr
    for child in node.children:
        param_used=look_for_param_use_all(child,func,param_used,in_cond=in_cond)

    return param_used

def look_for_param_use_in_priv(node,func,param_used,data_used,in_cond=False):
    if node.name in ['Identifier', 'MemberExpression']:
        v=get_node_computed_value_e(node)
        
        if v!=None:
            for index in func.params:
                #{name tainted, tainted_pure}
                item=func.params[index]
                taintedvar=item['name']
                if taintedvar==None:
                    continue
                # if param_used or data_used:
                #     continue 
                if 'extraData' in str(v):
                    data_used=True
                elif type(v)==str and v.startswith(taintedvar):  
                    param_used=True
                # elif
                    # if v==taintedvar:
                    #     pure=True
                    # elif taintedvar!=v:
                    #     pure=False
    
    #elif node.type=='ObjectExpression':
    if node.name=='MemberExpression' and in_cond:
        return param_used,data_used
        # if did not find the tainted value in the memberexpr, skip the rest of the children of memberexpr
    for child in node.children:
        param_used,data_used=look_for_param_use_in_priv(child,func,param_used,data_used,in_cond=in_cond)

    return param_used,data_used

def look_for_param_use(node,func, in_cond=False):
    flag=False
    pure=False
    if node.name in ['Identifier', 'MemberExpression']:
        v=get_node_computed_value_e(node)
        
        if v!=None:

            for index in func.params:
                #{name tainted, tainted_pure}
                item=func.params[index]
                taintedvar=item['name']
                if taintedvar==None:
                    continue
                if item['tainted']:
                        continue 
                elif type(v)==str and v.startswith(taintedvar):  
                    item['tainted']=True
                    if v==taintedvar:
                        item['tainted_pure']=True
                    elif taintedvar!=v:
                        item['tainted_pure']=False
    
    #elif node.type=='ObjectExpression':
    if node.name=='MemberExpression' and in_cond:
        return 
        # if did not find the tainted value in the memberexpr, skip the rest of the children of memberexpr
    for child in node.children:
        look_for_param_use(child,func,in_cond=in_cond)
        
    return 

def related_to_appid(node):
    v=get_node_computed_value_e(node)
    if v!=None and type(v)==str and 'appId' in v:
        return True
    for child in node.children:
        if child==None:
            continue
        if related_to_appid(child):
            return True
    return False
def has_id_in_binexpr(node):
    
    if node.name=='BinaryExpression':
        left=None
        right=None
        op=node.attributes['operator']
        for child in node.children:
            if child==None:
                continue
            
            if child.body=='left':
                left=child
            elif child.body=='right':
                right=child
        if op in ('==','===','!=','!==','in'):               
            if left!=None:
                if related_to_appid(left):
                    return True
            if right!=None:
                if related_to_appid(right):
                    return True
        
    
    for child in node.children:
        if child==None:
            continue
        if has_id_in_binexpr(child):
            return True
    return False
def look_for_idcheck(node):
    
    for child in node.children:
        if child.body in ('cond','test'): # child is a binary expr
            if has_id_in_binexpr(child):
                return True
    return False



def match_tainted_member():
    # match the left node and the right node
    a=1

def check_related_to_taint():
    # traverse the nested binary expression and get nodes related to referrerInfo and tainted variable
    a=1

def traverseChildren(node,func,tainted_vars,logs,filename):
    # if is block stmt and some vulnerability found or some sanitization found, stop the traversal
    if node.children==None:
        return False, False
    for child in node.children:
        sanitized, vuln=find_vulnerability_in_func(child,func,tainted_vars,logs,filename)
        if sanitized or vuln:
            return sanitized, vuln
    return False, False



class Func:
    def  __init__(self,name,node,params):
        self.children=[] # [{name:'', taintedparam:[]}]
        self.priv_children=set() # reachable called functions with related parameter
        self.apis_called_with_data=set()
        self.priv_invoked={} # {'request': {'param_used': False, 'data_used': True}}
        self.id=node.id
        self.name=name#a global id
        self.AST_node=node
        self.vulnerable=False
        self.params=params

def log_vulnerability(vulntype,node,func,filename,logs):
    logs['result'].append({'vulntype':vulntype,'funcname':func.name,'filename':filename,'loc':rephrase_loc(node.get_loc())})

def rephrase_loc(locstr):
    locdict=eval(locstr)
    br=locdict['start']['line']
    bc=locdict['start']['column']
    er=locdict['end']['line']
    ec=locdict['end']['column']
    return locdict

def find_vulnerability_in_func(node,func,tainted_vars,logs,filename): 
    a=1

    if node.visited:
        # print('visited')
        return False,False
    
    node.visited=True
    
    # traverse, triggered by extraData related value
    # if in ifstmt etc and checked, sanitized and stop the corresponding passing
        # sanitized=True
    
    sanitized=False
    tainted=False
    vuln=False
    # if '16144' in node.get_loc():
    
    # if if statement and related to appId
    # TODO add logical expression
    if node.name in ('IfStatement','ForStatement','WhileStatement','ConditionalExpression'):
        flag=look_for_idcheck(node)
        if flag:
            # print('checked')
            logs['checked']=True
            sanitized=True
            func.sanitized=True
            return True, False
            # add this to callgraph with sanitized on
            # func.sanitized=True
            # return True
        # return traverseChildren(node,func)
    flag=look_for_involve_data(node)
    if flag:
        logs['involved']=True

    if node.name in ('IfStatement','ForStatement','WhileStatement'):
        flag=False
        pure=False
        bodynode=None
        for child in node.children:
            if hasattr(child,'body'):
                if child.body in ('cond','test'):
                    flag,pure=look_for_data_use(child,tainted_vars,in_cond=True,consider_pureobj=False)# there is only one test/cond so will not be overwritten
                    look_for_param_use(child,func,in_cond=True)
                elif child.body in ('body'):
                    bodynode=child
        

        if flag:
            vuln=True
            func.vuln=True
            log_vulnerability('condition', node, func, filename, logs)
            # print('vuln_cond',node.get_loc())
            # exit()
            # return False, True
        if bodynode!=None:
            return find_vulnerability_in_func(bodynode,func,tainted_vars,logs,filename)
            
    # elif node.name in ('Identifier','MemberExpression'):

    elif node.name in ('AssignmentExpression'):
        a=1
        nodevalue=""
        flag=False
        pure=False
        for child in node.children:
            if child.body=='left':
                nodevalue=get_node_computed_value_e(child)
            elif child.body=='right':
                flag,pure=find_taint(child,tainted_vars)
                if flag and child.name=='BinaryExpression':
                    log_vulnerability('binary', node, func, filename, logs)
                    # print('vuln_binary_assignment')
        # TODO: add += -=

        if nodevalue!="" and flag:
            tainted_vars[nodevalue]=pure
        # if right related to taint and is exactly Identifier or ObjectExpr, propagate (done)
        # TODO if right related to tainted and is computed, including binary expr and call expression, vuln
    elif node.name in ('VariableDeclaration'):
        declaration=None
        for child in node.children:
            if child.body=='declarations':
                declaration=child
        nodevalue=""
        flag=False
        pure=False
        for child in declaration.children:
            
            if child.body=='id':
                nodevalue=get_node_computed_value_e(child)
            elif child.body=='init':
                flag,pure=find_taint(child,tainted_vars)
                if flag and child.name=='BinaryExpression':
                    log_vulnerability('binary', node, func, filename, logs)
                    # print('vuln_binary_assignment')
        if flag and nodevalue!="":
            tainted_vars[nodevalue]=pure
    elif node.name in ('ObjectExpression'):
        flag=False
        flag,pure=look_for_data_use(node,tainted_vars,in_cond=True,consider_pureobj=False)
        look_for_param_use(node,func,in_cond=True)
        if flag:
            vuln=True
            func.vuln=True
            log_vulnerability('object', node, func, filename, logs)

            # print('vulnerable_object',node.get_loc())
            # exit()
            # return False, True
            
    elif node.name in ('FunctionExpression'):
        tainted_vars={}
    elif node.name in ('CallExpression'):
        a=1
        paramcnt=0
        taintedparams={}
        taintednonpureparams={}
        calleename=""
        flag=False
        pure=False
        for child in node.children:
            if child.body=='callee':
                calleename=get_node_computed_value_e(child)
            elif child.body=='arguments':
                paramcnt+=1
                flag,pure=look_for_data_use(child,tainted_vars,in_cond=False,consider_pureobj=True)
                paramuse=look_for_param_use_all(node,func,False,in_cond=True)
                if flag:
                    taintedparams[paramcnt]=pure
                if paramuse and type(calleename)==str:
                    func.priv_children.add(calleename.split(".")[-1])
                if flag and type(calleename)==str:
                    taintedparams[paramcnt]=pure
                    func.apis_called_with_data.add(calleename.split(".")[-1])
        if len(taintedparams)>0 and calleename!="" and calleename!=None:
            func.children.append({'type':'normal','name':calleename,'taintedparam':taintedparams})
        if type(calleename)==str:
            calledfuncname=calleename.split(".")[-1]
            if calledfuncname in privilegedfunclist:
                flag,pure=look_for_data_use(child,tainted_vars,in_cond=False,consider_pureobj=True)
                
                param_used,data_used=look_for_param_use_in_priv(node,func,False,False,in_cond=True)
                if calledfuncname not in func.priv_invoked:
                    func.priv_invoked[calledfuncname]={'param_used': param_used,'data_used': data_used,'with_param': True}
                else:
                    func.priv_invoked[calledfuncname]['param_used']=func.priv_invoked[calledfuncname]['param_used'] or param_used
                    func.priv_invoked[calledfuncname]['data_used']=func.priv_invoked[calledfuncname]['data_used'] or data_used
                # print("WITH_PARAM",func.priv_invoked)
            elif calledfuncname in privilegedfunclist_nonparam:
                flag,pure=look_for_data_use(child,tainted_vars,in_cond=False,consider_pureobj=True)
                param_used,data_used=look_for_param_use_in_priv(node,func,False,False,in_cond=True)
                if calledfuncname not in func.priv_invoked:
                    func.priv_invoked[calledfuncname]={'param_used': param_used,'data_used': data_used,'with_param': False}
            # print("WITHOUT_PARAM",func.priv_invoked)
            
            # TRAVERSE_PARAM, if any argument relate to extradata, mark it

        # if parameter related to tainted, add this to call graph with used flag on
        # resolve funccallname
    elif node.name in ('BinaryExpression'):
        a=1
   
    return traverseChildren(node,func,tainted_vars,logs,filename)
    # return traverse children

       


def find_taint(node,tainted_vars):
    flag=False
    pure=False
    if 'extraData' in str(get_node_computed_value_e(node)):
        
        if str(get_node_computed_value_e(node)).endswith('extraData'):
            return True, True
        else:
            return True, False
    for v in tainted_vars:
        if v==None:
            return False,False
        if str(get_node_computed_value_e(node)).startswith(v):
            if not tainted_vars[v]:
                return True,True
            elif str(get_node_computed_value_e(node))==v:
                return True,True
            else:
                return True, False
    for child in node.children:
        flag,pure=find_taint(child,tainted_vars)
        if flag:
            return flag,pure
    return flag,pure
    
def resolve_param(child):
    if child.name=='Identifier':
        return {'name':get_node_computed_value_e(child),'tainted':False,'tainted_pure':False}
    elif child.name=='AssignmentPattern':
        for valuenode in child.children:
            if valuenode.body=='left':
                if valuenode.name=='Identifier':
                    return {'name':get_node_computed_value_e(child),'tainted':False,'tainted_pure':False}
    return {'name':'//NOT_FOUND//','tainted':False,'tainted_pure':False}

def traverse_all_files(node,filefuncmap):
    filename=""
    
    if node.name=='CallExpression':
        if get_node_computed_value_e(node.children[0])=='define' and len(node.children)==3 and node.children[0].name=='Identifier' and node.children[1].name=='Literal' and node.children[2].name=='FunctionExpression':
            funcmap={}
            filename=get_node_computed_value_e(node.children[1])
            traverse_all_functions(node.children[2],funcmap)
            filefuncmap[filename]=funcmap
            return
    for child in node.children:
        traverse_all_files(child,filefuncmap)    

def traverse_all_functions(node,funcmap):
    
    if node.name=='FunctionDeclaration':
        funcnode=node
        funcname=''
        params={}
        paramcnt=0
        for child in node.children:
            if child.body=='id' :
                funcname=child.attributes['name']
            elif child.body=='params':
                paramcnt+=1
                params[paramcnt]=resolve_param(child)
                # for param in child.children:
        if funcname!='':
            funcmap[funcname]=Func(funcname,funcnode,params)
    elif node.name=='FunctionExpression':
        if node.parent !=None:
            # do finding the 
            resolved_type_III=False
            if node.parent.parent!=None and node.parent.parent.name=='ObjectExpression': 
                # {"key": "Func","value": function()}
                # ObjectExpr-Property-Identifier
                funcnode=None
                funcname=''
                params={}
                paramcnt=0
                for property in node.parent.parent.children:
                    nameflag=False
                    funcflag=False
                    if property.name!='Property':
                        continue
                    for child in property.children:

                        if child.name=='Identifier':
                            if child.attributes['name']=='key':
                                nameflag=True
                            elif child.attributes['name']=='value':
                                funcflag=True
                            continue
                        if child.name=='Literal' and nameflag:
                            funcname=child.attributes['value']
                        elif child.name=='FunctionExpression' and funcflag:
                            funcnode=child
                for child in node.children:
                    if child.body=='params':
                        paramcnt+=1
                        params[paramcnt]=resolve_param(child)
                if funcname!='' and funcnode!=None:
                    resolved_type_III=True
                    
                    funcmap[funcname]=Func(funcname,funcnode,params)
                    

            if node.parent.name=='Property' and not resolved_type_III:  # App(){onLoad: function()}
                funcnode=node
                funcname=''
                params={}
                paramcnt=0

                for child in node.parent.children:
                    if child.name=='Identifier':
                        funcname=child.attributes['name']
                    elif child.name=='FunctionExpression':
                        funcnode=child
                for child in node.children:
                    if child.body=='params':
                        paramcnt+=1
                        params[paramcnt]=resolve_param(child)

                if funcname!='' and funcnode!=None:
                    funcmap[funcname]=Func(funcname,funcnode,params)

            
    for child in node.children:
        traverse_all_functions(child,funcmap)



# def traverse_funcnode_for_privilege(funcmap, funcnode):
def find_caller_with_data(func,funcmap,reversefuncmap,res,visitedset):
    result=False
    # print(func,"SDSDSSDSDS",visitedset)

    if func in visitedset or func not in reversefuncmap: # when reaching visited node
        return result
    visitedset.add(func)
    for called_by in reversefuncmap[func]['param_connected_by']:
        for parent_called in funcmap[called_by].apis_called_with_data:
            # print("****VISITING",func,'CALLED BY',called_by,'WHO CALLED',str(funcmap[called_by].apis_called_with_data))
            if func in parent_called:
                result=True
        result=result or find_caller_with_data(called_by,funcmap,reversefuncmap,res,visitedset)
    
    return result

# nodes=get_data_flow('test1.js',{})
import glob, os, time, sys
def analyze_a_wxapkg(wxid):
    print(wxid)
    t=time.time()
    # wxid='wxe0e3947bdc7d99ec'
    # walk_dir=folder+"/"+wxid+'-dec'
    walk_dir='/home/allen/Github/SP23/DoubleX/src/output/'+wxid+'-dec/'

    logs={'result':[],'checked':False,'involved':False,'sensitiveAPIs':{}}
    global privilegedfunclist
    global privilegedfunclist_nonparam
    global visitedset
    privilegedfunclist_nonparam=["connectSocket",
    "createVideoContext",
    "createWebAudioContext",
    "createMediaAudioPlayer",
    "createInnerAudioContext",
    "createAudioContext",
    "getBackgroundAudioManager",
    "getRecorderManager",
    "getFileSystemManager",
    "getAccountInfoSync",
    "getUserInfo",
    "login",
    "getUserProfile",
    "authorizeForMiniProgram",
    "authorize",
    "openSetting",
    "getSetting",
    "chooseAddress",
    "getStorageInfo",
    "getStorageSync",
    "getStorageInfoSync",
    "getStorage",
    "chooseInvoiceTitle",
    "chooseInvoice",
    "getWeRunData",
    "chooseLicensePlate",
    "getGroupEnterInfo",
    "openCustomerServiceChat",
    "openBluetoothAdapter",
    "makeBluetoothPair",
    "chooseImage",
    "chooseVideo",
    "createCameraContext",
    "getLocation",
    "openLocation",
    "chooseMedia",
    "chooseMessageFile",
    "createBLEConnection",
    "createBLEPeripheralServer",
    "startBeaconDiscovery"]
 
    privilegedfunclist=["request",
    "uploadFile",
    "createTCPSocket",
    "send",
    "saveImageToPhotosAlbu",
    "saveVideoToPhotosAlbum",
    "createMapContext",
    "createMediaAudioPlayer",
    "sendSocketMessage",
    "write",
    "requestPluginPayment",
    "requestPayment",
    "saveImageToPhotosAlbum",
    "saveVideoToPhotosAlbum",
    "openVideoEditor",
    "getVideoInfo",
    "chooseVideo",
    "chooseMedia",
    "addCard",
    "openCard",
    "startSoterAuthentication",
    "shareToWeRun",
    "requestSubscribeMessage",
    "requestSubscribeDeviceMessage",
    "writeBLECharacteristicValue",
    "addService",
    "setStorageSync",
    "setStorage",
    "setData"]
    # walk_dir='/home/allen/Github/SP23/DoubleX/src/output/wxefd7b04e86c5baaa-dec'
    alljsfiles=[]
    for root, dirs, files in os.walk(walk_dir):
        
        for file in files:
            
            if file.endswith("min.js"):
                continue
            # if file.endswith(".js"):
            if file.endswith("app-service.js"):
                
                functioncallmap={}
                fn=os.path.join(root, file)
                print(fn)
                nodes=get_data_flow(fn,{})
                print('ast gen complete')
                funcfilemap={}
                
                traverse_all_files(nodes,funcfilemap)
                for filename in funcfilemap:
                    # if 'nonepage' not in filename :
                    #     continue

                    reversefuncmap={}
                    param_use_set=set()
                    data_use_set=set()

                    funcmap=funcfilemap[filename]

                    for funcname in funcmap:
                        funcnode=funcmap[funcname]
                        # print(funcname,funcnode.params)
                        find_vulnerability_in_func(funcnode.AST_node,funcnode,{},logs,filename)
                    for func in funcmap:
                        for child in funcmap[func].priv_children:
                            # print("____",func,"called",child)
                            if child not in reversefuncmap:
                                if child in funcmap:
                                    reversefuncmap[child]={'param_connected_by':set(),'priv_invoked':funcmap[child].priv_invoked}
                                else:
                                    reversefuncmap[child]={'param_connected_by':set(),'priv_invoked':{'data_used': False, 'param_used': False}}
                            reversefuncmap[child]['param_connected_by'].add(func)
                            
                            # reverseprivmap[child].add(func)
                    for funcname in funcmap:
                        funcnode=funcmap[funcname]
                        for funccall in funcnode.children:
                            
                            #     if funccall['name'] not in reversefuncmap:  
                                    
                            #         reversefuncmap[funccall['name']]={'param_connected_by':[],'priv_invoked':funcmap[funccall['name']].priv_invoked}
                            #     reversefuncmap[funccall['name']]['param_connected_by'].append({'name':funcname,'used_param':False}) 

                            if len(funccall['taintedparam'])>0 and funccall['name'] in funcmap:
                                calledfuncnode=funcmap[funccall['name']]
                                
                                for paramid in funccall['taintedparam']:
                                    if paramid>len(calledfuncnode.params)-1:
                                        continue
                                    if not funccall['taintedparam'][paramid]:
                                        if calledfuncnode.params[paramid]['tainted']:
                                            log_vulnerability('call', funcnode.AST_node, funcnode, filename, logs)
                                            # print('vuln_funccall')
                                    else:
                                        if calledfuncnode.params[paramid]['tainted'] and not calledfuncnode.params[paramid]['tainted_pure']:
                                            log_vulnerability('call', funcnode.AST_node, funcnode, filename, logs)
                                            reversefuncmap[funccall['name']]['param_connected_by'][funcname]['used_param']=True

                                            # print('vuln_funccall')
                    
                    # print("!!!",param_use_set)
                    for func in reversefuncmap:
                        for child in reversefuncmap[func]['param_connected_by']:
                            calledlist='None'
                            if func in funcmap:
                                calledlist=str(funcmap[child].apis_called_with_data)
                            # print("_____",func,'paramatically linked by',child,"||functions called by",child, "with extradata transfered: "+calledlist)
                    for func in funcmap:
                        # if this one is used param, start a traversal with skip to explored function, to find a function whose called by contains the function itself. If so, result will be true
                        
                        if funcmap[func].priv_invoked!={}:
                            for involvedfunc in funcmap[func].priv_invoked:
                                if funcmap[func].priv_invoked[involvedfunc]['with_param']:
                                    if funcmap[func].priv_invoked[involvedfunc]['data_used']:
                                        # print("VULN paramatic func via extra",func,"->",involvedfunc)
                                        if involvedfunc not in logs['sensitiveAPIs']:
                                            logs['sensitiveAPIs'][involvedfunc]=[]
                                        logs['sensitiveAPIs'][involvedfunc].append({'called_by':func,'type':'parametic_via_extradata'})
                                    elif funcmap[func].priv_invoked[involvedfunc]['param_used']:
                                        
                                        # res=False
                                        res=find_caller_with_data(func,funcmap,reversefuncmap,False,set())
                                        if res:
                                            # print("VULN praramatic func via param",func,"->",involvedfunc)
                                            if involvedfunc not in logs['sensitiveAPIs']:
                                                logs['sensitiveAPIs'][involvedfunc]=[]
                                            logs['sensitiveAPIs'][involvedfunc].append({'called_by':func,'type':'parametic_via_param'})
                                else:
                                    # res=False
                                    res=find_caller_with_data(func,funcmap,reversefuncmap,False,set())
                                    if res:
                                        # print("VULN non-paramatic func (via param)",func,"->",involvedfunc)
                                        if involvedfunc not in logs['sensitiveAPIs']:
                                            logs['sensitiveAPIs'][involvedfunc]=[]
                                        logs['sensitiveAPIs'][involvedfunc].append({'called_by':func,'type':'nonparametic'})
                    # print("!!!",reverseprivmap)
                    # for  in reversefuncmap:
                    #     for privfunc in leaf['priv_invoked']:
                    #         if leaf['priv_invoked'][privfunc]['data_used']:
                    #             logs.sensitiveAPIs.add(privfunc)
                    #         elif leaf['priv_invoked'][privfunc]['param_used']:

                # if len(logs)==0:
                #     logs=None
                break
                print('analysis complete')
    exec_time=time.time()-t
    return logs,exec_time
    # print((time.time()-t))
# print (nodes)
def analyze_from_wxapkg(batch,wxid):
    # batch='22'
    # wxid='wxcd538bb3d50152f1'
    analysis_res,exec_time=analyze_a_wxapkg(wxid)
    finalresult={'batch':batch,'wxid':wxid,'res':analysis_res,'exec_time':exec_time}
    return finalresult

# print(time.time())
# import sys
# res=analyze_a_wxapkg(sys.argv[1])
# print("res",res)
# print(time.time())