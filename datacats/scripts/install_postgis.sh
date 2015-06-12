#!/bin/bash

su postgres -c "psql -d ckan -f /usr/share/postgresql/9.3/contrib/postgis-2.1/postgis.sql"
su postgres -c "psql -d ckan -f /usr/share/postgresql/9.3/contrib/postgis-2.1/spatial_ref_sys.sql"
su postgres -c "psql -d ckan -c 'ALTER VIEW geometry_columns OWNER TO ckan;'"
su postgres -c "psql -d ckan -c 'ALTER TABLE spatial_ref_sys OWNER TO ckan;'"
