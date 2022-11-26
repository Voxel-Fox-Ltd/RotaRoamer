CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "citext";


CREATE TABLE IF NOT EXISTS logins(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email CITEXT NOT NULL,
    pwhash TEXT NOT NULL  -- CRYPT('', GEN_SALT('md5'))
);


CREATE TABLE IF NOT EXISTS roles(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES logins(id) ON DELETE CASCADE,
    name CITEXT NOT NULL,
    parent_id UUID REFERENCES roles(id) ON DELETE SET NULL,
    UNIQUE (owner_id, name)  -- No duplicate names
);


CREATE TABLE IF NOT EXISTS people(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES logins(id) ON DELETE CASCADE,
    name CITEXT,
    email CITEXT,
    role_id UUID REFERENCES roles(id) ON DELETE SET NULL,
    UNIQUE (owner_id, email)  -- No duplicate emails
);
