-- Database: imam_test
-- using a command like: sudo -u postgres psql -f make_imam_test.sql
-- password will be '12345678'


DROP DATABASE IF EXISTS imam_test;
DROP ROLE IF EXISTS imamd_db_user;

CREATE ROLE imamd_db_user WITH LOGIN
  PASSWORD '12345678'
  SUPERUSER INHERIT CREATEDB NOCREATEROLE REPLICATION;

CREATE DATABASE imam_test
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       CONNECTION LIMIT = -1
       TEMPLATE template0;


