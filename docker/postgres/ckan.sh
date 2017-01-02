gosu postgres postgres --single <<-EOSQL
CREATE USER ckan WITH PASSWORD '$CKAN_PASSWORD';
CREATE DATABASE ckan OWNER ckan;
CREATE USER ckan_datastore_readonly WITH PASSWORD '$DATASTORE_RO_PASSWORD';
CREATE USER ckan_datastore_readwrite WITH PASSWORD '$DATASTORE_RW_PASSWORD';
CREATE DATABASE ckan_datastore OWNER ckan;
EOSQL

gosu postgres postgres --single ckan_datastore <<-EOSQL
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT CREATE ON SCHEMA public TO ckan;
GRANT USAGE ON SCHEMA public TO ckan;
GRANT CREATE ON SCHEMA public TO ckan_datastore_readwrite;
GRANT USAGE ON SCHEMA public TO ckan_datastore_readwrite;
REVOKE CONNECT ON DATABASE ckan FROM ckan_datastore_readonly;
GRANT CONNECT ON DATABASE ckan_datastore TO ckan_datastore_readonly;
GRANT USAGE ON SCHEMA public TO ckan_datastore_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ckan_datastore_readonly;

ALTER DEFAULT PRIVILEGES FOR USER ckan_datastore_readwrite IN SCHEMA public GRANT SELECT ON TABLES TO ckan_datastore_readonly;

CREATE OR REPLACE VIEW "_table_metadata" AS
    SELECT DISTINCT
        substr(md5(dependee.relname || COALESCE(dependent.relname, '')), 0, 17) AS "_id",
        dependee.relname AS name,
        dependee.oid AS oid,
        dependent.relname AS alias_of
        -- dependent.oid AS oid
    FROM
        pg_class AS dependee
        LEFT OUTER JOIN pg_rewrite AS r ON r.ev_class = dependee.oid
        LEFT OUTER JOIN pg_depend AS d ON d.objid = r.oid
        LEFT OUTER JOIN pg_class AS dependent ON d.refobjid = dependent.oid
    WHERE
        (dependee.oid != dependent.oid OR dependent.oid IS NULL) AND
        (dependee.relname IN (SELECT tablename FROM pg_catalog.pg_tables)
            OR dependee.relname IN (SELECT viewname FROM pg_catalog.pg_views)) AND
        dependee.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname='public')
    ORDER BY dependee.oid DESC;
ALTER VIEW "_table_metadata" OWNER TO "ckan_datastore_readwrite";
GRANT SELECT ON "_table_metadata" TO "ckan_datastore_readonly";
EOSQL

# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
echo "local all  postgres    peer" >> /var/lib/postgresql/data/pg_hba.conf
echo "host  all  all    0.0.0.0/0  md5" >> /var/lib/postgresql/data/pg_hba.conf
echo "listen_addresses='*'" >> /var/lib/postgresql/data/postgresql.conf
