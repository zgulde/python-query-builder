'''
This module exposes a class to build SQL queries.

>>> q = Query('tips').select('tip')
>>> print(q.build())
SELECT tip
FROM tips

The methods can be called in any order, and .build() renders a string full of
SQL.

>>> q = Query('tips').where('total_bill > 10')
>>> q = q.select(['tip', 'total_bill', 'day AS weekday'])
>>> print(q.build())
SELECT tip, total_bill, day AS weekday
FROM tips
WHERE total_bill > 10

Methods can be passed either a single string or a list of strings.

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

If group by columns are not explicitly in the .select, they will be added.

>>> q = Query('tips').groupby(['day', 'time'])
>>> q = q.select(['MAX(tip) AS tip_max', 'MIN(tip) AS tip_min'])
>>> print(q.build())
SELECT day, time, MAX(tip) AS tip_max, MIN(tip) AS tip_min
FROM tips
GROUP BY day, time

If no columns are selected, a SELECT * will be used.

>>> q = Query('tips')
>>> print(q.build())
SELECT *
FROM tips

multiple .wheres are combined with an AND. There is also a .orwhere method.

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

CTEs are supported in the form of another query object passed to the .cte
method and given an alias.

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
'''
# TODO: nested CTE query objects?
import textwrap as tw

class Query():
    def __init__(self, table, add_groupbys_to_select=True):
        self._table = table
        self._selects = []
        self._wheres = []
        self._orwheres = []
        self._groupbys = []
        self._orderbys = []
        self._ctes = []
        self._limit = None
        self._offset = None
        self._add_groupbys_to_select = add_groupbys_to_select

    def select(self, column):
        if type(column) is list:
            self._selects.extend(column)
        else:
            self._selects.append(column)
        return self
    def where(self, cond):
        if type(cond) is list:
            self._wheres.extend(cond)
        else:
            self._wheres.append(cond)
        return self
    def orwhere(self, cond):
        if type(cond) is list:
            self._orwheres.extend(cond)
        else:
            self._orwheres.append(cond)
        return self
    def groupby(self, column):
        if type(column) is list:
            self._groupbys.extend(column)
        else:
            self._groupbys.append(column)
        return self
    def orderby(self, column):
        if type(column) is list:
            self._orderbys.extend(column)
        else:
            self._orderbys.append(column)
        return self
    def limit(self, l):
        self._limit = l
        return self
    def offset(self, o):
        self._offset = o
        return self
    def cte(self, query, alias):
        self._ctes.append([query, alias])
        return self

    def _build_ctes(self):
        s = 'WITH '
        s += ',\n'.join([
            alias + ' AS (\n' + tw.indent(query.build(), '  ') + '\n)'
            for query, alias in self._ctes
        ])
        s += '\n'
        return s

    def __str__(self):
        return self.build()
    def _repr_html_(self):
        return f'<pre>{self.build()}</pre>'

    def build(self):
        if self._groupbys and self._add_groupbys_to_select:
            idx = 0
            for col in self._groupbys:
                if col not in self._selects:
                    self._selects.insert(idx, col)
                    idx += 1
        query = ''
        if self._ctes:
            query += self._build_ctes()
        query += 'SELECT ' + ', '.join(self._selects or ['*']) + '\n'
        query += 'FROM ' + self._table + '\n'
        if self._wheres:
            first_cond, rest_conds = self._wheres[0], self._wheres[1:]
            query += 'WHERE ' + first_cond
            if rest_conds:
                query += ' AND ' + ' AND '.join(rest_conds)
            if self._orwheres:
                first_cond, rest_conds = self._orwheres[0], self._orwheres[1:]
                query += ' OR ' + first_cond
                if rest_conds:
                    query += ' OR '.join(rest_conds)
            query += '\n'
        if self._groupbys:
            query += 'GROUP BY ' + ', '.join(self._groupbys) + '\n'
        if self._orderbys:
            query += 'ORDER BY ' + ', '.join(self._orderbys) + '\n'
        if self._limit:
            query += 'LIMIT ' + str(self._limit)
        if self._offset:
            query += 'OFFSET ' + str(self._offset)
        return query.strip()

