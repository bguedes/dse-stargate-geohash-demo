

//  CQL command file to; make keyspace, make table and indexes, load data
//
//  All of these are used by a given demo Web program/pod, to show geo-spatial
//  and GraphQL


// DROP KEYSPACE IF EXISTS my_keyspace;

CREATE KEYSPACE IF NOT EXISTS my_keyspace
   WITH replication = {'class':'SimpleStrategy', 'replication_factor':2};

USE my_keyspace;

CREATE TABLE IF NOT EXISTS my_mapdata
   (
   md_pk             TEXT PRIMARY KEY,
   md_lat            TEXT,
   md_lng            TEXT,
   geo_hash10        TEXT,
   md_name           TEXT,
   md_address        TEXT,
   md_city           TEXT,
   md_province       TEXT,
   md_postcode       TEXT,
   md_phone          TEXT,
   md_category       TEXT,
   md_subcategory    TEXT,
      //
   geo_hash5         TEXT,
   geo_hash6         TEXT,
   geo_hash7         TEXT,
   name3             TEXT,
   name5             TEXT,
   name7             TEXT
   );


 CREATE CUSTOM INDEX IF NOT EXISTS geo_hash5_idx ON my_mapdata(geo_hash5)
 USING 'StorageAttachedIndex'
 WITH OPTIONS = { 'case_sensitive': true, 'normalize': false };

CREATE CUSTOM INDEX IF NOT EXISTS geo_hash6_idx ON my_mapdata(geo_hash6)
USING 'StorageAttachedIndex'
WITH OPTIONS = { 'case_sensitive': true, 'normalize': false };

CREATE CUSTOM INDEX IF NOT EXISTS geo_hash7_idx ON my_mapdata(geo_hash7)
USING 'StorageAttachedIndex'
WITH OPTIONS = { 'case_sensitive': true, 'normalize': false };

CREATE CUSTOM INDEX IF NOT EXISTS name3_idx ON my_mapdata(name3)
USING 'StorageAttachedIndex'
WITH OPTIONS = { 'case_sensitive': false, 'normalize': true };

CREATE CUSTOM INDEX IF NOT EXISTS name5_idx ON my_mapdata(name5)
USING 'StorageAttachedIndex'
WITH OPTIONS = { 'case_sensitive': false, 'normalize': true };

CREATE CUSTOM INDEX IF NOT EXISTS name7_idx ON my_mapdata(name7)
USING 'StorageAttachedIndex'
WITH OPTIONS = { 'case_sensitive': false, 'normalize': true };

COPY my_mapdata
   (
   md_pk             ,
   md_lat            ,
   md_lng            ,
   geo_hash10        ,
   md_name           ,
   md_address        ,
   md_city           ,
   md_province       ,
   md_postcode       ,
   md_phone          ,
   md_category       ,
   md_subcategory    ,
   geo_hash5         ,
   geo_hash6         ,
   geo_hash7         ,
   name3             ,
   name5             ,
   name7
   )
   FROM '20_File_10_as_CSV.csv'
   WITH HEADER = TRUE
   AND DELIMITER = '|'
   AND MAXBATCHSIZE = 20;
