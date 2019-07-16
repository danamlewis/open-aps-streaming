\set ingestor_password `echo "$POSTGRES_INGESTOR_PASSWORD"`
\set admin_viewer_password `echo "$POSTGRES_ADMIN_VIEWER_PASSWORD"`
\set viewer_password `echo "$POSTGRES_VIEWER_PASSWORD"`
\set ext_openaps_app_password `echo "$POSTGRES_EXT_OPENAPS_APP_PASSWORD"`

CREATE USER ingestor;
ALTER USER ingestor WITH ENCRYPTED PASSWORD :'ingestor_password';
GRANT USAGE ON SCHEMA openaps TO ingestor;

CREATE USER admin_viewer;
ALTER USER admin_viewer WITH ENCRYPTED PASSWORD :'admin_viewer_password';
GRANT USAGE ON SCHEMA openaps TO admin_viewer;
GRANT SELECT ON ALL TABLES IN SCHEMA openaps TO admin_viewer;

CREATE USER viewer;
ALTER USER viewer WITH ENCRYPTED PASSWORD :'viewer_password';
GRANT USAGE ON SCHEMA openaps TO viewer;

CREATE USER ext_openaps_app;
ALTER USER ext_openaps_app WITH ENCRYPTED PASSWORD :'ext_openaps_app_password';
GRANT USAGE ON SCHEMA openaps TO ext_openaps_app;
GRANT SELECT, UPDATE, INSERT ON ALL TABLES IN SCHEMA openaps TO ext_openaps_app;


