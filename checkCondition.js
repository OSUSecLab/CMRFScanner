// function traverseFunction(parent,filepath,node,res) {
// console.log("???",node)
// }
function traverseFunction(parent,filepath,node,res){
    // vardeclaration -> vardeclarator ->
    // if(node.type==='ConditionalExpression'){
    //     console.log(node)
    // }

    if(node==null){
        return
    }
    if(node==='test.js'){
        console.log(node,parent)
    }

    node.parent=parent
    node.declare={}
    node.called={}
    node.extra= {}
    switch (node.type) {
        case 'VariableDeclaration':
            let declarations=node.declarations
            for (var j=0;j<declarations.length;j++){
                traverseFunction(node,filepath,declarations[j],res)
            }

            break
        case 'VariableDeclarator':
            // if is interested variable
            let init=node.init
            if(init===null){
                return
            }
            traverseFunction(node,filepath,init,res)
            break
        case 'CallExpression':

            traverseFunction(node,filepath,node.callee,res)
            for(var j=0;j<node.arguments.length;j++){
                traverseFunction(node,filepath,node.arguments[j],res)
            }
            if(node.callee.property){
//                if(node.callee.property.name==='set'){
//                    console.log("??",node.callee.object)
//                    console.log("??",node.callee.property)
//                }
                var prefix=""
                var startnode=node.callee
                while(startnode.object){
                    // console.log(startnode.object)
                    if(startnode.property)prefix='.'+startnode.property.name+prefix
                    startnode=startnode.object
                }
                prefix=startnode.name+prefix
                res.func.push(prefix)
            }

            break
        case 'FunctionExpression':
            traverseFunction(node,filepath,node.body,res)
            break
        case 'FunctionDeclaration':
            traverseFunction(node,filepath,node.body,res)
            break
        case 'BlockStatement':

            let blockbody=node.body
            for (var j=0;j<blockbody.length;j++){
                traverseFunction(node,filepath,blockbody[j],res)
            }
            break
        case 'ReturnStatement':

            if (node.argument===null){
                return
            }
            traverseFunction(node,filepath,node.argument,res)
            break
        case 'SequenceExpression': // aaa(), bbb(), ccc();
            let expressions=node.expressions
            for(var j=0;j<expressions.length;j++){
                traverseFunction(node,filepath,expressions[j],res)
            }
            break
        case 'ArrayExpression':
            let elements=node.elements
            for(var j=0;j<elements.length;j++){
                traverseFunction(node,filepath,elements[j],res)
            }
            break
        case 'ObjectExpression':

            for(var j=0;j<node.properties.length;j++){
                traverseFunction(node,filepath,node.properties[j],res)
            }
            break
        case 'Property':
            if(node.value==null){
                return
            }
            traverseFunction(node,filepath,node.value,res)

            break
        case 'ExpressionStatement':
            traverseFunction(node,filepath,node.expression,res)


            break
        case 'MemberExpression':
            traverseFunction(node,filepath,node.object,res)

            if(node.property.value&&typeof node.property==='string'){
                if(node.property.value.includes('session')&&node.property.value.includes('key'))res.susp_prop.push(node.property.value)
            }
            
            break
        case 'IfStatement':
            traverseFunction(node,filepath,node.test,res)
            traverseFunction(node,filepath,node.consequent,res)
            if (node.alternate!=null){
                traverseFunction(node,filepath,node.alternate,res)
            }
            break
        case 'UnaryExpression':
            traverseFunction(node,filepath,node.argument,res)
            break
        case 'ConditionalExpression':
            traverseFunction(node,filepath,node.test,res)
            traverseFunction(node,filepath,node.consequent,res)
            traverseFunction(node,filepath,node.alternate,res)
            break
        case 'AssignmentExpression':
            traverseFunction(node,filepath,node.left,res)
            traverseFunction(node,filepath,node.right,res)

            break
        case 'TryStatement':
            traverseFunction(node,filepath,node.block,res)
            if (node.handler!=null){
                traverseFunction(node,filepath,node.handler,res)
            }
            if(node.finalizer!=null){
                traverseFunction(node,filepath,node.finalizer,res)
            }
            break
        case 'Identifier':
            break
        case 'Literal':
            if(typeof node.value==='string'&&node.value.includes('/'))res.susp_path.push(node.value)
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
            traverseFunction(node,filepath,node.discriminant,res)
            for(var j=0;j<node.cases.length;j++){
                traverseFunction(node,filepath,node.cases[j],res)
            }
            break
        case 'WhileStatement':
            traverseFunction(node,filepath,node.test,res)
            traverseFunction(node,filepath,node.body,res)
            break
        case 'DoWhileStatement':
            traverseFunction(node,filepath,node.body,res)
            traverseFunction(node,filepath,node.test,res)
            break
        case "SwitchCase":
            if(node.test!=null){
                traverseFunction(node,filepath,node.test,res)
            }
            for(var j=0;j<node.consequent.length;j++){
                traverseFunction(node,filepath,node.consequent[j],res)
            }
            break
        case 'NewExpression':
            traverseFunction(node,filepath,node.callee,res)
            for(var j=0;j<node.arguments.length;j++){
                traverseFunction(node,filepath,node.arguments[j],res)
            }
            break
        case 'UpdateExpression':
            traverseFunction(node,filepath,node.argument,res)
            break
        case 'ThrowStatement':
            traverseFunction(node,filepath,node.argument,res)
            break
        case 'ForInStatement':
            traverseFunction(node,filepath,node.left,res)
            traverseFunction(node,filepath,node.right,res)
            break
        case 'CatchClause':
            traverseFunction(node,filepath,node.param,res)
            traverseFunction(node,filepath,node.body,res)
            break
        case 'ForStatement':
            if(node.init!=null){
                traverseFunction(node,filepath,node.init,res)
            }
            if(node.test!=null){
                traverseFunction(node,filepath,node.test,res)
            }
            if(node.update!=null){
                traverseFunction(node,filepath,node.update,res)
            }
            traverseFunction(node,filepath,node.body,res)
            break
        case 'BinaryExpression':
            traverseFunction(node,filepath,node.left,res)
            traverseFunction(node,filepath,node.right,res)
            break
        case 'LogicalExpression':
            //checkCondition();
            traverseFunction(node,filepath,node.left,res)
            traverseFunction(node,filepath,node.right,res)
            break
        default:
            break
    }
    return res

    // else if (node.type=="")
}
function traverseCondition(parent,filepath,node,res){
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
    switch (node.type) {
        case 'VariableDeclaration':
            let declarations=node.declarations
            for (var j=0;j<declarations.length;j++){
                traverseCondition(node,filepath,declarations[j],res)
            }

            break
        case 'VariableDeclarator':
            // if is interested variable
            let init=node.init
            if(init===null){
                return
            }
            traverseCondition(node,filepath,init,res)
            break
        case 'CallExpression':
            traverseCondition(node,filepath,node.callee,res)
            for(var j=0;j<node.arguments.length;j++){
                traverseCondition(node,filepath,node.arguments[j],res)
            }

            // if(node.callee.type==='MemberExpression'){
            //
            //     res.push(node.callee.property.name)
            //
            // }
            break
        case 'FunctionExpression':
            traverseCondition(node,filepath,node.body,res)
            break
        case 'FunctionDeclaration':
            traverseCondition(node,filepath,node.body,res)
            break
        case 'BlockStatement':

            let blockbody=node.body
            for (var j=0;j<blockbody.length;j++){
                traverseCondition(node,filepath,blockbody[j],res)
            }
            break
        case 'ReturnStatement':
            if (node.argument===null){
                return
            }

            traverseCondition(node,filepath,node.argument,res)
            break
        case 'SequenceExpression': // aaa(), bbb(), ccc();
            let expressions=node.expressions
            for(var j=0;j<expressions.length;j++){
                traverseCondition(node,filepath,expressions[j],res)
            }
            break
        case 'ArrayExpression':
            let elements=node.elements
            for(var j=0;j<elements.length;j++){
                traverseCondition(node,filepath,elements[j],res)
            }
            break
        case 'ObjectExpression':

            for(var j=0;j<node.properties.length;j++){
                traverseCondition(node,filepath,node.properties[j],res)
            }
            break
        case 'Property':
            if(node.value==null){
                return
            }
            traverseCondition(node,filepath,node.value,res)

            break
        case 'ExpressionStatement':
            traverseCondition(node,filepath,node.expression,res)


            break
        case 'MemberExpression':
            if(node.property.name==='referrerInfo'){
                res.referrerInfo=true
            }else if(node.property.name==='appId'){
                res.appId=true
            }
            traverseCondition(node,filepath,node.object,res)
            break
        case 'IfStatement':
            traverseCondition(node,filepath,node.test,res)
            traverseCondition(node,filepath,node.consequent,res)
            if (node.alternate!=null){
                traverseCondition(node,filepath,node.alternate,res)
            }
            break
        case 'UnaryExpression':
            traverseCondition(node,filepath,node.argument,res)
            break
        case 'ConditionalExpression':
            traverseCondition(node,filepath,node.test,res)
            traverseCondition(node,filepath,node.consequent,res)
            traverseCondition(node,filepath,node.alternate,res)
            break
        case 'AssignmentExpression':
            traverseCondition(node,filepath,node.left,res)
            traverseCondition(node,filepath,node.right,res)

            break
        case 'TryStatement':
            traverseCondition(node,filepath,node.block,res)
            if (node.handler!=null){
                traverseCondition(node,filepath,node.handler,res)
            }
            if(node.finalizer!=null){
                traverseCondition(node,filepath,node.finalizer,res)
            }
            break
        case 'Identifier':
            break
        case 'Literal':

            if(node.value&&node.value.toString().match(/^([a-zA-Z0-9]{16})/g)!=null){

                res.literal.push(node.value)
            }
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
            traverseCondition(node,filepath,node.discriminant,res)
            for(var j=0;j<node.cases.length;j++){
                traverseCondition(node,filepath,node.cases[j],res)
            }
            break
        case 'WhileStatement':
            traverseCondition(node,filepath,node.test,res)
            traverseCondition(node,filepath,node.body,res)
            break
        case 'DoWhileStatement':
            traverseCondition(node,filepath,node.body,res)
            traverseCondition(node,filepath,node.test,res)
            break
        case "SwitchCase":
            if(node.test!=null){
                traverseCondition(node,filepath,node.test,res)
            }
            for(var j=0;j<node.consequent.length;j++){
                traverseCondition(node,filepath,node.consequent[j],res)
            }
            break
        case 'NewExpression':
            traverseCondition(node,filepath,node.callee,res)
            for(var j=0;j<node.arguments.length;j++){
                traverseCondition(node,filepath,node.arguments[j],res)
            }
            break
        case 'UpdateExpression':
            traverseCondition(node,filepath,node.argument,res)
            break
        case 'ThrowStatement':
            traverseCondition(node,filepath,node.argument,res)
            break
        case 'ForInStatement':
            traverseCondition(node,filepath,node.left,res)
            traverseCondition(node,filepath,node.right,res)
            break
        case 'CatchClause':
            traverseCondition(node,filepath,node.param,res)
            traverseCondition(node,filepath,node.body,res)
            break
        case 'ForStatement':
            if(node.init!=null){
                traverseCondition(node,filepath,node.init,res)
            }
            if(node.test!=null){
                traverseCondition(node,filepath,node.test,res)
            }
            if(node.update!=null){
                traverseCondition(node,filepath,node.update,res)
            }
            traverseCondition(node,filepath,node.body,res)
            break
        case 'BinaryExpression':
            if(node.operator==='=='||node.operator==='!='||node.operator==='==='||node.operator==='!=='||node.operator==='in') {
                var tempres = {appId: false, referrerInfo:false, literal:[],checked: false}
                traverseCondition(node,filepath,node.left,tempres)
                traverseCondition(node,filepath,node.right,tempres)

                if(tempres.referrerInfo){
                    res.referrerInfo=true
                }
                if(tempres.appId){
                    res.checked=true
                    res.appId=true
                }
                if(tempres.literal.length>0){

                    res.literal.push(tempres.literal)
                }
            }
            else{
                traverseCondition(node,filepath,node.left,res)
                traverseCondition(node,filepath,node.right,res)
            }
            break
        case 'LogicalExpression':
            //checkCondition();

            traverseCondition(node,filepath,node.left,res)
            traverseCondition(node,filepath,node.right,res)
            break
        default:
            break
    }
    return res

    // else if (node.type=="")
}

module.exports={
    traverseCondition: traverseCondition,
    traverseFunction:traverseFunction
}
