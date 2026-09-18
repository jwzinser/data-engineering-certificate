brew services start mongodb-community

mongosh
   use catalog;
   db.createUser({
     user: "root",
     pwd: "123",
     roles: [{ role: "root", db: "admin" }]
   })
   db.changeUserPassword("root", "123")

mongoimport -u root -p 123 --authenticationDatabase admin --db catalog --collection electronics --file catalog.json

mongosh

show dbs;

use catalog;

show collections;

db.electronics.createIndex({"type":1});

db.electronics.count();

db.electronics.find({"type":"laptop"}).count();

db.electronics.find({"type":"smart phone", "screen size":{"$eq":6}}).count();

db.electronics.aggregate([{"$match":{"type":"smart phone"}},
{"$group":{"_id":null,
"average screen size of smart phones": {"$avg":"$screen size"}}}
]);


mongoexport -u root -p 123 --authenticationDatabase admin --db catalog --collection electronics --out electronics.csv --type=csv --fields _id,type,model;