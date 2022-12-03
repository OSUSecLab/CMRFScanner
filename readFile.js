var fs = require('fs');
var readdir = promisify(fs.readdir);
var stat = promisify(fs.stat);
var readFile = promisify(fs.readFile);
var path=require('path')
// 简单实现一个promisify
function promisify(fn) {
    return function() {
        var args = arguments;
        return new Promise(function(resolve, reject) {
            [].push.call(args, function(err, result) {
                if(err) {
                    console.log(err)
                    reject(err);
                }else {
                    resolve(result);
                }
            });
            fn.apply(null, args);
        });
    }
}

function readDirRecur(file, callback) {
    return readdir(file).then((files) => {
        files = files.map((item) => {
            var fullPath = file + '/' + item;

            return stat(fullPath).then((stats) => {
                if (stats.isDirectory()) {
                    return readDirRecur(fullPath, callback);
                } else {
                    /*not use ignore files*/
                    if(item[0] == '.'){
                        //console.log(item + ' is a hide file.');
                    } else {
                        callback && callback(fullPath)
                    }
                }
            })
        });
        return Promise.all(files);
    });
}

var fileList = []


var filePath = path.resolve('static/sx')


    module.exports = {
    readDirRecur: readDirRecur
};
