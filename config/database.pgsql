CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "citext";


-- Describing user IDs and their login credentials.
CREATE TABLE IF NOT EXISTS logins(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email CITEXT NOT NULL,
    pwhash TEXT NOT NULL  -- CRYPT('', GEN_SALT('md5'))
);


-- Describing different job roles that people can have.
CREATE TABLE IF NOT EXISTS roles(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES logins(id) ON DELETE CASCADE,
    name CITEXT NOT NULL,
    parent_id UUID REFERENCES roles(id) ON DELETE SET NULL,
    UNIQUE (owner_id, name)  -- No duplicate names
);


-- Describing the different people who can have their availability filled in.
CREATE TABLE IF NOT EXISTS people(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES logins(id) ON DELETE CASCADE,
    name CITEXT,
    email CITEXT,
    role_id UUID REFERENCES roles(id) ON DELETE SET NULL,
    maximum_working_hours SMALLINT NOT NULL DEFAULT 0,
    UNIQUE (owner_id, email)  -- No duplicate emails
);


-- Describing the start and end dates for a given availability that users can
-- fill in.
CREATE TABLE IF NOT EXISTS availability(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES logins(id) ON DELETE CASCADE,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL
);


-- A set of filled availability for a given user.
CREATE TABLE IF NOT EXISTS filled_availability(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    availability_id UUID NOT NULL REFERENCES availability(id) ON DELETE CASCADE,
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    availability TEXT[] DEFAULT '{}'
);


-- A table for storing the different rotas that people can work.
CREATE TABLE IF NOT EXISTS rotas(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES logins(id) ON DELETE CASCADE,
    availability_id UUID NOT NULL REFERENCES availability(id) ON DELETE CASCADE
);


-- A table for storing the different venues in which people can work.
CREATE TABLE IF NOT EXISTS venues(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES logins(id) ON DELETE CASCADE,
    rota_id UUID NOT NULL REFERENCES rotas(id) ON DELETE CASCADE,
    name CITEXT NOT NULL,
    index INTEGER NOT NULL  -- The order of the venues
);


-- A table for storing the different departments in which people can work.
CREATE TABLE IF NOT EXISTS venue_positions(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES logins(id) ON DELETE CASCADE,
    rota_id UUID NOT NULL REFERENCES rotas(id) ON DELETE CASCADE,
    venue_id UUID NOT NULL REFERENCES venues(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE SET NULL,  -- The role that can fill this position
    index INTEGER NOT NULL,  -- The order of the position in the venue
    start_time TEXT,  -- Nullable and text so the user can put in whatever they want
    end_time TEXT,  -- Nullable and text so the user can put in whatever they want
    notes TEXT  -- Nullable and text so the user can put in whatever they want
);
