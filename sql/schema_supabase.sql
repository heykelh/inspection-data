-- INSPECTION DATA - Schema Supabase (Postgres). Pour le chargement en P1.
create table if not exists clients (
    client_id        text primary key,
    nom              text,
    prenom           text,
    date_naissance   date,
    email            text,
    adresse          text,
    consentement_rgpd boolean,
    date_collecte    date,
    date_maj         timestamp
);

create table if not exists prets (
    pret_id          text primary key,
    client_id        text references clients(client_id),
    montant          numeric,
    taux             numeric,
    date_octroi      date,
    statut           text,
    notation_risque  text
);

-- Registre des constats produit par le moteur d'inspection
create table if not exists constats (
    id               bigint generated always as identity primary key,
    controle_id      text not null,
    pilier           text not null,
    libelle          text not null,
    severite         text not null,
    statut           text not null,
    criticite        text not null,
    exceptions       integer not null,
    population       integer not null,
    taux             numeric not null,
    recommandation   text,
    date_mission     date not null default current_date
);

create index if not exists idx_prets_client on prets(client_id);
create index if not exists idx_constats_controle on constats(controle_id);
