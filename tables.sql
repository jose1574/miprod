-- Table: my_prods.new_products

-- DROP TABLE my_prods.new_products;

CREATE TABLE my_prods.new_products
(
  id serial NOT NULL,
  code text NOT NULL,
  description text,
  old_code text,
  department text,
  mark text,
  unit text,
  unitary_cost numeric(12,2),
  maximum_price numeric(12,2),
  offer_price numeric(12,2),
  higher_price numeric(12,2),
  minimum_price numeric(12,2),
  CONSTRAINT new_products_pkey PRIMARY KEY (id ),
  CONSTRAINT new_products_code_key UNIQUE (code )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE my_prods.new_products
  OWNER TO postgres;
