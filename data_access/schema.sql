-- ======================================================
-- Table : variete
-- Stocke les variétés de tomates issues du catalogue
-- Source : jardinsdetomates.fr
-- ======================================================

CREATE TABLE IF NOT EXISTS variete (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_source INTEGER NOT NULL UNIQUE,
    nom TEXT NOT NULL,
    couleur TEXT,
    forme TEXT,
    taille TEXT,
    precocite TEXT,
    descriptif TEXT,
    notes_gustatives TEXT,
    date_semence TEXT,
    image_url TEXT
);
