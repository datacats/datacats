gosu postgres postgres --single <<-EOSQL
			CREATE USER ckan WITH PASSWORD 'password';
            CREATE DATABASE ckan OWNER ckan;
            CREATE USER ckan_datastore_readonly WITH PASSWORD 'password';
            CREATE USER ckan_datastore_readwrite WITH PASSWORD 'password';
            CREATE DATABASE ckan_datastore OWNER ckan;
EOSQL


# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
echo "local all  postgres    peer" >> /var/lib/postgresql/data/pg_hba.conf
echo "host  all  all    0.0.0.0/0  md5" >> /var/lib/postgresql/data/pg_hba.conf
echo "listen_addresses='*'" >> /var/lib/postgresql/data/postgresql.conf
