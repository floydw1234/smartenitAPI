var http = require('http');
var requirep = require('request-promise');
var request = require('request');
var JSON = require('JSON');
var mongoose = require('mongoose');
mongoose.connect('mongodb://localhost:27017/west');



            var Schema = mongoose.Schema;

            var idSchema = new Schema({
                sensorId:Number,
                value: Number,
                timePolled: Number,
                last_seen: Number
            });


            var id = mongoose.model('id', idSchema);
            //a8e61c58f8
            var options = {
                "method": "GET",
                "hostname": "192.168.10.50",
                "port": "50334",
                "path": "/devices",
                "headers": {
                    "cache-control": "no-cache",
                }
            };

            console.log("script is starting");
setInterval(function(){
//console.log("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx");

            var req = http.request(options, function(res) {
                        res.on('error', function(err) {
                            console.log(err)
                        });
                        var chunks = [];
                        console.log("connection, successful");

                        res.on("data", function(chunk) {
                            chunks.push(chunk);
                            //console.log(chunk.toString());
                        });

                        res.on("end", function() {
                                var body = Buffer.concat(chunks);
                                jsonParsed = JSON.parse(body.toString());
                                //console.log(jsonParsed);
                                //console.log("\n");
                                //console.log();
                                var deviceIdList = [];
                                var deviceIdListMongoose = [];
                                for (i = 1; i < jsonParsed.devices.length; i++) {
                                    var currentdate = new Date();

                                    var Divisor = -1;
                                    var Multiplier = -1;
                                    var InstPower = -1;
					//console.log(jsonParsed.devices[i].id);
                                    jsonParsed.devices[i].components.forEach(function(cap) {
                                        cap.capabilities.forEach(function(thing) {
                                            if (thing.SimpleMeter != undefined) {
                                                thing.SimpleMeter.forEach(function(thing3) {
                                                    if (thing3.Divisor != undefined) {
                                                        Divisor = thing3.Divisor.value;
                                                    }
                                                    if (thing3.Multiplier != undefined) {
                                                        Multiplier = thing3.Multiplier.value;
                                                    }
                                                    if (thing3.InstantaneousPower != undefined) {


								InstPower = thing3.InstantaneousPower.value;




                                                    }
                                                });
                                            }

                                        });
                                    });
                                    deviceIdList[i] = [jsonParsed.devices[i].id, jsonParsed.devices[i].last_seen];
                                    if (InstPower != -1) {
					console.log(InstPower);
					//console.log(jsonParsed.devices[i].id + "\n ---------------------------------");
                                        InstPowerArray = String(InstPower).split(" ");
					//console.log(InstPowerArray);
                                        deviceIdListMongoose[i] = new id({
                                            sensorId: jsonParsed.devices[i].id,
                                            value: Multiplier / Divisor * parseFloat(InstPowerArray[0]),
                                            timePolled: parseInt(Math.floor(Date.now() / 1000)),
                                            last_seen: jsonParsed.devices[i].last_seen
                                        });

                                        deviceIdListMongoose[i].save(function(err) {
                                            if (err) throw err;
                                            console.log("save successful")
                                        });
                                    } else {
                                       //console.log("device with id: " + jsonParsed.devices[i].id + " did not have Instantaneos Power Property ");
                                        }
                                    }


                                });
                        }).on('error', function(err) {
                        console.error(err)
                    });

                    req.end();

 },
3000);
//setTimeout(function(){process.exit();},3000);
