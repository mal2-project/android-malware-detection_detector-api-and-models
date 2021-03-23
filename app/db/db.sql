CREATE DATABASE bincache;

\c bincache

CREATE TABLE "cache" (
    filename varchar(500),              -- file name of the binary 
    path_on_disk varchar(1000),          -- the file name we gave it on our disk
    md5 varchar(33), 
    sha1 varchar(42), 
    sha256 varchar(65) primary key, 
    contains_malware float,                
    contains_trackers float,                
    contains_adware float,                
    first_seen timestamp with time zone,
    analyzed_at timestamp with time zone
);


CREATE index idx_cache_sha256 on "cache"(sha256);
CREATE index idx_cache_sha1 on "cache"(sha1);
CREATE index idx_cache_md5 on "cache"(md5);
CREATE index idx_cache_filename on "cache"(filename);

