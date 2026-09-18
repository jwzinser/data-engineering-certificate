mongoimport --db entertainment --collection movies --file movies.json 

use entertainment
db.movies.countDocuments()
db.movies.findOne()

db.movies.aggregate([
  {
    $group: {
      _id: "$year",
      count: { $sum: 1 }
    }
  },
  {
    $sort: { count: -1 }
  },
  {
    $limit: 1
  }
])

// 2016 - 73

db.movies.countDocuments({ year: { $gt: 1999 } })
//99

db.movies.aggregate([
  { $match: { year: 2007 } },
  { $group: { _id: "$year", averageVotes: { $avg: "$Votes" } } }
])

mongoexport --db=entertainment --collection=movies --type=csv --fields=_id,title,year,rating,Director --out=partial_data.csv --username=<user> --password=<pass> --authenticationDatabase=admin




CREATE KEYSPACE entertainment
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
CREATE KEYSPACE entertainment
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
AND durable_writes = true;
USE entertainment;

CREATE TABLE movies (
    "_id" text PRIMARY KEY,
    title text,
    year text,
    rating text,
    director text
);

COPY entertainment.movies ("_id", title, year, rating, director)
FROM 'partial_data.csv'
WITH DELIMITER=',' AND HEADER=TRUE;

SELECT COUNT(*) FROM movies;

SELECT COUNT(*) FROM movies WHERE rating = 'G';