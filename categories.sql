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

-- INSERT INTO categories(name, type)
-- VALUES
-- 	('Продукты', 'Расход'),
-- 	('Зарплата', 'Доход'),
-- 	('Телефон', 'Расход'),
-- 	('Подарок', 'Доход'),
-- 	('Долг Маша', 'Доход')
-- RETURNING *;
-- INSERT INTO transactions(category_id, amount)
-- VALUES
-- 	(1, 500),
-- 	(2, 35000),
-- 	(3, 27499.99),
-- 	(4, 1000),
-- 	(5, 1500)
-- RETURNING *;

-- DELETE FROM transactions WHERE id = 5;

-- SELECT * FROM categories INNER JOIN transactions USING(category_id)

-- SELECT * FROM transactions ORDER BY created_at DESC

-- SELECT ((SELECT SUM(amount) AS sum FROM transactions WHERE category_id IN (SELECT category_id FROM categories WHERE type = 'Доход')) - (SELECT SUM(amount) AS sum FROM transactions WHERE category_id IN (SELECT category_id FROM categories WHERE type = 'Расход')))
