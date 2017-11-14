var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var request = require("request-promise");
var mongoose = require('mongoose');
mongoose.connect('mongodb://localhost:27017/west');
var Schema = mongoose.Schema;
var PythonShell = require('python-shell');


//var index = require('./routes/index');
//var users = require('./routes/users');
var multer = require('multer');
var upload = multer();

var app = express();
app.use(bodyParser.urlencoded({ extended: false}));
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

//one({"type": "hrlyaverage", "value": numpy.average(hourValues), "timeStamp" : hourLimit})

var avgS = new Schema({
    type: String,
    value: Number,
    timeStamp: Number,
    id: Schema.Types.Mixed
});
var values = new Schema({
    type: String,
    value: Number,
    timeStamp: Number,
    id: Schema.Types.Mixed
});
var idList = new Schema({
    id: Schema.Types.Mixed
});




// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');




// error handler
app.get("/", function(req,res){
	res.sendfile('public/index.html');
});

app.post("/valuesInRange", upload.array(), function(req,res){
	var ranges = datesToUnix(req.body.range);
	var array = [];
	var model = mongoose.model('average1', avgS, 'averages');
		model.find({ "timeStamp": { "$gt": ranges[0] , "$lt": ranges[1]}, "sensorId" : req.body.id}).exec(function(err,avgs){
			avgs.forEach(function(thing){
				array.push(thing);
			});
			res.send(array);
		});
});

app.get("/averages", function(req,res){
	var array = [];
	var model = mongoose.model('average2', avgS, 'averages');
		model.find().exec(function(err,avgs){
			avgs.forEach(function(thing){
				array.push(thing);
			});
			res.send(array);
		});
});
app.get("/idList", function(req,res){
	var array = [];
	var model = mongoose.model('average3', idList, 'averages');
		model.find({type: "idList"}).exec(function(err,ids){
			res.send(ids[0]);
		});
});
app.get("/allValues", function(req,res){
	var array = [];
	var model = mongoose.model('id', values, 'ids');
		model.find().exec(function(err,values){
			values.forEach(function(thing){
				array.push(thing);
			});
			res.send(array);
		});
});


app.get("/doPython", function(req,res){
	PythonShell.run('py/hdwStats.py', function (err) {
  		if (err) throw err;
  		res.send('avgs Calculated');
	});
});
setInterval(function(){
	PythonShell.run('py/hdwStats.py', function (err) {
  		if (err) throw err;
  		console.log('avgs Calculated');
	});

},600000);

var datesToUnix = function(date){
	var dates = date.split("-");
	dates[0] = dates[0].replace(/^\s\s*/, '').replace(/\s\s*$/, '');
	dates[1] = dates[1].replace(/^\s\s*/, '').replace(/\s\s*$/, '');
	return [Math.floor(Date.parse(dates[0])/1000), Math.floor(Date.parse(dates[1])/1000)];
};




module.exports = app;
app.listen(3000, function () {
  console.log('Example app listening on port 3000!')
});
