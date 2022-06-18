# Python Query Builder

This module exposes a class to build SQL queries.

```python
>>> from query import Query
>>> q = Query('tips').select('tip')
>>> print(q)
SELECT tip
FROM tips

```

The methods can be called in any order, and .build() renders a string full of
SQL.

```python
>>> q = Query('tips').where('total_bill > 10')
>>> q = q.select(['tip', 'total_bill', 'day AS weekday'])
>>> q.build()
'SELECT tip, total_bill, day AS weekday\nFROM tips\nWHERE total_bill > 10'
>>> print(q.build())
SELECT tip, total_bill, day AS weekday
FROM tips
WHERE total_bill > 10

```

Methods can be passed either a single string or a list of strings.

```python
>>> q = Query('tips').where('total_bill > 10')
>>> q = q.select(['tip', 'total_bill', 'day AS weekday'])
>>> print(q.build())
SELECT tip, total_bill, day AS weekday
FROM tips
WHERE total_bill > 10
>>> q = Query('tips').orderby(['tip', 'total_bill'])
>>> q = q.select(['smoker', 'total_bill']).where('tip < 4')
>>> print(q.build())
SELECT smoker, total_bill
FROM tips
WHERE tip < 4
ORDER BY tip, total_bill

```

If group by columns are not explicitly in the .select, they will be added.

```python
>>> q = Query('tips').groupby(['day', 'time'])
>>> q = q.select(['MAX(tip) AS tip_max', 'MIN(tip) AS tip_min'])
>>> print(q.build())
SELECT day, time, MAX(tip) AS tip_max, MIN(tip) AS tip_min
FROM tips
GROUP BY day, time

```

If no columns are selected, a SELECT * will be used.

```python
>>> q = Query('tips')
>>> print(q.build())
SELECT *
FROM tips

```

multiple .wheres are combined with an AND. There is also a .orwhere method.

```python
>>> q = Query('tips').where(['tip < 10', 'tip > 2'])
>>> print(q.build())
SELECT *
FROM tips
WHERE tip < 10 AND tip > 2
>>> q = Query('tips').where('tip < 10').orwhere('total_bill > 10')
>>> print(q.build())
SELECT *
FROM tips
WHERE tip < 10 OR total_bill > 10

```

CTEs are supported in the form of another query object passed to the .cte
method and given an alias.

```python
>>> q = Query('foo')
>>> print(q.build())
SELECT *
FROM foo
>>> q = Query('foo').cte(Query('bar'), 't')
>>> print(q.build())
WITH t AS (
  SELECT *
  FROM bar
)
SELECT *
FROM foo

```

```python
>>> q = Query('foo').cte(Query('bar'), 't1').cte(Query('baz'), 't2')
>>> print(q.build())
WITH t1 AS (
  SELECT *
  FROM bar
),
t2 AS (
  SELECT *
  FROM baz
)
SELECT *
FROM foo

```
