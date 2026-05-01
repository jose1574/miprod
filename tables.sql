-- Table: ferre.new_products

-- DROP TABLE ferre.new_products;

CREATE TABLE ferre.new_products
(
  id serial NOT NULL,
  code text NOT NULL,
  bar_code text,
  description text,
  department text,
  mark text,
  unit text,
  price numeric(12,2),
  CONSTRAINT new_products_pkey PRIMARY KEY (id ),
  CONSTRAINT new_products_code_key UNIQUE (code )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE ferre.new_products
  OWNER TO postgres;
