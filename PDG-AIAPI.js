const fs=require('fs')
const readfile=require('./readFile.js')
const escodegen =require('escodegen')

const esprima = require('esprima');
const checkCondition=require('./checkCondition.js')
const options = {
    loc: true,  //  位置信息
    range: false,    //  位置信息
    jsx: false,  //  支持jsx语法
    tolerant: false,
    tokens: false,
    comment: false
}
function translateObject(objnode){
    
    return escodegen.generate(objnode)
    var str="{"
    for(var k=0;k<objnode.properties.length;k++){
        str=str+objnode.properties[k].key.name+":"
        if(objnode.properties[k].value.type==='Identifier'){
            str=str+objnode.properties[k].value.name
        }else if(objnode.properties[k].value.type==='Literal'){
            str=str+objnode.properties[k].value.raw
        }else if(objnode.properties[k].value.type==='MemberExpression'){
            str=str+translateMember(objnode.properties[k].value)
        }else if(objnode.properties[k].value.type==='ObjectExpression'){
            str=str+translateObject(objnode.properties[k].value)
            
        } 
        if(k!=objnode.properties.length-1)
            str=str+","  
    }
    str=str+"}"
    return str
}

function translateMember(memnode){
    return escodegen.generate(memnode)
    str=""
    if(memnode.object.type==='MemberExpression'){
        str=translateMember(memnode.object)
    }else if(memnode.object.type==='Identifier'){
        str=memnode.object.name
    }
    str=str+"."+memnode.property.name
    return str
}
function mergeextra(extra1,extra2){
    if(extra2==null){
        return
    }
    for(var s in extra2){
        if(s in extra1){
            for(var k in extra2[s]){

                if(!(extra2[s][k] in extra1[s]))extra1[s].push(extra2[s][k])
            }
        }else{
            extra1[s]=extra2[s]
        }
    }
}

var credentialfunctionlist=['getUserInfo','getLocation','getWeRunData','saveImageToPhotosAlbum','getFriendCloudStorage','getGroupCloudStorage','getGroupInfo','getPotentialFriendList','getUserCloudStorageKeys','getUserInfo','getFriendsStateData','getUserInteractiveStorage']// if not sent online, either over-privileged, or decrypted in the frontend
var privilegefunclist=['openUrl','getDeviceInfo','addDownloadTaskStraight','installDownloadTask']
credentialfunctionlist=["ocrIdCard","ocrBankCard","ocrDrivingLicense","ocrVehicleLicense","textReview","nlpLexerCustom","advancedGeneralIdentity","animalClassify","carClassify","dishClarssify","logoClassify","objectDetectIdentify","plantClassify","imageAudit","getVoiceRecognizer","textToAudio","faceDetect","faceMatch","faceSearch","facePersonVerify","facePersonIdmatch","faceLivenessSessioncode"]
privilegefunclist=["ocrIdCard","ocrBankCard","ocrDrivingLicense","ocrVehicleLicense","textReview","nlpLexerCustom","advancedGeneralIdentity","animalClassify","carClassify","dishClarssify","logoClassify","objectDetectIdentify","plantClassify","imageAudit","getVoiceRecognizer","textToAudio","faceDetect","faceMatch","faceSearch","facePersonVerify","facePersonIdmatch","faceLivenessSessioncode"]
function func2type(name){
    switch (name){
        case 'login':

    }
}
function traverse(func,parent,filepath,node,res,extra){
    // vardeclaration -> vardeclarator ->
    // if(node.type==='ConditionalExpression'){
    //     console.log(node)
    // }
    if(node==null){
        return
    }
    node.parent=parent
    node.declare={}
    node.called={}
    node.extra= {}
//    process(filepath,node,res,extra)
    // if(node.type==='CallExpression'){
    //     console.log(node)
    // }
    switch (node.type) {
        case 'Program':
            let body=node.body
            for (var j=0;j<body.length;j++){
                traverse(func,node,filepath,body[j],res,extra)
            }
            break
        case 'VariableDeclaration':

            let declarations=node.declarations
            for (var j=0;j<declarations.length;j++){
                traverse(func,node,filepath,declarations[j],res,extra)
            }

            // mergeextra(parent.extra,node.extra)

            break
        case 'VariableDeclarator':
            // if is interested variable
            func.declare[node.id.name]=node
            let init=node.init
            if(init===null){
                return
            }
            traverse(func,node,filepath,init,res,extra)

            // parent.extra=JSON.parse(JSON.stringify(node.extra))
            // for(var k in parent.extra){
                // parent.extra[k].push(node.id.name)
            // }
//            res.totallength=res.totallength+node.id.name.length
//            res.totalvars=res.totalvars+1
            break
        case 'CallExpression':
            traverse(func,node,filepath,node.callee,res,extra)
            for(var j=0;j<node.arguments.length;j++){
                traverse(func,node,filepath,node.arguments[j],res,extra)
            }
            if(node.callee.type==='Identifier'){
                if(node.callee.name==='require'){

                    if(node.arguments.length>0){
                        for(var k =0;k<node.arguments.length;k++){
//                        console.log(">??",node.arguments[k].type)
                            if(node.arguments[k].type==='Literal'&&(!node.arguments[k].value.includes('.js'))){
                                if(!(filepath in res.requires))res.requires[filepath]=[]
                                res.requires[filepath].push(node.arguments[k].value)
                            }
                        }                    
                    }                    
                }
            }
            if(node.callee.type==='MemberExpression'){

                if(node.callee.property.name==='updateShareMenu'&&node.arguments.length>0){
                    var shareprivate=null
                    
                    for(var k=0;k<node.arguments[0].properties.length;k++){
                        if(node.arguments[0].properties[k].key.name==='isPrivateMessage'){
                            shareprivate=node.arguments[0].properties[k]
                        }
                    }
                    if(shareprivate!=null&&shareprivate.value.type==='Literal'){
                        if(shareprivate.value.value){
                            res.secretshare.sent.push({
                                path: filepath,
                                loc: node.loc
                            })
                        }
                    }
                }else if(node.callee.property.name=='navigateToMiniProgram'){

                    var miniappid=''
                    var hasExtraData=false
                    var pagepath=""
                    var redirectpath=""
                    var extraData=""
                    if(node.arguments.length==0||node.arguments[0].type!=='ObjectExpression'){
                        break//currently we cannot handle wx.navigateToMiniProgram(t), because we do not have flow tracking
                    }   
                    for(var k=0;k<node.arguments[0].properties.length;k++){
                        if(node.arguments[0].properties[k].key.name==='appId'&&node.arguments[0].properties[k].value.value!=null){
                            miniappid=node.arguments[0].properties[k].value.value
                        }
                        else if(node.arguments[0].properties[k].key.name==='extraData'){
                            hasExtraData=true
                            if(node.arguments[0].properties[k].value.type==='Identifier'){
                                extraData=node.arguments[0].properties[k].value.name
                            }else if(node.arguments[0].properties[k].value.type==='Literal'){
                                extraData=node.arguments[0].properties[k].value.raw 
                            }else if(node.arguments[0].properties[k].value.type==='ObjectExpression'){
                                extraData=translateObject(node.arguments[0].properties[k].value)
                                
                            }else if(node.arguments[0].properties[k].value.type==='MemberExpression'){
                                extraData=translateMember(node.arguments[0].properties[k].value)
                                
                            }
                            
                        }
                        else if(node.arguments[0].properties[k].key.name==='path'){
                            if(node.arguments[0].properties[k].value.type==='Identifier'){
                                redirectpath=node.arguments[0].properties[k].value.name  
                                pagepath=node.arguments[0].properties[k].value.value

                            }else if(node.arguments[0].properties[k].value.type==='Literal'){
                                redirectpath=node.arguments[0].properties[k].value.raw 
                                pagepath=node.arguments[0].properties[k].value.value
                            }else if(node.arguments[0].properties[k].value.type==='ObjectExpression'){
                                redirectpath=translateObject(node.arguments[0].properties[k].value)
                                pagepath=node.arguments[0].properties[k].value.value

                            }else if(node.arguments[0].properties[k].value.type==='MemberExpression'){
                                redirectpath=translateMember(node.arguments[0].properties[k].value)
                                pagepath=node.arguments[0].properties[k].value.value

                            }
                        }
                    }
                    if(extraData!=="{}"&&extraData!=""){
                        res.navigationto.push({
                            appid: miniappid,
                            extradata:extraData,
                            path:redirectpath,
                            filepath: filepath,
                            topath: pagepath,
                            loc: node.loc
                        })
                    }
                    
                }
                else if(node.callee.property.name=='navigateBackMiniProgram'){
                    var miniappid=''
                    var hasExtraData=false
                    var pagepath=""
                    var redirectpath=""
                    var extraData=""
                    if(node.arguments.length==0||node.arguments[0].type!=='ObjectExpression'){
                        break//currently we cannot handle wx.navigateToMiniProgram(t), because we do not have flow tracking
                    }   
                    for(var k=0;k<node.arguments[0].properties.length;k++){
                        if(node.arguments[0].properties[k].key.name==='appId'&&node.arguments[0].properties[k].value.value!=null){
                            miniappid=node.arguments[0].properties[k].value.value
                        }
                        
                        else if(node.arguments[0].properties[k].key.name==='extraData'){
                            hasExtraData=true
                            if(node.arguments[0].properties[k].value.type==='Identifier'){
                                extraData=node.arguments[0].properties[k].value.name
                            }else if(node.arguments[0].properties[k].value.type==='Literal'){
                                extraData=node.arguments[0].properties[k].value.raw 
                            }else if(node.arguments[0].properties[k].value.type==='ObjectExpression'){
                                objectstr=translateObject(node.arguments[0].properties[k].value)
                                extraData=objectstr
                            }else if(node.arguments[0].properties[k].value.type==='MemberExpression'){
                                objectstr=translateMember(node.arguments[0].properties[k].value)
                                extraData=objectstr
                            }
                            
                        }
                        else if(node.arguments[0].properties[k].key.name==='path'){
                            if(node.arguments[0].properties[k].value.type==='Identifier'){
                                redirectpath=node.arguments[0].properties[k].value.name  
                                pagepath=node.arguments[0].properties[k].value.value

                            }else if(node.arguments[0].properties[k].value.type==='Literal'){
                                redirectpath=node.arguments[0].properties[k].value.raw 
                                pagepath=node.arguments[0].properties[k].value.value
                            }else if(node.arguments[0].properties[k].value.type==='ObjectExpression'){
                                redirectpath=translateObject(node.arguments[0].properties[k].value)
                                pagepath=node.arguments[0].properties[k].value.value

                            }else if(node.arguments[0].properties[k].value.type==='MemberExpression'){
                                redirectpath=translateMember(node.arguments[0].properties[k].value)
                                pagepath=node.arguments[0].properties[k].value.value

                            }
                        }
                    }
                    res.navigationback.push({
                        extradata:extraData,
                        urlpath: redirectpath,
                        filepath: filepath,
                        loc: node.loc
                    })
                }
                else if(node.callee.property.name==='makeBluetoothPair'){
                    res.blepairing.push({
                        path: filepath,
                        loc: node.loc
                    })
                }else if(node.callee.property.name==='authPrivateMessage'){
                    res.secretshare.checked.push({
                        path: filepath,
                        loc: node.loc
                    })
                }
                if(privilegefunclist.includes(node.callee.property.name)){
                    res.privilegefunclist.push({
                        name:node.callee.property.name,
                        loc: node.loc
                    })
                }
                //TODO: track interested functions and their related API calls in success/fail callbacks
                if(node.callee.property) {
                    if (node.callee.property.name === 'then') {
                        var arg=null
                        var funcname=""
                        if(!node.callee.object.callee){
                            break
                        }
                        if(node.callee.object.callee.type==='SequenceExpression'){
                            funcname=node.callee.object.callee.expressions[1].property.name
                        }else if(node.callee.object.callee.property){
                            funcname=node.callee.object.callee.property.name
                        }
                        if(credentialfunctionlist.includes(funcname)){
                            for(var k=0;k<node.arguments.length;k++){
                                arg=node.arguments[k]
                                var funclist = {func:[],susp_path:[],susp_prop:[]}
                                // console.log("???",arg.body)
                                if(arg==null)continue

                                checkCondition.traverseFunction(arg, filepath, arg, funclist)

                                if(funclist.func.length>0||funclist.susp_path.length>0||funclist.susp_prop.length>0){
                                    res.wxfuncmap.push({
                                        name: funcname,
                                        called: funclist,
                                        path: filepath,
                                        loc: node.loc
                                    })
                                }
                            }
                        }

                    }else if(credentialfunctionlist.includes(node.callee.property.name)){
//                        console.log("???",node.arguments[0].type)
                        if(node.arguments.length>0&&node.arguments[0].type==='ObjectExpression'){
                            for(var k=0;k<node.arguments[0].properties.length;k++){
                                var propertyname=node.arguments[0].properties[k].key.name
                                if(propertyname==='success'||propertyname==='fail'||propertyname==='finish'){
                                    var funclist={func:[],susp_path:[],susp_prop:[]}
                                    checkCondition.traverseFunction(node.arguments[0].properties[k].value,filepath,node.arguments[0].properties[k].value,funclist)

                                    if(funclist.func.length>0||funclist.susp_path.length>0||funclist.susp_prop.length>0){
                                        res.wxfuncmap.push({
                                            name:node.callee.property.name,
                                            called: funclist,
                                            path:filepath,
                                            loc:node.loc
                                        })
                                    }
                                }
                            }
                        }
                    }
                }
                // else{
                //     for(var k=0;k<node.arguments[0].properties.length;k++){
                //         var propertyname=node.arguments[0].properties[k].key.name
                //         if(propertyname==='success'||propertyname==='fail'||propertyname==='finish'){
                //             var funclist=[]
                //             checkCondition.traverseFunction(node,filepath,node,funclist)
                //             if(funclist.length>0){
                //                 res.wxfuncmap.push({
                //                     name:node.callee.property.name,
                //                     called: funclist,
                //                     path:filepath,
                //                     loc:node.loc
                //                 })
                //             }
                //         }
                //     }
                // }


            }
            break
        case 'FunctionExpression':
            if(node.parent.type==='Property'&&node.parent.key!=null){
                if(node.parent.key.type==='Identifier'&&node.params.length>0&&(['onLoad','onShow','onLaunch','onReady'].includes(node.parent.key.name))){
                    extra={varname:node.params[0].name,funcname:node.parent.key.name}
                }
    
            }
            
            traverse(node,node,filepath,node.body,res,extra)
            // if(node.loc.start.line===5){
            //     console.log(node.body.body[1])
            // }

            break
        case 'FunctionDeclaration':
            traverse(node,node,filepath,node.body,res,extra)

            break
        case 'BlockStatement':
            let blockbody=node.body
            for (var j=0;j<blockbody.length;j++){
                traverse(func,node,filepath,blockbody[j],res,extra)
            }

            break
        case 'ReturnStatement':
            if (node.argument===null){
                return
            }
            traverse(func,node,filepath,node.argument,res,extra)
            break
        case 'SequenceExpression': // aaa(), bbb(), ccc();
            let expressions=node.expressions
            for(var j=0;j<expressions.length;j++){
                traverse(func,node,filepath,expressions[j],res,extra)
            }
            break
        case 'ArrayExpression':
            let elements=node.elements
            for(var j=0;j<elements.length;j++){
                traverse(func,node,filepath,elements[j],res,extra)
            }
            break
        case 'ObjectExpression':

            for(var j=0;j<node.properties.length;j++){
//                 if(node.properties[j].key.name==='onShareAppMessage'){
//                     var functionbodies=node.properties[j].value.body.body
//                     for (var k=0;k<functionbodies.length;k++){
//                         if(functionbodies[k].type==='ReturnStatement'){
//                             if(functionbodies[k].argument.type==='ObjectExpression'){
//                                 var properties=functionbodies[k].argument.properties
//                                 for (var m=0;m<properties.length;m++){
                                    
//                                     if(properties[m].key.name==='path' && properties[m].value.value){
//  res.sharingpath.push({"filepath":filepath,"redirectpath":properties[m].value.value,"match":filepath.includes(properties[m].value.value)})
                                        
//                                     }
//                                 }
//                             }
//                         }
//                     }

//                 }
                traverse(func,node,filepath,node.properties[j],res,extra)
            }

            break
        case 'Property':
            if(node.value==null){
                return
            }
            traverse(func,node,filepath,node.value,res,extra)
            var flag=true

            // if(node.key.name==='isPrivateMessage' && node.value.value===true){// && node.value.type==='Literal' && node.value.value===false){
            //     // console.log(node.value.value)
            //     if(parent.extra.privatemsg==null){
            //         parent.extra.privatemsg=[]
            //     }
            //     parent.extra.privatemsg.push(node.key.name)
            //     flag=false
            // }
            // if(flag){
            //     for(var k in parent.extra){
            //         parent.extra[k].push(node.key.name)
            //     }
            // }

            break
        case 'ExpressionStatement':

            traverse(func,node,filepath,node.expression,res,extra)


            break
        case 'MemberExpression':
            if(node.property.name==='referrerInfo'){
                
                // if(node.parent.property && node.parent.property.name==='extraData')
            }
            // traverse(func,node,filepath,node.object,res,extra)
            var str=translateMember(node)
            if(str.includes("referrerInfo.extraData.")){
                res.referrerInfo.push({
                    variable:str,
                    filepath:filepath,
                    loc:node.loc
                })
            }else if(str.includes(extra.varname+".query.")){
                res.pathinfo.push({
                    variable:translateMember(node),
                    funcname:extra.funcname,
                    filepath:filepath,
                    loc:node.loc
                })
            }

            // parent.extra=JSON.parse(JSON.stringify(node.extra))
            break
        case 'IfStatement':
            traverse(func,node,filepath,node.test,res,extra)
            traverse(func,node,filepath,node.consequent,res,extra)
            if (node.alternate!=null){
                traverse(func,node,filepath,node.alternate,res,extra)
            }
            break
        case 'UnaryExpression':
            traverse(func,node,filepath,node.argument,res,extra)
            break
        case 'ConditionalExpression':
            traverse(func,node,filepath,node.test,res,extra)
            traverse(func,node,filepath,node.consequent,res,extra)
            traverse(func,node,filepath,node.alternate,res,extra)
            break
        case 'AssignmentExpression':
            traverse(func,node,filepath,node.left,res,extra)
            traverse(func,node,filepath,node.right,res,extra)

            break
        case 'TryStatement':
            traverse(func,node,filepath,node.block,res,extra)
            if (node.handler!=null){
                traverse(func,node,filepath,node.handler,res,extra)
            }
            if(node.finalizer!=null){
                traverse(func,node,filepath,node.finalizer,res,extra)
            }
            break
        case 'Identifier':
            if(node.name=='NativeGlobal'){
                res.privilegefunclist.push({
                    name:"NativeGlobal",
                    loc:node.loc
                })
            }
            break
        case 'Literal':
           if(node.value&&node.value.toString().match(/^([a-f0-9]{32})/g)!=null){
                res.appsecret.push({
                    secret: node.value,
                    verified: false,
                    truesecret: false,
                    path: filepath,
                    loc: node.loc
                })
            }
/*            if(node.value&&node.value.length==44&&node.value.toString().match(/^([a-z0-9A-Z+/]{44})/g)!=null){
                res.appsecret.push({
                    base64secret44: node.value,
                    verified: false,
                    truesecret: false,
                    path: filepath,
                    loc: node.loc
                })
            }else if(node.value&&node.value.length==24&&node.value.toString().match(/^([a-z0-9A-Z+/]{24})/g)!=null){
                res.appsecret.push({
                    base64secret24: node.value,
                    verified: false,
                    truesecret: false,
                    path: filepath,
                    loc: node.loc
                })
            }*/
            break
        case 'ThisExpression':
            break
        case 'ContinueStatement':
            break
        case 'BreakStatement':
            break
        case 'EmptyStatement':
            break
        case 'LabeledStatement':
            break
        case "SwitchStatement":
            traverse(func,node,filepath,node.discriminant,res,extra)
            for(var j=0;j<node.cases.length;j++){
                traverse(func,node,filepath,node.cases[j],res,extra)
            }
            break
        case 'WhileStatement':
            traverse(func,node,filepath,node.test,res,extra)
            traverse(func,node,filepath,node.body,res,extra)
            break
        case 'DoWhileStatement':
            traverse(func,node,filepath,node.body,res,extra)
            traverse(func,node,filepath,node.test,res,extra)
            break
        case "SwitchCase":
            if(node.test!=null){
                traverse(func,node,filepath,node.test,res,extra)
            }
            for(var j=0;j<node.consequent.length;j++){
                traverse(func,node,filepath,node.consequent[j],res,extra)
            }
            break
        case 'NewExpression':
            traverse(func,node,filepath,node.callee,res,extra)
            for(var j=0;j<node.arguments.length;j++){
                traverse(func,node,filepath,node.arguments[j],res,extra)
            }
            break
        case 'UpdateExpression':
            traverse(func,node,filepath,node.argument,res,extra)
            break
        case 'ThrowStatement':
            traverse(func,node,filepath,node.argument,res,extra)
            break
        case 'ForInStatement':
            traverse(func,node,filepath,node.left,res,extra)
            traverse(func,node,filepath,node.right,res,extra)
            break
        case 'CatchClause':
            traverse(func,node,filepath,node.param,res,extra)
            traverse(func,node,filepath,node.body,res,extra)
            break
        case 'ForStatement':
            if(node.init!=null){
                traverse(func,node,filepath,node.init,res,extra)
            }
            if(node.test!=null){
                traverse(func,node,filepath,node.test,res,extra)
            }
            if(node.update!=null){
                traverse(func,node,filepath,node.update,res,extra)
            }
            traverse(func,node,filepath,node.body,res,extra)
            break
        case 'BinaryExpression':

            traverse(func,node,filepath,node.left,res,extra)
            traverse(func,node,filepath,node.right,res,extra)
            break
        case 'LogicalExpression':
            //checkCondition();
            if(parent.type!=='LogicalExpression'&&parent.type!=='BinaryExpression'&&parent.type!=='ConditionalExpression'){
                var tempres= {appId:null,referrerInfo:null,checked:null,literal:[]}
                //appId: .appId; referrerInfo: existence of referrerInfo, checked: are there any 'wx' == appId
                checkCondition.traverseCondition(node,filepath,node,tempres)
                if(tempres.referrerInfo){
                    if(tempres.checked==null){
                        res.checkednavigation.push({
                            checked:false,
                            appid:[],
                            path: filepath,
                            loc:node.loc
                        })
                        // console.log('not checked')
                    }else{
                        if(tempres.literal.length===0){
                            // console.log('checked somehow')
                            res.checkednavigation.push({
                                checked:true,
                                appid:[],
                                path: filepath,
                                loc:node.loc
                            })
                        }else{
                            // console.log('checked to specific miniapp')
                            res.checkednavigation.push({
                                checked:true,
                                appid:tempres.literal,
                                path: filepath,
                                loc:node.loc
                            })
                        }
                    }
                }
            }

            traverse(func,node,filepath,node.left,res,extra)
            traverse(func,node,filepath,node.right,res,extra)
            break
        default:
            break
    }
    return res

    // else if (node.type=="")
}

function parseMiniapp(folder){
    global.res={
        blepairing: [], // list of {path:'xxx', loc:{}}
        blelevel: [], // list of {path: 'xxx', loc:{}, encryptedread: true,encryptedwrite:true}
        navigationto: [],
        navigationback: [],// list of {appid: 'xxx', path: 'xxx', loc: {}}
        referrerInfo:[],
        pathinfo:[],
        privilegefunclist:[],
        checkednavigation:[],//list of {checked:false,appid:null, path: 'xxx', loc:{}}
        appsecret: [], //list of {secret: 'xxx', verified: false, truesecret: false, path: 'xxx', loc:{}}
        wxfuncmap:[],//list of {name:'xxx', called: ['xxx'],'path:'xxx',loc:{}}
        secretshare:{
            sent:[], // list of {'path':'xxx',loc:{}}
            checked:[],// list of {'path':'xxx',loc:{}}
        },
        scopes: {}, //list of {'xxx': {declared: false, used: false}}
        requires: {}, // list of {'path': "", 'required':[""]}
        pluginjs:[],
        transpile:false,
        uglify: false,
        totalvars:0,
        totallength:0,
        sharingpath:[]
    }
    var fileList=[]
    readfile.readDirRecur(folder, function(filePath) {
        fileList.push(filePath)
    }).then(function() {
            for(var i=0;i<fileList.length;i++){
                var filePath=fileList[i]
                if(filePath.includes('.json')||filePath.includes('.ori.js')){
                    continue
                }
                else if(filePath.includes('@babel')){ 
                    global.res.transpile=true
                    continue
                }else if (filePath.includes('.js')){
                    const code = fs.readFileSync(fileList[i], 'utf8');
                    const ast = esprima.parse(code, options, function (node, metadata) {
                    });

                    var pagepath=fileList[i]
                    res=traverse(ast,null,pagepath,ast,global.res,{})
                    if(filePath.includes("__plugin__"))res.pluginjs.push(filePath)
                }
            }
        var obj={}
        obj.appsecret=global.res.appsecret
	obj.checkednavigation=global.res.checkednavigation
        obj.navigationto=global.res.navigationto
        obj.nagivationback=global.res.navigationback
        obj.referrerInfo=global.res.referrerInfo
        obj.pathinfo=global.res.pathinfo
        obj.privilegefunclist=global.res.privilegefunclist
        obj.wxfuncmap=global.res.wxfuncmap
        console.log(JSON.stringify(obj))
    }).catch(function(err) {
        console.log(err);
    })


    // filelist=readfile.readDirRecur(folder, filelist,function (fileList) {
    //     console.log(fileList)

            // })
}

//var filePath = "../navigation-miniapp/"
//var miniappname='newwxapkg/'
//filePath= filePath+miniappname
//console.log(filePath)
//parseMiniapp(filePath)

parseMiniapp(process.argv[2])

// fs.readdir(filePath,function (err,files){
//     for(var i =0;i<files.length;i++){
//         if(files[i].indexOf('.wxapkg')==-1){
//             parseMiniapp(filePath+files[i]+"/")
//         }
//     }
// })

//var res={
//    blepairing: [], // list of {path:'xxx', loc:{}}
//    blelevel: [], // list of {path: 'xxx', loc:{}, encryptedread: true,encryptedwrite:true}
//    navigationto: [],// list of {appid: 'xxx', path: 'xxx', loc: {}}
//    checkednavigation:[],//list of {checked:false,appid:null, path: 'xxx', loc:{}}
//    appsecret: [], //list of {secret: 'xxx', verified: false, truesecret: false, path: 'xxx', loc:{}}
//    wxfuncmap:[],//list of {name:'xxx', called: ['xxx'],'path:'xxx',loc:{}}
//    secretshare:{
//        sent:[], // list of {'path':'xxx',loc:{}}
//        checked:[],// list of {'path':'xxx',loc:{}}
//    },
//    scopes: {}, //list of {'xxx': {declared: false, used: false}}
//    transpile:false,
//    uglify: false
//}
//const code = fs.readFileSync('test.js', 'utf8');
//const ast = esprima.parse(code, options, function (node, metadata) {
//});
//var body=ast.body

