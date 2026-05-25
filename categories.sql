-- ! Конфигурация таблицы
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS categories;
DROP TYPE IF EXISTS transaction_type;

CREATE TYPE transaction_type AS ENUM ('Доход', 'Расход');
CREATE TABLE categories
(
	category_id SERIAL PRIMARY KEY NOT NULL,
	name VARCHAR(100) NOT NULL,
	type transaction_type NOT NULL
);

CREATE TABLE transactions
(
	id SERIAL PRIMARY KEY NOT NULL,
	category_id INT,
	amount NUMERIC NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT fk_categories
		FOREIGN KEY(category_id)
			REFERENCES categories(category_id)
);