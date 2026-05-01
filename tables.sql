-- Table: ferre.new_products

-- DROP TABLE ferre.new_products;

CREATE TABLE ferre.new_products
(
  id serial NOT NULL,
  code text NOT NULL,
  description text,
  mark text,
  CONSTRAINT new_products_pkey PRIMARY KEY (id ),
  CONSTRAINT new_products_code_key UNIQUE (code )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE ferre.new_products
  OWNER TO postgres;
