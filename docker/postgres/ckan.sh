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
EOSQL

# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
echo "local all  postgres    peer" >> /var/lib/postgresql/data/pg_hba.conf
echo "host  all  all    0.0.0.0/0  md5" >> /var/lib/postgresql/data/pg_hba.conf
echo "listen_addresses='*'" >> /var/lib/postgresql/data/postgresql.conf
