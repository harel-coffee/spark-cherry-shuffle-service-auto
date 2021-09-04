#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
A collections of builtin functions
"""
import sys
import functools
import warnings

from pyspark import since, SparkContext
from pyspark.rdd import PythonEvalType
from pyspark.sql.column import Column, _to_java_column, _to_seq, _create_column_from_literal
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import StringType, DataType
# Keep UserDefinedFunction import for backwards compatible import; moved in SPARK-22409
from pyspark.sql.udf import UserDefinedFunction, _create_udf  # noqa: F401
from pyspark.sql.udf import _create_udf
# Keep pandas_udf and PandasUDFType import for backwards compatible import; moved in SPARK-28264
from pyspark.sql.pandas.functions import pandas_udf, PandasUDFType  # noqa: F401
from pyspark.sql.utils import to_str

# Note to developers: all of PySpark functions here take string as column names whenever possible.
# Namely, if columns are referred as arguments, they can be always both Column or string,
# even though there might be few exceptions for legacy or inevitable reasons.
# If you are fixing other language APIs together, also please note that Scala side is not the case
# since it requires to make every single overridden definition.


def _get_get_jvm_function(name, sc):
    """
    Retrieves JVM function identified by name from
    Java gateway associated with sc.
    """
    return getattr(sc._jvm.functions, name)


def _invoke_function(name, *args):
    """
    Invokes JVM function identified by name with args
    and wraps the result with :class:`Column`.
    """
    jf = _get_get_jvm_function(name, SparkContext._active_spark_context)
    return Column(jf(*args))


def _invoke_function_over_column(name, col):
    """
    Invokes unary JVM function identified by name
    and wraps the result with :class:`Column`.
    """
    return _invoke_function(name, _to_java_column(col))


def _invoke_binary_math_function(name, col1, col2):
    """
    Invokes binary JVM math function identified by name
    and wraps the result with :class:`Column`.
    """
    return _invoke_function(
        name,
        # For legacy reasons, the arguments here can be implicitly converted into floats,
        # if they are not columns or strings.
        _to_java_column(col1) if isinstance(col1, (str, Column)) else float(col1),
        _to_java_column(col2) if isinstance(col2, (str, Column)) else float(col2)
    )


def _options_to_str(options):
    return {key: to_str(value) for (key, value) in options.items()}


@since(1.3)
def lit(col):
    """
    Creates a :class:`Column` of literal value.

    >>> df.select(lit(5).alias('height')).withColumn('spark_user', lit(True)).take(1)
    [Row(height=5, spark_user=True)]
    """
    return col if isinstance(col, Column) else _invoke_function("lit", col)


@since(1.3)
def col(col):
    """
    Returns a :class:`Column` based on the given column name.'
    """
    return _invoke_function("col", col)


@since(1.3)
def column(col):
    """
    Returns a :class:`Column` based on the given column name.'
    """
    return col(col)


@since(1.3)
def asc(col):
    """
    Returns a sort expression based on the ascending order of the given column name.
    """
    return _invoke_function("asc", col)


@since(1.3)
def desc(col):
    """
    Returns a sort expression based on the descending order of the given column name.
    """
    return _invoke_function("desc", col)


@since(1.3)
def sqrt(col):
    """
    Computes the square root of the specified float value.
    """
    return _invoke_function_over_column("sqrt", col)


@since(1.3)
def abs(col):
    """
    Computes the absolute value.
    """
    return _invoke_function_over_column("abs", col)


@since(1.3)
def max(col):
    """
    Aggregate function: returns the maximum value of the expression in a group.
    """
    return _invoke_function_over_column("max", col)


@since(1.3)
def min(col):
    """
    Aggregate function: returns the minimum value of the expression in a group.
    """
    return _invoke_function_over_column("min", col)


@since(1.3)
def count(col):
    """
    Aggregate function: returns the number of items in a group.
    """
    return _invoke_function_over_column("count", col)


@since(1.3)
def sum(col):
    """
    Aggregate function: returns the sum of all values in the expression.
    """
    return _invoke_function_over_column("sum", col)


@since(1.3)
def avg(col):
    """
    Aggregate function: returns the average of the values in a group.
    """
    return _invoke_function_over_column("avg", col)


@since(1.3)
def mean(col):
    """
    Aggregate function: returns the average of the values in a group.
    """
    return _invoke_function_over_column("mean", col)


@since(1.3)
def sumDistinct(col):
    """
    Aggregate function: returns the sum of distinct values in the expression.
    """
    return _invoke_function_over_column("sumDistinct", col)


@since(1.4)
def acos(col):
    """
    :return: inverse cosine of `col`, as if computed by `java.lang.Math.acos()`
    """
    return _invoke_function_over_column("acos", col)


@since(1.4)
def asin(col):
    """
    :return: inverse sine of `col`, as if computed by `java.lang.Math.asin()`
    """
    return _invoke_function_over_column("asin", col)


@since(1.4)
def atan(col):
    """
    :return: inverse tangent of `col`, as if computed by `java.lang.Math.atan()`
    """
    return _invoke_function_over_column("atan", col)


@since(1.4)
def cbrt(col):
    """
    Computes the cube-root of the given value.
    """
    return _invoke_function_over_column("cbrt", col)


@since(1.4)
def ceil(col):
    """
    Computes the ceiling of the given value.
    """
    return _invoke_function_over_column("ceil", col)


@since(1.4)
def cos(col):
    """
    :param col: angle in radians
    :return: cosine of the angle, as if computed by `java.lang.Math.cos()`.
    """
    return _invoke_function_over_column("cos", col)


@since(1.4)
def cosh(col):
    """
    :param col: hyperbolic angle
    :return: hyperbolic cosine of the angle, as if computed by `java.lang.Math.cosh()`
    """
    return _invoke_function_over_column("cosh", col)


@since(1.4)
def exp(col):
    """
    Computes the exponential of the given value.
    """
    return _invoke_function_over_column("exp", col)


@since(1.4)
def expm1(col):
    """
    Computes the exponential of the given value minus one.
    """
    return _invoke_function_over_column("expm1", col)


@since(1.4)
def floor(col):
    """
    Computes the floor of the given value.
    """
    return _invoke_function_over_column("floor", col)


@since(1.4)
def log(col):
    """
    Computes the natural logarithm of the given value.
    """
    return _invoke_function_over_column("log", col)


@since(1.4)
def log10(col):
    """
    Computes the logarithm of the given value in Base 10.
    """
    return _invoke_function_over_column("log10", col)


@since(1.4)
def log1p(col):
    """
    Computes the natural logarithm of the given value plus one.
    """
    return _invoke_function_over_column("log1p", col)


@since(1.4)
def rint(col):
    """
    Returns the double value that is closest in value to the argument and
    is equal to a mathematical integer.
    """
    return _invoke_function_over_column("rint", col)


@since(1.4)
def signum(col):
    """
    Computes the signum of the given value.
    """
    return _invoke_function_over_column("signum", col)


@since(1.4)
def sin(col):
    """
    :param col: angle in radians
    :return: sine of the angle, as if computed by `java.lang.Math.sin()`
    """
    return _invoke_function_over_column("sin", col)


@since(1.4)
def sinh(col):
    """
    :param col: hyperbolic angle
    :return: hyperbolic sine of the given value,
             as if computed by `java.lang.Math.sinh()`
    """
    return _invoke_function_over_column("sinh", col)


@since(1.4)
def tan(col):
    """
    :param col: angle in radians
    :return: tangent of the given value, as if computed by `java.lang.Math.tan()`
    """
    return _invoke_function_over_column("tan", col)


@since(1.4)
def tanh(col):
    """
    :param col: hyperbolic angle
    :return: hyperbolic tangent of the given value
             as if computed by `java.lang.Math.tanh()`
    """
    return _invoke_function_over_column("tanh", col)


@since(1.4)
def toDegrees(col):
    """
    .. note:: Deprecated in 2.1, use :func:`degrees` instead.
    """
    warnings.warn("Deprecated in 2.1, use degrees instead.", DeprecationWarning)
    return degrees(col)


@since(1.4)
def toRadians(col):
    """
    .. note:: Deprecated in 2.1, use :func:`radians` instead.
    """
    warnings.warn("Deprecated in 2.1, use radians instead.", DeprecationWarning)
    return radians(col)


@since(1.4)
def bitwiseNOT(col):
    """
    Computes bitwise not.
    """
    return _invoke_function_over_column("bitwiseNOT", col)


@since(2.4)
def asc_nulls_first(col):
    """
    Returns a sort expression based on the ascending order of the given
    column name, and null values return before non-null values.
    """
    return _invoke_function("asc_nulls_first", col)


@since(2.4)
def asc_nulls_last(col):
    """
    Returns a sort expression based on the ascending order of the given
    column name, and null values appear after non-null values.
    """
    return _invoke_function("asc_nulls_last", col)


@since(2.4)
def desc_nulls_first(col):
    """
    Returns a sort expression based on the descending order of the given
    column name, and null values appear before non-null values.
    """
    return _invoke_function("desc_nulls_first", col)


@since(2.4)
def desc_nulls_last(col):
    """
    Returns a sort expression based on the descending order of the given
    column name, and null values appear after non-null values.
    """
    return _invoke_function("desc_nulls_last", col)


@since(1.6)
def stddev(col):
    """
    Aggregate function: alias for stddev_samp.
    """
    return _invoke_function_over_column("stddev", col)


@since(1.6)
def stddev_samp(col):
    """
    Aggregate function: returns the unbiased sample standard deviation of
    the expression in a group.
    """
    return _invoke_function_over_column("stddev_samp", col)


@since(1.6)
def stddev_pop(col):
    """
    Aggregate function: returns population standard deviation of
    the expression in a group.
    """
    return _invoke_function_over_column("stddev_pop", col)


@since(1.6)
def variance(col):
    """
    Aggregate function: alias for var_samp
    """
    return _invoke_function_over_column("variance", col)


@since(1.6)
def var_samp(col):
    """
    Aggregate function: returns the unbiased sample variance of
    the values in a group.
    """
    return _invoke_function_over_column("var_samp", col)


@since(1.6)
def var_pop(col):
    """
    Aggregate function: returns the population variance of the values in a group.
    """
    return _invoke_function_over_column("var_pop", col)


@since(1.6)
def skewness(col):
    """
    Aggregate function: returns the skewness of the values in a group.
    """
    return _invoke_function_over_column("skewness", col)


@since(1.6)
def kurtosis(col):
    """
    Aggregate function: returns the kurtosis of the values in a group.
    """
    return _invoke_function_over_column("kurtosis", col)


@since(1.6)
def collect_list(col):
    """
    Aggregate function: returns a list of objects with duplicates.

    .. note:: The function is non-deterministic because the order of collected results depends
        on the order of the rows which may be non-deterministic after a shuffle.

    >>> df2 = spark.createDataFrame([(2,), (5,), (5,)], ('age',))
    >>> df2.agg(collect_list('age')).collect()
    [Row(collect_list(age)=[2, 5, 5])]
    """
    return _invoke_function_over_column("collect_list", col)


@since(1.6)
def collect_set(col):
    """
    Aggregate function: returns a set of objects with duplicate elements eliminated.

    .. note:: The function is non-deterministic because the order of collected results depends
        on the order of the rows which may be non-deterministic after a shuffle.

    >>> df2 = spark.createDataFrame([(2,), (5,), (5,)], ('age',))
    >>> df2.agg(collect_set('age')).collect()
    [Row(collect_set(age)=[5, 2])]
    """
    return _invoke_function_over_column("collect_set", col)


@since(2.1)
def degrees(col):
    """
    Converts an angle measured in radians to an approximately equivalent angle
    measured in degrees.

    :param col: angle in radians
    :return: angle in degrees, as if computed by `java.lang.Math.toDegrees()`
    """
    return _invoke_function_over_column("degrees", col)


@since(2.1)
def radians(col):
    """
    Converts an angle measured in degrees to an approximately equivalent angle
    measured in radians.

    :param col: angle in degrees
    :return: angle in radians, as if computed by `java.lang.Math.toRadians()`
    """
    return _invoke_function_over_column("radians", col)


@since(1.4)
def atan2(col1, col2):
    """
    :param col1: coordinate on y-axis
    :param col2: coordinate on x-axis
    :return: the `theta` component of the point
          (`r`, `theta`)
          in polar coordinates that corresponds to the point
          (`x`, `y`) in Cartesian coordinates,
          as if computed by `java.lang.Math.atan2()`
    """
    return _invoke_binary_math_function("atan2", col1, col2)


@since(1.4)
def hypot(col1, col2):
    """
    Computes ``sqrt(a^2 + b^2)`` without intermediate overflow or underflow.
    """
    return _invoke_binary_math_function("hypot", col1, col2)


@since(1.4)
def pow(col1, col2):
    """
    Returns the value of the first argument raised to the power of the second argument.
    """
    return _invoke_binary_math_function("pow", col1, col2)


@since(1.6)
def row_number():
    """
    Window function: returns a sequential number starting at 1 within a window partition.
    """
    return _invoke_function("row_number")


@since(1.6)
def dense_rank():
    """
    Window function: returns the rank of rows within a window partition, without any gaps.

    The difference between rank and dense_rank is that dense_rank leaves no gaps in ranking
    sequence when there are ties. That is, if you were ranking a competition using dense_rank
    and had three people tie for second place, you would say that all three were in second
    place and that the next person came in third. Rank would give me sequential numbers, making
    the person that came in third place (after the ties) would register as coming in fifth.

    This is equivalent to the DENSE_RANK function in SQL.
    """
    return _invoke_function("dense_rank")


@since(1.6)
def rank():
    """
    Window function: returns the rank of rows within a window partition.

    The difference between rank and dense_rank is that dense_rank leaves no gaps in ranking
    sequence when there are ties. That is, if you were ranking a competition using dense_rank
    and had three people tie for second place, you would say that all three were in second
    place and that the next person came in third. Rank would give me sequential numbers, making
    the person that came in third place (after the ties) would register as coming in fifth.

    This is equivalent to the RANK function in SQL.
    """
    return _invoke_function("rank")


@since(1.6)
def cume_dist():
    """
    Window function: returns the cumulative distribution of values within a window partition,
    i.e. the fraction of rows that are below the current row.
    """
    return _invoke_function("cume_dist")


@since(1.6)
def percent_rank():
    """
    Window function: returns the relative rank (i.e. percentile) of rows within a window partition.
    """
    return _invoke_function("percent_rank")


@since(1.3)
def approxCountDistinct(col, rsd=None):
    """
    .. note:: Deprecated in 2.1, use :func:`approx_count_distinct` instead.
    """
    warnings.warn("Deprecated in 2.1, use approx_count_distinct instead.", DeprecationWarning)
    return approx_count_distinct(col, rsd)


@since(2.1)
def approx_count_distinct(col, rsd=None):
    """Aggregate function: returns a new :class:`Column` for approximate distinct count of
    column `col`.

    :param rsd: maximum relative standard deviation allowed (default = 0.05).
        For rsd < 0.01, it is more efficient to use :func:`countDistinct`

    >>> df.agg(approx_count_distinct(df.age).alias('distinct_ages')).collect()
    [Row(distinct_ages=2)]
    """
    sc = SparkContext._active_spark_context
    if rsd is None:
        jc = sc._jvm.functions.approx_count_distinct(_to_java_column(col))
    else:
        jc = sc._jvm.functions.approx_count_distinct(_to_java_column(col), rsd)
    return Column(jc)


@since(1.6)
def broadcast(df):
    """Marks a DataFrame as small enough for use in broadcast joins."""

    sc = SparkContext._active_spark_context
    return DataFrame(sc._jvm.functions.broadcast(df._jdf), df.sql_ctx)


@since(1.4)
def coalesce(*cols):
    """Returns the first column that is not null.

    >>> cDf = spark.createDataFrame([(None, None), (1, None), (None, 2)], ("a", "b"))
    >>> cDf.show()
    +----+----+
    |   a|   b|
    +----+----+
    |null|null|
    |   1|null|
    |null|   2|
    +----+----+

    >>> cDf.select(coalesce(cDf["a"], cDf["b"])).show()
    +--------------+
    |coalesce(a, b)|
    +--------------+
    |          null|
    |             1|
    |             2|
    +--------------+

    >>> cDf.select('*', coalesce(cDf["a"], lit(0.0))).show()
    +----+----+----------------+
    |   a|   b|coalesce(a, 0.0)|
    +----+----+----------------+
    |null|null|             0.0|
    |   1|null|             1.0|
    |null|   2|             0.0|
    +----+----+----------------+
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.coalesce(_to_seq(sc, cols, _to_java_column))
    return Column(jc)


@since(1.6)
def corr(col1, col2):
    """Returns a new :class:`Column` for the Pearson Correlation Coefficient for ``col1``
    and ``col2``.

    >>> a = range(20)
    >>> b = [2 * x for x in range(20)]
    >>> df = spark.createDataFrame(zip(a, b), ["a", "b"])
    >>> df.agg(corr("a", "b").alias('c')).collect()
    [Row(c=1.0)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.corr(_to_java_column(col1), _to_java_column(col2)))


@since(2.0)
def covar_pop(col1, col2):
    """Returns a new :class:`Column` for the population covariance of ``col1`` and ``col2``.

    >>> a = [1] * 10
    >>> b = [1] * 10
    >>> df = spark.createDataFrame(zip(a, b), ["a", "b"])
    >>> df.agg(covar_pop("a", "b").alias('c')).collect()
    [Row(c=0.0)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.covar_pop(_to_java_column(col1), _to_java_column(col2)))


@since(2.0)
def covar_samp(col1, col2):
    """Returns a new :class:`Column` for the sample covariance of ``col1`` and ``col2``.

    >>> a = [1] * 10
    >>> b = [1] * 10
    >>> df = spark.createDataFrame(zip(a, b), ["a", "b"])
    >>> df.agg(covar_samp("a", "b").alias('c')).collect()
    [Row(c=0.0)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.covar_samp(_to_java_column(col1), _to_java_column(col2)))


@since(1.3)
def countDistinct(col, *cols):
    """Returns a new :class:`Column` for distinct count of ``col`` or ``cols``.

    >>> df.agg(countDistinct(df.age, df.name).alias('c')).collect()
    [Row(c=2)]

    >>> df.agg(countDistinct("age", "name").alias('c')).collect()
    [Row(c=2)]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.countDistinct(_to_java_column(col), _to_seq(sc, cols, _to_java_column))
    return Column(jc)


@since(1.3)
def first(col, ignorenulls=False):
    """Aggregate function: returns the first value in a group.

    The function by default returns the first values it sees. It will return the first non-null
    value it sees when ignoreNulls is set to true. If all values are null, then null is returned.

    .. note:: The function is non-deterministic because its results depends on the order of the
        rows which may be non-deterministic after a shuffle.
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.first(_to_java_column(col), ignorenulls)
    return Column(jc)


@since(2.0)
def grouping(col):
    """
    Aggregate function: indicates whether a specified column in a GROUP BY list is aggregated
    or not, returns 1 for aggregated or 0 for not aggregated in the result set.

    >>> df.cube("name").agg(grouping("name"), sum("age")).orderBy("name").show()
    +-----+--------------+--------+
    | name|grouping(name)|sum(age)|
    +-----+--------------+--------+
    | null|             1|       7|
    |Alice|             0|       2|
    |  Bob|             0|       5|
    +-----+--------------+--------+
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.grouping(_to_java_column(col))
    return Column(jc)


@since(2.0)
def grouping_id(*cols):
    """
    Aggregate function: returns the level of grouping, equals to

       (grouping(c1) << (n-1)) + (grouping(c2) << (n-2)) + ... + grouping(cn)

    .. note:: The list of columns should match with grouping columns exactly, or empty (means all
        the grouping columns).

    >>> df.cube("name").agg(grouping_id(), sum("age")).orderBy("name").show()
    +-----+-------------+--------+
    | name|grouping_id()|sum(age)|
    +-----+-------------+--------+
    | null|            1|       7|
    |Alice|            0|       2|
    |  Bob|            0|       5|
    +-----+-------------+--------+
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.grouping_id(_to_seq(sc, cols, _to_java_column))
    return Column(jc)


@since(1.6)
def input_file_name():
    """Creates a string column for the file name of the current Spark task.
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.input_file_name())


@since(1.6)
def isnan(col):
    """An expression that returns true iff the column is NaN.

    >>> df = spark.createDataFrame([(1.0, float('nan')), (float('nan'), 2.0)], ("a", "b"))
    >>> df.select(isnan("a").alias("r1"), isnan(df.a).alias("r2")).collect()
    [Row(r1=False, r2=False), Row(r1=True, r2=True)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.isnan(_to_java_column(col)))


@since(1.6)
def isnull(col):
    """An expression that returns true iff the column is null.

    >>> df = spark.createDataFrame([(1, None), (None, 2)], ("a", "b"))
    >>> df.select(isnull("a").alias("r1"), isnull(df.a).alias("r2")).collect()
    [Row(r1=False, r2=False), Row(r1=True, r2=True)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.isnull(_to_java_column(col)))


@since(1.3)
def last(col, ignorenulls=False):
    """Aggregate function: returns the last value in a group.

    The function by default returns the last values it sees. It will return the last non-null
    value it sees when ignoreNulls is set to true. If all values are null, then null is returned.

    .. note:: The function is non-deterministic because its results depends on the order of the
        rows which may be non-deterministic after a shuffle.
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.last(_to_java_column(col), ignorenulls)
    return Column(jc)


@since(1.6)
def monotonically_increasing_id():
    """A column that generates monotonically increasing 64-bit integers.

    The generated ID is guaranteed to be monotonically increasing and unique, but not consecutive.
    The current implementation puts the partition ID in the upper 31 bits, and the record number
    within each partition in the lower 33 bits. The assumption is that the data frame has
    less than 1 billion partitions, and each partition has less than 8 billion records.

    .. note:: The function is non-deterministic because its result depends on partition IDs.

    As an example, consider a :class:`DataFrame` with two partitions, each with 3 records.
    This expression would return the following IDs:
    0, 1, 2, 8589934592 (1L << 33), 8589934593, 8589934594.

    >>> df0 = sc.parallelize(range(2), 2).mapPartitions(lambda x: [(1,), (2,), (3,)]).toDF(['col1'])
    >>> df0.select(monotonically_increasing_id().alias('id')).collect()
    [Row(id=0), Row(id=1), Row(id=2), Row(id=8589934592), Row(id=8589934593), Row(id=8589934594)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.monotonically_increasing_id())


@since(1.6)
def nanvl(col1, col2):
    """Returns col1 if it is not NaN, or col2 if col1 is NaN.

    Both inputs should be floating point columns (:class:`DoubleType` or :class:`FloatType`).

    >>> df = spark.createDataFrame([(1.0, float('nan')), (float('nan'), 2.0)], ("a", "b"))
    >>> df.select(nanvl("a", "b").alias("r1"), nanvl(df.a, df.b).alias("r2")).collect()
    [Row(r1=1.0, r2=1.0), Row(r1=2.0, r2=2.0)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.nanvl(_to_java_column(col1), _to_java_column(col2)))


@since(3.1)
def percentile_approx(col, percentage, accuracy=10000):
    """Returns the approximate `percentile` of the numeric column `col` which is the smallest value
    in the ordered `col` values (sorted from least to greatest) such that no more than `percentage`
    of `col` values is less than the value or equal to that value.
    The value of percentage must be between 0.0 and 1.0.

    The accuracy parameter (default: 10000)
    is a positive numeric literal which controls approximation accuracy at the cost of memory.
    Higher value of accuracy yields better accuracy, 1.0/accuracy is the relative error
    of the approximation.

    When percentage is an array, each value of the percentage array must be between 0.0 and 1.0.
    In this case, returns the approximate percentile array of column col
    at the given percentage array.

    >>> key = (col("id") % 3).alias("key")
    >>> value = (randn(42) + key * 10).alias("value")
    >>> df = spark.range(0, 1000, 1, 1).select(key, value)
    >>> df.select(
    ...     percentile_approx("value", [0.25, 0.5, 0.75], 1000000).alias("quantiles")
    ... ).printSchema()
    root
     |-- quantiles: array (nullable = true)
     |    |-- element: double (containsNull = false)

    >>> df.groupBy("key").agg(
    ...     percentile_approx("value", 0.5, lit(1000000)).alias("median")
    ... ).printSchema()
    root
     |-- key: long (nullable = true)
     |-- median: double (nullable = true)
    """
    sc = SparkContext._active_spark_context

    if isinstance(percentage, (list, tuple)):
        # A local list
        percentage = sc._jvm.functions.array(_to_seq(sc, [
            _create_column_from_literal(x) for x in percentage
        ]))
    elif isinstance(percentage, Column):
        # Already a Column
        percentage = _to_java_column(percentage)
    else:
        # Probably scalar
        percentage = _create_column_from_literal(percentage)

    accuracy = (
        _to_java_column(accuracy) if isinstance(accuracy, Column)
        else _create_column_from_literal(accuracy)
    )

    return Column(sc._jvm.functions.percentile_approx(_to_java_column(col), percentage, accuracy))


@since(1.4)
def rand(seed=None):
    """Generates a random column with independent and identically distributed (i.i.d.) samples
    uniformly distributed in [0.0, 1.0).

    .. note:: The function is non-deterministic in general case.

    >>> df.withColumn('rand', rand(seed=42) * 3).collect()
    [Row(age=2, name='Alice', rand=2.4052597283576684),
     Row(age=5, name='Bob', rand=2.3913904055683974)]
    """
    sc = SparkContext._active_spark_context
    if seed is not None:
        jc = sc._jvm.functions.rand(seed)
    else:
        jc = sc._jvm.functions.rand()
    return Column(jc)


@since(1.4)
def randn(seed=None):
    """Generates a column with independent and identically distributed (i.i.d.) samples from
    the standard normal distribution.

    .. note:: The function is non-deterministic in general case.

    >>> df.withColumn('randn', randn(seed=42)).collect()
    [Row(age=2, name='Alice', randn=1.1027054481455365),
    Row(age=5, name='Bob', randn=0.7400395449950132)]
    """
    sc = SparkContext._active_spark_context
    if seed is not None:
        jc = sc._jvm.functions.randn(seed)
    else:
        jc = sc._jvm.functions.randn()
    return Column(jc)


@since(1.5)
def round(col, scale=0):
    """
    Round the given value to `scale` decimal places using HALF_UP rounding mode if `scale` >= 0
    or at integral part when `scale` < 0.

    >>> spark.createDataFrame([(2.5,)], ['a']).select(round('a', 0).alias('r')).collect()
    [Row(r=3.0)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.round(_to_java_column(col), scale))


@since(2.0)
def bround(col, scale=0):
    """
    Round the given value to `scale` decimal places using HALF_EVEN rounding mode if `scale` >= 0
    or at integral part when `scale` < 0.

    >>> spark.createDataFrame([(2.5,)], ['a']).select(bround('a', 0).alias('r')).collect()
    [Row(r=2.0)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.bround(_to_java_column(col), scale))


@since(1.5)
def shiftLeft(col, numBits):
    """Shift the given value numBits left.

    >>> spark.createDataFrame([(21,)], ['a']).select(shiftLeft('a', 1).alias('r')).collect()
    [Row(r=42)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.shiftLeft(_to_java_column(col), numBits))


@since(1.5)
def shiftRight(col, numBits):
    """(Signed) shift the given value numBits right.

    >>> spark.createDataFrame([(42,)], ['a']).select(shiftRight('a', 1).alias('r')).collect()
    [Row(r=21)]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.shiftRight(_to_java_column(col), numBits)
    return Column(jc)


@since(1.5)
def shiftRightUnsigned(col, numBits):
    """Unsigned shift the given value numBits right.

    >>> df = spark.createDataFrame([(-42,)], ['a'])
    >>> df.select(shiftRightUnsigned('a', 1).alias('r')).collect()
    [Row(r=9223372036854775787)]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.shiftRightUnsigned(_to_java_column(col), numBits)
    return Column(jc)


@since(1.6)
def spark_partition_id():
    """A column for partition ID.

    .. note:: This is indeterministic because it depends on data partitioning and task scheduling.

    >>> df.repartition(1).select(spark_partition_id().alias("pid")).collect()
    [Row(pid=0), Row(pid=0)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.spark_partition_id())


@since(1.5)
def expr(str):
    """Parses the expression string into the column that it represents

    >>> df.select(expr("length(name)")).collect()
    [Row(length(name)=5), Row(length(name)=3)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.expr(str))


@since(1.4)
def struct(*cols):
    """Creates a new struct column.

    :param cols: list of column names (string) or list of :class:`Column` expressions

    >>> df.select(struct('age', 'name').alias("struct")).collect()
    [Row(struct=Row(age=2, name='Alice')), Row(struct=Row(age=5, name='Bob'))]
    >>> df.select(struct([df.age, df.name]).alias("struct")).collect()
    [Row(struct=Row(age=2, name='Alice')), Row(struct=Row(age=5, name='Bob'))]
    """
    sc = SparkContext._active_spark_context
    if len(cols) == 1 and isinstance(cols[0], (list, set)):
        cols = cols[0]
    jc = sc._jvm.functions.struct(_to_seq(sc, cols, _to_java_column))
    return Column(jc)


@since(1.5)
def greatest(*cols):
    """
    Returns the greatest value of the list of column names, skipping null values.
    This function takes at least 2 parameters. It will return null iff all parameters are null.

    >>> df = spark.createDataFrame([(1, 4, 3)], ['a', 'b', 'c'])
    >>> df.select(greatest(df.a, df.b, df.c).alias("greatest")).collect()
    [Row(greatest=4)]
    """
    if len(cols) < 2:
        raise ValueError("greatest should take at least two columns")
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.greatest(_to_seq(sc, cols, _to_java_column)))


@since(1.5)
def least(*cols):
    """
    Returns the least value of the list of column names, skipping null values.
    This function takes at least 2 parameters. It will return null iff all parameters are null.

    >>> df = spark.createDataFrame([(1, 4, 3)], ['a', 'b', 'c'])
    >>> df.select(least(df.a, df.b, df.c).alias("least")).collect()
    [Row(least=1)]
    """
    if len(cols) < 2:
        raise ValueError("least should take at least two columns")
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.least(_to_seq(sc, cols, _to_java_column)))


@since(1.4)
def when(condition, value):
    """Evaluates a list of conditions and returns one of multiple possible result expressions.
    If :func:`Column.otherwise` is not invoked, None is returned for unmatched conditions.

    :param condition: a boolean :class:`Column` expression.
    :param value: a literal value, or a :class:`Column` expression.

    >>> df.select(when(df['age'] == 2, 3).otherwise(4).alias("age")).collect()
    [Row(age=3), Row(age=4)]

    >>> df.select(when(df.age == 2, df.age + 1).alias("age")).collect()
    [Row(age=3), Row(age=None)]
    """
    sc = SparkContext._active_spark_context
    if not isinstance(condition, Column):
        raise TypeError("condition should be a Column")
    v = value._jc if isinstance(value, Column) else value
    jc = sc._jvm.functions.when(condition._jc, v)
    return Column(jc)


@since(1.5)
def log(arg1, arg2=None):
    """Returns the first argument-based logarithm of the second argument.

    If there is only one argument, then this takes the natural logarithm of the argument.

    >>> df.select(log(10.0, df.age).alias('ten')).rdd.map(lambda l: str(l.ten)[:7]).collect()
    ['0.30102', '0.69897']

    >>> df.select(log(df.age).alias('e')).rdd.map(lambda l: str(l.e)[:7]).collect()
    ['0.69314', '1.60943']
    """
    sc = SparkContext._active_spark_context
    if arg2 is None:
        jc = sc._jvm.functions.log(_to_java_column(arg1))
    else:
        jc = sc._jvm.functions.log(arg1, _to_java_column(arg2))
    return Column(jc)


@since(1.5)
def log2(col):
    """Returns the base-2 logarithm of the argument.

    >>> spark.createDataFrame([(4,)], ['a']).select(log2('a').alias('log2')).collect()
    [Row(log2=2.0)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.log2(_to_java_column(col)))


@since(1.5)
def conv(col, fromBase, toBase):
    """
    Convert a number in a string column from one base to another.

    >>> df = spark.createDataFrame([("010101",)], ['n'])
    >>> df.select(conv(df.n, 2, 16).alias('hex')).collect()
    [Row(hex='15')]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.conv(_to_java_column(col), fromBase, toBase))


@since(1.5)
def factorial(col):
    """
    Computes the factorial of the given value.

    >>> df = spark.createDataFrame([(5,)], ['n'])
    >>> df.select(factorial(df.n).alias('f')).collect()
    [Row(f=120)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.factorial(_to_java_column(col)))


# ---------------  Window functions ------------------------

@since(1.4)
def lag(col, offset=1, default=None):
    """
    Window function: returns the value that is `offset` rows before the current row, and
    `defaultValue` if there is less than `offset` rows before the current row. For example,
    an `offset` of one will return the previous row at any given point in the window partition.

    This is equivalent to the LAG function in SQL.

    :param col: name of column or expression
    :param offset: number of row to extend
    :param default: default value
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.lag(_to_java_column(col), offset, default))


@since(1.4)
def lead(col, offset=1, default=None):
    """
    Window function: returns the value that is `offset` rows after the current row, and
    `defaultValue` if there is less than `offset` rows after the current row. For example,
    an `offset` of one will return the next row at any given point in the window partition.

    This is equivalent to the LEAD function in SQL.

    :param col: name of column or expression
    :param offset: number of row to extend
    :param default: default value
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.lead(_to_java_column(col), offset, default))


@since(3.1)
def nth_value(col, offset, ignoreNulls=False):
    """
    Window function: returns the value that is the `offset`\\th row of the window frame
    (counting from 1), and `null` if the size of window frame is less than `offset` rows.

    It will return the `offset`\\th non-null value it sees when `ignoreNulls` is set to
    true. If all values are null, then null is returned.

    This is equivalent to the nth_value function in SQL.

    :param col: name of column or expression
    :param offset: number of row to use as the value
    :param ignoreNulls: indicates the Nth value should skip null in the
        determination of which row to use
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.nth_value(_to_java_column(col), offset, ignoreNulls))


@since(1.4)
def ntile(n):
    """
    Window function: returns the ntile group id (from 1 to `n` inclusive)
    in an ordered window partition. For example, if `n` is 4, the first
    quarter of the rows will get value 1, the second quarter will get 2,
    the third quarter will get 3, and the last quarter will get 4.

    This is equivalent to the NTILE function in SQL.

    :param n: an integer
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.ntile(int(n)))


# ---------------------- Date/Timestamp functions ------------------------------

@since(1.5)
def current_date():
    """
    Returns the current date at the start of query evaluation as a :class:`DateType` column.
    All calls of current_date within the same query return the same value.
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.current_date())


def current_timestamp():
    """
    Returns the current timestamp at the start of query evaluation as a :class:`TimestampType`
    column. All calls of current_timestamp within the same query return the same value.
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.current_timestamp())


@since(1.5)
def date_format(date, format):
    """
    Converts a date/timestamp/string to a value of string in the format specified by the date
    format given by the second argument.

    A pattern could be for instance `dd.MM.yyyy` and could return a string like '18.03.1993'. All
    pattern letters of `datetime pattern`_. can be used.

    .. _datetime pattern: https://spark.apache.org/docs/latest/sql-ref-datetime-pattern.html
    .. note:: Use when ever possible specialized functions like `year`. These benefit from a
        specialized implementation.

    >>> df = spark.createDataFrame([('2015-04-08',)], ['dt'])
    >>> df.select(date_format('dt', 'MM/dd/yyy').alias('date')).collect()
    [Row(date='04/08/2015')]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.date_format(_to_java_column(date), format))


@since(1.5)
def year(col):
    """
    Extract the year of a given date as integer.

    >>> df = spark.createDataFrame([('2015-04-08',)], ['dt'])
    >>> df.select(year('dt').alias('year')).collect()
    [Row(year=2015)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.year(_to_java_column(col)))


@since(1.5)
def quarter(col):
    """
    Extract the quarter of a given date as integer.

    >>> df = spark.createDataFrame([('2015-04-08',)], ['dt'])
    >>> df.select(quarter('dt').alias('quarter')).collect()
    [Row(quarter=2)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.quarter(_to_java_column(col)))


@since(1.5)
def month(col):
    """
    Extract the month of a given date as integer.

    >>> df = spark.createDataFrame([('2015-04-08',)], ['dt'])
    >>> df.select(month('dt').alias('month')).collect()
    [Row(month=4)]
   """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.month(_to_java_column(col)))


@since(2.3)
def dayofweek(col):
    """
    Extract the day of the week of a given date as integer.

    >>> df = spark.createDataFrame([('2015-04-08',)], ['dt'])
    >>> df.select(dayofweek('dt').alias('day')).collect()
    [Row(day=4)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.dayofweek(_to_java_column(col)))


@since(1.5)
def dayofmonth(col):
    """
    Extract the day of the month of a given date as integer.

    >>> df = spark.createDataFrame([('2015-04-08',)], ['dt'])
    >>> df.select(dayofmonth('dt').alias('day')).collect()
    [Row(day=8)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.dayofmonth(_to_java_column(col)))


@since(1.5)
def dayofyear(col):
    """
    Extract the day of the year of a given date as integer.

    >>> df = spark.createDataFrame([('2015-04-08',)], ['dt'])
    >>> df.select(dayofyear('dt').alias('day')).collect()
    [Row(day=98)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.dayofyear(_to_java_column(col)))


@since(1.5)
def hour(col):
    """
    Extract the hours of a given date as integer.

    >>> df = spark.createDataFrame([('2015-04-08 13:08:15',)], ['ts'])
    >>> df.select(hour('ts').alias('hour')).collect()
    [Row(hour=13)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.hour(_to_java_column(col)))


@since(1.5)
def minute(col):
    """
    Extract the minutes of a given date as integer.

    >>> df = spark.createDataFrame([('2015-04-08 13:08:15',)], ['ts'])
    >>> df.select(minute('ts').alias('minute')).collect()
    [Row(minute=8)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.minute(_to_java_column(col)))


@since(1.5)
def second(col):
    """
    Extract the seconds of a given date as integer.

    >>> df = spark.createDataFrame([('2015-04-08 13:08:15',)], ['ts'])
    >>> df.select(second('ts').alias('second')).collect()
    [Row(second=15)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.second(_to_java_column(col)))


@since(1.5)
def weekofyear(col):
    """
    Extract the week number of a given date as integer.

    >>> df = spark.createDataFrame([('2015-04-08',)], ['dt'])
    >>> df.select(weekofyear(df.dt).alias('week')).collect()
    [Row(week=15)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.weekofyear(_to_java_column(col)))


@since(1.5)
def date_add(start, days):
    """
    Returns the date that is `days` days after `start`

    >>> df = spark.createDataFrame([('2015-04-08',)], ['dt'])
    >>> df.select(date_add(df.dt, 1).alias('next_date')).collect()
    [Row(next_date=datetime.date(2015, 4, 9))]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.date_add(_to_java_column(start), days))


@since(1.5)
def date_sub(start, days):
    """
    Returns the date that is `days` days before `start`

    >>> df = spark.createDataFrame([('2015-04-08',)], ['dt'])
    >>> df.select(date_sub(df.dt, 1).alias('prev_date')).collect()
    [Row(prev_date=datetime.date(2015, 4, 7))]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.date_sub(_to_java_column(start), days))


@since(1.5)
def datediff(end, start):
    """
    Returns the number of days from `start` to `end`.

    >>> df = spark.createDataFrame([('2015-04-08','2015-05-10')], ['d1', 'd2'])
    >>> df.select(datediff(df.d2, df.d1).alias('diff')).collect()
    [Row(diff=32)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.datediff(_to_java_column(end), _to_java_column(start)))


@since(1.5)
def add_months(start, months):
    """
    Returns the date that is `months` months after `start`

    >>> df = spark.createDataFrame([('2015-04-08',)], ['dt'])
    >>> df.select(add_months(df.dt, 1).alias('next_month')).collect()
    [Row(next_month=datetime.date(2015, 5, 8))]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.add_months(_to_java_column(start), months))


@since(1.5)
def months_between(date1, date2, roundOff=True):
    """
    Returns number of months between dates date1 and date2.
    If date1 is later than date2, then the result is positive.
    If date1 and date2 are on the same day of month, or both are the last day of month,
    returns an integer (time of day will be ignored).
    The result is rounded off to 8 digits unless `roundOff` is set to `False`.

    >>> df = spark.createDataFrame([('1997-02-28 10:30:00', '1996-10-30')], ['date1', 'date2'])
    >>> df.select(months_between(df.date1, df.date2).alias('months')).collect()
    [Row(months=3.94959677)]
    >>> df.select(months_between(df.date1, df.date2, False).alias('months')).collect()
    [Row(months=3.9495967741935485)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.months_between(
        _to_java_column(date1), _to_java_column(date2), roundOff))


@since(2.2)
def to_date(col, format=None):
    """Converts a :class:`Column` into :class:`pyspark.sql.types.DateType`
    using the optionally specified format. Specify formats according to `datetime pattern`_.
    By default, it follows casting rules to :class:`pyspark.sql.types.DateType` if the format
    is omitted. Equivalent to ``col.cast("date")``.

    .. _datetime pattern: https://spark.apache.org/docs/latest/sql-ref-datetime-pattern.html

    >>> df = spark.createDataFrame([('1997-02-28 10:30:00',)], ['t'])
    >>> df.select(to_date(df.t).alias('date')).collect()
    [Row(date=datetime.date(1997, 2, 28))]

    >>> df = spark.createDataFrame([('1997-02-28 10:30:00',)], ['t'])
    >>> df.select(to_date(df.t, 'yyyy-MM-dd HH:mm:ss').alias('date')).collect()
    [Row(date=datetime.date(1997, 2, 28))]
    """
    sc = SparkContext._active_spark_context
    if format is None:
        jc = sc._jvm.functions.to_date(_to_java_column(col))
    else:
        jc = sc._jvm.functions.to_date(_to_java_column(col), format)
    return Column(jc)


@since(2.2)
def to_timestamp(col, format=None):
    """Converts a :class:`Column` into :class:`pyspark.sql.types.TimestampType`
    using the optionally specified format. Specify formats according to `datetime pattern`_.
    By default, it follows casting rules to :class:`pyspark.sql.types.TimestampType` if the format
    is omitted. Equivalent to ``col.cast("timestamp")``.

    .. _datetime pattern: https://spark.apache.org/docs/latest/sql-ref-datetime-pattern.html

    >>> df = spark.createDataFrame([('1997-02-28 10:30:00',)], ['t'])
    >>> df.select(to_timestamp(df.t).alias('dt')).collect()
    [Row(dt=datetime.datetime(1997, 2, 28, 10, 30))]

    >>> df = spark.createDataFrame([('1997-02-28 10:30:00',)], ['t'])
    >>> df.select(to_timestamp(df.t, 'yyyy-MM-dd HH:mm:ss').alias('dt')).collect()
    [Row(dt=datetime.datetime(1997, 2, 28, 10, 30))]
    """
    sc = SparkContext._active_spark_context
    if format is None:
        jc = sc._jvm.functions.to_timestamp(_to_java_column(col))
    else:
        jc = sc._jvm.functions.to_timestamp(_to_java_column(col), format)
    return Column(jc)


@since(1.5)
def trunc(date, format):
    """
    Returns date truncated to the unit specified by the format.

    :param format: 'year', 'yyyy', 'yy' or 'month', 'mon', 'mm'

    >>> df = spark.createDataFrame([('1997-02-28',)], ['d'])
    >>> df.select(trunc(df.d, 'year').alias('year')).collect()
    [Row(year=datetime.date(1997, 1, 1))]
    >>> df.select(trunc(df.d, 'mon').alias('month')).collect()
    [Row(month=datetime.date(1997, 2, 1))]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.trunc(_to_java_column(date), format))


@since(2.3)
def date_trunc(format, timestamp):
    """
    Returns timestamp truncated to the unit specified by the format.

    :param format: 'year', 'yyyy', 'yy', 'month', 'mon', 'mm',
        'day', 'dd', 'hour', 'minute', 'second', 'week', 'quarter'

    >>> df = spark.createDataFrame([('1997-02-28 05:02:11',)], ['t'])
    >>> df.select(date_trunc('year', df.t).alias('year')).collect()
    [Row(year=datetime.datetime(1997, 1, 1, 0, 0))]
    >>> df.select(date_trunc('mon', df.t).alias('month')).collect()
    [Row(month=datetime.datetime(1997, 2, 1, 0, 0))]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.date_trunc(format, _to_java_column(timestamp)))


@since(1.5)
def next_day(date, dayOfWeek):
    """
    Returns the first date which is later than the value of the date column.

    Day of the week parameter is case insensitive, and accepts:
        "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun".

    >>> df = spark.createDataFrame([('2015-07-27',)], ['d'])
    >>> df.select(next_day(df.d, 'Sun').alias('date')).collect()
    [Row(date=datetime.date(2015, 8, 2))]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.next_day(_to_java_column(date), dayOfWeek))


@since(1.5)
def last_day(date):
    """
    Returns the last day of the month which the given date belongs to.

    >>> df = spark.createDataFrame([('1997-02-10',)], ['d'])
    >>> df.select(last_day(df.d).alias('date')).collect()
    [Row(date=datetime.date(1997, 2, 28))]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.last_day(_to_java_column(date)))


@since(1.5)
def from_unixtime(timestamp, format="yyyy-MM-dd HH:mm:ss"):
    """
    Converts the number of seconds from unix epoch (1970-01-01 00:00:00 UTC) to a string
    representing the timestamp of that moment in the current system time zone in the given
    format.

    >>> spark.conf.set("spark.sql.session.timeZone", "America/Los_Angeles")
    >>> time_df = spark.createDataFrame([(1428476400,)], ['unix_time'])
    >>> time_df.select(from_unixtime('unix_time').alias('ts')).collect()
    [Row(ts='2015-04-08 00:00:00')]
    >>> spark.conf.unset("spark.sql.session.timeZone")
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.from_unixtime(_to_java_column(timestamp), format))


@since(1.5)
def unix_timestamp(timestamp=None, format='yyyy-MM-dd HH:mm:ss'):
    """
    Convert time string with given pattern ('yyyy-MM-dd HH:mm:ss', by default)
    to Unix time stamp (in seconds), using the default timezone and the default
    locale, return null if fail.

    if `timestamp` is None, then it returns current timestamp.

    >>> spark.conf.set("spark.sql.session.timeZone", "America/Los_Angeles")
    >>> time_df = spark.createDataFrame([('2015-04-08',)], ['dt'])
    >>> time_df.select(unix_timestamp('dt', 'yyyy-MM-dd').alias('unix_time')).collect()
    [Row(unix_time=1428476400)]
    >>> spark.conf.unset("spark.sql.session.timeZone")
    """
    sc = SparkContext._active_spark_context
    if timestamp is None:
        return Column(sc._jvm.functions.unix_timestamp())
    return Column(sc._jvm.functions.unix_timestamp(_to_java_column(timestamp), format))


@since(1.5)
def from_utc_timestamp(timestamp, tz):
    """
    This is a common function for databases supporting TIMESTAMP WITHOUT TIMEZONE. This function
    takes a timestamp which is timezone-agnostic, and interprets it as a timestamp in UTC, and
    renders that timestamp as a timestamp in the given time zone.

    However, timestamp in Spark represents number of microseconds from the Unix epoch, which is not
    timezone-agnostic. So in Spark this function just shift the timestamp value from UTC timezone to
    the given timezone.

    This function may return confusing result if the input is a string with timezone, e.g.
    '2018-03-13T06:18:23+00:00'. The reason is that, Spark firstly cast the string to timestamp
    according to the timezone in the string, and finally display the result by converting the
    timestamp to string according to the session local timezone.

    :param timestamp: the column that contains timestamps
    :param tz: A string detailing the time zone ID that the input should be adjusted to. It should
               be in the format of either region-based zone IDs or zone offsets. Region IDs must
               have the form 'area/city', such as 'America/Los_Angeles'. Zone offsets must be in
               the format '(+|-)HH:mm', for example '-08:00' or '+01:00'. Also 'UTC' and 'Z' are
               supported as aliases of '+00:00'. Other short names are not recommended to use
               because they can be ambiguous.

    .. versionchanged:: 2.4
       `tz` can take a :class:`Column` containing timezone ID strings.

    >>> df = spark.createDataFrame([('1997-02-28 10:30:00', 'JST')], ['ts', 'tz'])
    >>> df.select(from_utc_timestamp(df.ts, "PST").alias('local_time')).collect()
    [Row(local_time=datetime.datetime(1997, 2, 28, 2, 30))]
    >>> df.select(from_utc_timestamp(df.ts, df.tz).alias('local_time')).collect()
    [Row(local_time=datetime.datetime(1997, 2, 28, 19, 30))]
    """
    sc = SparkContext._active_spark_context
    if isinstance(tz, Column):
        tz = _to_java_column(tz)
    return Column(sc._jvm.functions.from_utc_timestamp(_to_java_column(timestamp), tz))


@since(1.5)
def to_utc_timestamp(timestamp, tz):
    """
    This is a common function for databases supporting TIMESTAMP WITHOUT TIMEZONE. This function
    takes a timestamp which is timezone-agnostic, and interprets it as a timestamp in the given
    timezone, and renders that timestamp as a timestamp in UTC.

    However, timestamp in Spark represents number of microseconds from the Unix epoch, which is not
    timezone-agnostic. So in Spark this function just shift the timestamp value from the given
    timezone to UTC timezone.

    This function may return confusing result if the input is a string with timezone, e.g.
    '2018-03-13T06:18:23+00:00'. The reason is that, Spark firstly cast the string to timestamp
    according to the timezone in the string, and finally display the result by converting the
    timestamp to string according to the session local timezone.

    :param timestamp: the column that contains timestamps
    :param tz: A string detailing the time zone ID that the input should be adjusted to. It should
               be in the format of either region-based zone IDs or zone offsets. Region IDs must
               have the form 'area/city', such as 'America/Los_Angeles'. Zone offsets must be in
               the format '(+|-)HH:mm', for example '-08:00' or '+01:00'. Also 'UTC' and 'Z' are
               supported as aliases of '+00:00'. Other short names are not recommended to use
               because they can be ambiguous.

    .. versionchanged:: 2.4
       `tz` can take a :class:`Column` containing timezone ID strings.

    >>> df = spark.createDataFrame([('1997-02-28 10:30:00', 'JST')], ['ts', 'tz'])
    >>> df.select(to_utc_timestamp(df.ts, "PST").alias('utc_time')).collect()
    [Row(utc_time=datetime.datetime(1997, 2, 28, 18, 30))]
    >>> df.select(to_utc_timestamp(df.ts, df.tz).alias('utc_time')).collect()
    [Row(utc_time=datetime.datetime(1997, 2, 28, 1, 30))]
    """
    sc = SparkContext._active_spark_context
    if isinstance(tz, Column):
        tz = _to_java_column(tz)
    return Column(sc._jvm.functions.to_utc_timestamp(_to_java_column(timestamp), tz))


@since(3.1)
def timestamp_seconds(col):
    """
    >>> from pyspark.sql.functions import timestamp_seconds
    >>> spark.conf.set("spark.sql.session.timeZone", "America/Los_Angeles")
    >>> time_df = spark.createDataFrame([(1230219000,)], ['unix_time'])
    >>> time_df.select(timestamp_seconds(time_df.unix_time).alias('ts')).show()
    +-------------------+
    |                 ts|
    +-------------------+
    |2008-12-25 07:30:00|
    +-------------------+
    >>> spark.conf.unset("spark.sql.session.timeZone")
    """

    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.timestamp_seconds(_to_java_column(col)))


@since(2.0)
def window(timeColumn, windowDuration, slideDuration=None, startTime=None):
    """Bucketize rows into one or more time windows given a timestamp specifying column. Window
    starts are inclusive but the window ends are exclusive, e.g. 12:05 will be in the window
    [12:05,12:10) but not in [12:00,12:05). Windows can support microsecond precision. Windows in
    the order of months are not supported.

    The time column must be of :class:`pyspark.sql.types.TimestampType`.

    Durations are provided as strings, e.g. '1 second', '1 day 12 hours', '2 minutes'. Valid
    interval strings are 'week', 'day', 'hour', 'minute', 'second', 'millisecond', 'microsecond'.
    If the ``slideDuration`` is not provided, the windows will be tumbling windows.

    The startTime is the offset with respect to 1970-01-01 00:00:00 UTC with which to start
    window intervals. For example, in order to have hourly tumbling windows that start 15 minutes
    past the hour, e.g. 12:15-13:15, 13:15-14:15... provide `startTime` as `15 minutes`.

    The output column will be a struct called 'window' by default with the nested columns 'start'
    and 'end', where 'start' and 'end' will be of :class:`pyspark.sql.types.TimestampType`.

    >>> df = spark.createDataFrame([("2016-03-11 09:00:07", 1)]).toDF("date", "val")
    >>> w = df.groupBy(window("date", "5 seconds")).agg(sum("val").alias("sum"))
    >>> w.select(w.window.start.cast("string").alias("start"),
    ...          w.window.end.cast("string").alias("end"), "sum").collect()
    [Row(start='2016-03-11 09:00:05', end='2016-03-11 09:00:10', sum=1)]
    """
    def check_string_field(field, fieldName):
        if not field or type(field) is not str:
            raise TypeError("%s should be provided as a string" % fieldName)

    sc = SparkContext._active_spark_context
    time_col = _to_java_column(timeColumn)
    check_string_field(windowDuration, "windowDuration")
    if slideDuration and startTime:
        check_string_field(slideDuration, "slideDuration")
        check_string_field(startTime, "startTime")
        res = sc._jvm.functions.window(time_col, windowDuration, slideDuration, startTime)
    elif slideDuration:
        check_string_field(slideDuration, "slideDuration")
        res = sc._jvm.functions.window(time_col, windowDuration, slideDuration)
    elif startTime:
        check_string_field(startTime, "startTime")
        res = sc._jvm.functions.window(time_col, windowDuration, windowDuration, startTime)
    else:
        res = sc._jvm.functions.window(time_col, windowDuration)
    return Column(res)


# ---------------------------- misc functions ----------------------------------

@since(1.5)
def crc32(col):
    """
    Calculates the cyclic redundancy check value  (CRC32) of a binary column and
    returns the value as a bigint.

    >>> spark.createDataFrame([('ABC',)], ['a']).select(crc32('a').alias('crc32')).collect()
    [Row(crc32=2743272264)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.crc32(_to_java_column(col)))


@since(1.5)
def md5(col):
    """Calculates the MD5 digest and returns the value as a 32 character hex string.

    >>> spark.createDataFrame([('ABC',)], ['a']).select(md5('a').alias('hash')).collect()
    [Row(hash='902fbdd2b1df0c4f70b4a5d23525e932')]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.md5(_to_java_column(col))
    return Column(jc)


@since(1.5)
def sha1(col):
    """Returns the hex string result of SHA-1.

    >>> spark.createDataFrame([('ABC',)], ['a']).select(sha1('a').alias('hash')).collect()
    [Row(hash='3c01bdbb26f358bab27f267924aa2c9a03fcfdb8')]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.sha1(_to_java_column(col))
    return Column(jc)


@since(1.5)
def sha2(col, numBits):
    """Returns the hex string result of SHA-2 family of hash functions (SHA-224, SHA-256, SHA-384,
    and SHA-512). The numBits indicates the desired bit length of the result, which must have a
    value of 224, 256, 384, 512, or 0 (which is equivalent to 256).

    >>> digests = df.select(sha2(df.name, 256).alias('s')).collect()
    >>> digests[0]
    Row(s='3bc51062973c458d5a6f2d8d64a023246354ad7e064b1e4e009ec8a0699a3043')
    >>> digests[1]
    Row(s='cd9fb1e148ccd8442e5aa74904cc73bf6fb54d1d54d333bd596aa9bb4bb4e961')
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.sha2(_to_java_column(col), numBits)
    return Column(jc)


@since(2.0)
def hash(*cols):
    """Calculates the hash code of given columns, and returns the result as an int column.

    >>> spark.createDataFrame([('ABC',)], ['a']).select(hash('a').alias('hash')).collect()
    [Row(hash=-757602832)]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.hash(_to_seq(sc, cols, _to_java_column))
    return Column(jc)


@since(3.0)
def xxhash64(*cols):
    """Calculates the hash code of given columns using the 64-bit variant of the xxHash algorithm,
    and returns the result as a long column.

    >>> spark.createDataFrame([('ABC',)], ['a']).select(xxhash64('a').alias('hash')).collect()
    [Row(hash=4105715581806190027)]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.xxhash64(_to_seq(sc, cols, _to_java_column))
    return Column(jc)


@since(3.1)
def assert_true(col, errMsg=None):
    """
    Returns null if the input column is true; throws an exception with the provided error message
    otherwise.

    >>> df = spark.createDataFrame([(0,1)], ['a', 'b'])
    >>> df.select(assert_true(df.a < df.b).alias('r')).collect()
    [Row(r=None)]
    >>> df = spark.createDataFrame([(0,1)], ['a', 'b'])
    >>> df.select(assert_true(df.a < df.b, df.a).alias('r')).collect()
    [Row(r=None)]
    >>> df = spark.createDataFrame([(0,1)], ['a', 'b'])
    >>> df.select(assert_true(df.a < df.b, 'error').alias('r')).collect()
    [Row(r=None)]
    """
    sc = SparkContext._active_spark_context
    if errMsg is None:
        return Column(sc._jvm.functions.assert_true(_to_java_column(col)))
    if not isinstance(errMsg, (str, Column)):
        raise TypeError(
            "errMsg should be a Column or a str, got {}".format(type(errMsg))
        )

    errMsg = (
        _create_column_from_literal(errMsg)
        if isinstance(errMsg, str)
        else _to_java_column(errMsg)
    )
    return Column(sc._jvm.functions.assert_true(_to_java_column(col), errMsg))


@since(3.1)
def raise_error(errMsg):
    """
    Throws an exception with the provided error message.
    """
    if not isinstance(errMsg, (str, Column)):
        raise TypeError(
            "errMsg should be a Column or a str, got {}".format(type(errMsg))
        )

    sc = SparkContext._active_spark_context
    errMsg = (
        _create_column_from_literal(errMsg)
        if isinstance(errMsg, str)
        else _to_java_column(errMsg)
    )
    return Column(sc._jvm.functions.raise_error(errMsg))


# ---------------------- String/Binary functions ------------------------------

@since(1.5)
def upper(col):
    """
    Converts a string expression to upper case.
    """
    return _invoke_function_over_column("upper", col)


@since(1.5)
def lower(col):
    """
    Converts a string expression to lower case.
    """
    return _invoke_function_over_column("lower", col)


@since(1.5)
def ascii(col):
    """
    Computes the numeric value of the first character of the string column.
    """
    return _invoke_function_over_column("ascii", col)


@since(1.5)
def base64(col):
    """
    Computes the BASE64 encoding of a binary column and returns it as a string column.
    """
    return _invoke_function_over_column("base64", col)


@since(1.5)
def unbase64(col):
    """
    Decodes a BASE64 encoded string column and returns it as a binary column.
    """
    return _invoke_function_over_column("unbase64", col)


@since(1.5)
def ltrim(col):
    """
    Trim the spaces from left end for the specified string value.
    """
    return _invoke_function_over_column("ltrim", col)


@since(1.5)
def rtrim(col):
    """
    Trim the spaces from right end for the specified string value.
    """
    return _invoke_function_over_column("rtrim", col)


@since(1.5)
def trim(col):
    """
    Trim the spaces from both ends for the specified string column.
    """
    return _invoke_function_over_column("trim", col)


@since(1.5)
def concat_ws(sep, *cols):
    """
    Concatenates multiple input string columns together into a single string column,
    using the given separator.

    >>> df = spark.createDataFrame([('abcd','123')], ['s', 'd'])
    >>> df.select(concat_ws('-', df.s, df.d).alias('s')).collect()
    [Row(s='abcd-123')]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.concat_ws(sep, _to_seq(sc, cols, _to_java_column)))


@since(1.5)
def decode(col, charset):
    """
    Computes the first argument into a string from a binary using the provided character set
    (one of 'US-ASCII', 'ISO-8859-1', 'UTF-8', 'UTF-16BE', 'UTF-16LE', 'UTF-16').
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.decode(_to_java_column(col), charset))


@since(1.5)
def encode(col, charset):
    """
    Computes the first argument into a binary from a string using the provided character set
    (one of 'US-ASCII', 'ISO-8859-1', 'UTF-8', 'UTF-16BE', 'UTF-16LE', 'UTF-16').
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.encode(_to_java_column(col), charset))


@since(1.5)
def format_number(col, d):
    """
    Formats the number X to a format like '#,--#,--#.--', rounded to d decimal places
    with HALF_EVEN round mode, and returns the result as a string.

    :param col: the column name of the numeric value to be formatted
    :param d: the N decimal places

    >>> spark.createDataFrame([(5,)], ['a']).select(format_number('a', 4).alias('v')).collect()
    [Row(v='5.0000')]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.format_number(_to_java_column(col), d))


@since(1.5)
def format_string(format, *cols):
    """
    Formats the arguments in printf-style and returns the result as a string column.

    :param format: string that can contain embedded format tags and used as result column's value
    :param cols: list of column names (string) or list of :class:`Column` expressions to
        be used in formatting

    >>> df = spark.createDataFrame([(5, "hello")], ['a', 'b'])
    >>> df.select(format_string('%d %s', df.a, df.b).alias('v')).collect()
    [Row(v='5 hello')]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.format_string(format, _to_seq(sc, cols, _to_java_column)))


@since(1.5)
def instr(str, substr):
    """
    Locate the position of the first occurrence of substr column in the given string.
    Returns null if either of the arguments are null.

    .. note:: The position is not zero based, but 1 based index. Returns 0 if substr
        could not be found in str.

    >>> df = spark.createDataFrame([('abcd',)], ['s',])
    >>> df.select(instr(df.s, 'b').alias('s')).collect()
    [Row(s=2)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.instr(_to_java_column(str), substr))


@since(3.0)
def overlay(src, replace, pos, len=-1):
    """
    Overlay the specified portion of `src` with `replace`,
    starting from byte position `pos` of `src` and proceeding for `len` bytes.

    >>> df = spark.createDataFrame([("SPARK_SQL", "CORE")], ("x", "y"))
    >>> df.select(overlay("x", "y", 7).alias("overlayed")).show()
    +----------+
    | overlayed|
    +----------+
    |SPARK_CORE|
    +----------+
    """
    if not isinstance(pos, (int, str, Column)):
        raise TypeError(
            "pos should be an integer or a Column / column name, got {}".format(type(pos)))
    if len is not None and not isinstance(len, (int, str, Column)):
        raise TypeError(
            "len should be an integer or a Column / column name, got {}".format(type(len)))

    pos = _create_column_from_literal(pos) if isinstance(pos, int) else _to_java_column(pos)
    len = _create_column_from_literal(len) if isinstance(len, int) else _to_java_column(len)

    sc = SparkContext._active_spark_context

    return Column(sc._jvm.functions.overlay(
        _to_java_column(src),
        _to_java_column(replace),
        pos,
        len
    ))


@since(1.5)
def substring(str, pos, len):
    """
    Substring starts at `pos` and is of length `len` when str is String type or
    returns the slice of byte array that starts at `pos` in byte and is of length `len`
    when str is Binary type.

    .. note:: The position is not zero based, but 1 based index.

    >>> df = spark.createDataFrame([('abcd',)], ['s',])
    >>> df.select(substring(df.s, 1, 2).alias('s')).collect()
    [Row(s='ab')]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.substring(_to_java_column(str), pos, len))


@since(1.5)
def substring_index(str, delim, count):
    """
    Returns the substring from string str before count occurrences of the delimiter delim.
    If count is positive, everything the left of the final delimiter (counting from left) is
    returned. If count is negative, every to the right of the final delimiter (counting from the
    right) is returned. substring_index performs a case-sensitive match when searching for delim.

    >>> df = spark.createDataFrame([('a.b.c.d',)], ['s'])
    >>> df.select(substring_index(df.s, '.', 2).alias('s')).collect()
    [Row(s='a.b')]
    >>> df.select(substring_index(df.s, '.', -3).alias('s')).collect()
    [Row(s='b.c.d')]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.substring_index(_to_java_column(str), delim, count))


@since(1.5)
def levenshtein(left, right):
    """Computes the Levenshtein distance of the two given strings.

    >>> df0 = spark.createDataFrame([('kitten', 'sitting',)], ['l', 'r'])
    >>> df0.select(levenshtein('l', 'r').alias('d')).collect()
    [Row(d=3)]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.levenshtein(_to_java_column(left), _to_java_column(right))
    return Column(jc)


@since(1.5)
def locate(substr, str, pos=1):
    """
    Locate the position of the first occurrence of substr in a string column, after position pos.

    .. note:: The position is not zero based, but 1 based index. Returns 0 if substr
        could not be found in str.

    :param substr: a string
    :param str: a Column of :class:`pyspark.sql.types.StringType`
    :param pos: start position (zero based)

    >>> df = spark.createDataFrame([('abcd',)], ['s',])
    >>> df.select(locate('b', df.s, 1).alias('s')).collect()
    [Row(s=2)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.locate(substr, _to_java_column(str), pos))


@since(1.5)
def lpad(col, len, pad):
    """
    Left-pad the string column to width `len` with `pad`.

    >>> df = spark.createDataFrame([('abcd',)], ['s',])
    >>> df.select(lpad(df.s, 6, '#').alias('s')).collect()
    [Row(s='##abcd')]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.lpad(_to_java_column(col), len, pad))


@since(1.5)
def rpad(col, len, pad):
    """
    Right-pad the string column to width `len` with `pad`.

    >>> df = spark.createDataFrame([('abcd',)], ['s',])
    >>> df.select(rpad(df.s, 6, '#').alias('s')).collect()
    [Row(s='abcd##')]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.rpad(_to_java_column(col), len, pad))


@since(1.5)
def repeat(col, n):
    """
    Repeats a string column n times, and returns it as a new string column.

    >>> df = spark.createDataFrame([('ab',)], ['s',])
    >>> df.select(repeat(df.s, 3).alias('s')).collect()
    [Row(s='ababab')]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.repeat(_to_java_column(col), n))


@since(1.5)
def split(str, pattern, limit=-1):
    """
    Splits str around matches of the given pattern.

    :param str: a string expression to split
    :param pattern: a string representing a regular expression. The regex string should be
        a Java regular expression.
    :param limit: an integer which controls the number of times `pattern` is applied.

        * ``limit > 0``: The resulting array's length will not be more than `limit`, and the
                         resulting array's last entry will contain all input beyond the last
                         matched pattern.
        * ``limit <= 0``: `pattern` will be applied as many times as possible, and the resulting
                          array can be of any size.

    .. versionchanged:: 3.0
       `split` now takes an optional `limit` field. If not provided, default limit value is -1.

    >>> df = spark.createDataFrame([('oneAtwoBthreeC',)], ['s',])
    >>> df.select(split(df.s, '[ABC]', 2).alias('s')).collect()
    [Row(s=['one', 'twoBthreeC'])]
    >>> df.select(split(df.s, '[ABC]', -1).alias('s')).collect()
    [Row(s=['one', 'two', 'three', ''])]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.split(_to_java_column(str), pattern, limit))


@since(1.5)
def regexp_extract(str, pattern, idx):
    r"""Extract a specific group matched by a Java regex, from the specified string column.
    If the regex did not match, or the specified group did not match, an empty string is returned.

    >>> df = spark.createDataFrame([('100-200',)], ['str'])
    >>> df.select(regexp_extract('str', r'(\d+)-(\d+)', 1).alias('d')).collect()
    [Row(d='100')]
    >>> df = spark.createDataFrame([('foo',)], ['str'])
    >>> df.select(regexp_extract('str', r'(\d+)', 1).alias('d')).collect()
    [Row(d='')]
    >>> df = spark.createDataFrame([('aaaac',)], ['str'])
    >>> df.select(regexp_extract('str', '(a+)(b)?(c)', 2).alias('d')).collect()
    [Row(d='')]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.regexp_extract(_to_java_column(str), pattern, idx)
    return Column(jc)


@since(1.5)
def regexp_replace(str, pattern, replacement):
    r"""Replace all substrings of the specified string value that match regexp with rep.

    >>> df = spark.createDataFrame([('100-200',)], ['str'])
    >>> df.select(regexp_replace('str', r'(\d+)', '--').alias('d')).collect()
    [Row(d='-----')]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.regexp_replace(_to_java_column(str), pattern, replacement)
    return Column(jc)


@since(1.5)
def initcap(col):
    """Translate the first letter of each word to upper case in the sentence.

    >>> spark.createDataFrame([('ab cd',)], ['a']).select(initcap("a").alias('v')).collect()
    [Row(v='Ab Cd')]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.initcap(_to_java_column(col)))


@since(1.5)
def soundex(col):
    """
    Returns the SoundEx encoding for a string

    >>> df = spark.createDataFrame([("Peters",),("Uhrbach",)], ['name'])
    >>> df.select(soundex(df.name).alias("soundex")).collect()
    [Row(soundex='P362'), Row(soundex='U612')]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.soundex(_to_java_column(col)))


@since(1.5)
def bin(col):
    """Returns the string representation of the binary value of the given column.

    >>> df.select(bin(df.age).alias('c')).collect()
    [Row(c='10'), Row(c='101')]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.bin(_to_java_column(col))
    return Column(jc)


@since(1.5)
def hex(col):
    """Computes hex value of the given column, which could be :class:`pyspark.sql.types.StringType`,
    :class:`pyspark.sql.types.BinaryType`, :class:`pyspark.sql.types.IntegerType` or
    :class:`pyspark.sql.types.LongType`.

    >>> spark.createDataFrame([('ABC', 3)], ['a', 'b']).select(hex('a'), hex('b')).collect()
    [Row(hex(a)='414243', hex(b)='3')]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.hex(_to_java_column(col))
    return Column(jc)


@since(1.5)
def unhex(col):
    """Inverse of hex. Interprets each pair of characters as a hexadecimal number
    and converts to the byte representation of number.

    >>> spark.createDataFrame([('414243',)], ['a']).select(unhex('a')).collect()
    [Row(unhex(a)=bytearray(b'ABC'))]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.unhex(_to_java_column(col)))


@since(1.5)
def length(col):
    """Computes the character length of string data or number of bytes of binary data.
    The length of character data includes the trailing spaces. The length of binary data
    includes binary zeros.

    >>> spark.createDataFrame([('ABC ',)], ['a']).select(length('a').alias('length')).collect()
    [Row(length=4)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.length(_to_java_column(col)))


@since(1.5)
def translate(srcCol, matching, replace):
    """A function translate any character in the `srcCol` by a character in `matching`.
    The characters in `replace` is corresponding to the characters in `matching`.
    The translate will happen when any character in the string matching with the character
    in the `matching`.

    >>> spark.createDataFrame([('translate',)], ['a']).select(translate('a', "rnlt", "123") \\
    ...     .alias('r')).collect()
    [Row(r='1a2s3ae')]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.translate(_to_java_column(srcCol), matching, replace))


# ---------------------- Collection functions ------------------------------

@since(2.0)
def create_map(*cols):
    """Creates a new map column.

    :param cols: list of column names (string) or list of :class:`Column` expressions that are
        grouped as key-value pairs, e.g. (key1, value1, key2, value2, ...).

    >>> df.select(create_map('name', 'age').alias("map")).collect()
    [Row(map={'Alice': 2}), Row(map={'Bob': 5})]
    >>> df.select(create_map([df.name, df.age]).alias("map")).collect()
    [Row(map={'Alice': 2}), Row(map={'Bob': 5})]
    """
    sc = SparkContext._active_spark_context
    if len(cols) == 1 and isinstance(cols[0], (list, set)):
        cols = cols[0]
    jc = sc._jvm.functions.map(_to_seq(sc, cols, _to_java_column))
    return Column(jc)


@since(2.4)
def map_from_arrays(col1, col2):
    """Creates a new map from two arrays.

    :param col1: name of column containing a set of keys. All elements should not be null
    :param col2: name of column containing a set of values

    >>> df = spark.createDataFrame([([2, 5], ['a', 'b'])], ['k', 'v'])
    >>> df.select(map_from_arrays(df.k, df.v).alias("map")).show()
    +----------------+
    |             map|
    +----------------+
    |{2 -> a, 5 -> b}|
    +----------------+
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.map_from_arrays(_to_java_column(col1), _to_java_column(col2)))


@since(1.4)
def array(*cols):
    """Creates a new array column.

    :param cols: list of column names (string) or list of :class:`Column` expressions that have
        the same data type.

    >>> df.select(array('age', 'age').alias("arr")).collect()
    [Row(arr=[2, 2]), Row(arr=[5, 5])]
    >>> df.select(array([df.age, df.age]).alias("arr")).collect()
    [Row(arr=[2, 2]), Row(arr=[5, 5])]
    """
    sc = SparkContext._active_spark_context
    if len(cols) == 1 and isinstance(cols[0], (list, set)):
        cols = cols[0]
    jc = sc._jvm.functions.array(_to_seq(sc, cols, _to_java_column))
    return Column(jc)


@since(1.5)
def array_contains(col, value):
    """
    Collection function: returns null if the array is null, true if the array contains the
    given value, and false otherwise.

    :param col: name of column containing array
    :param value: value or column to check for in array

    >>> df = spark.createDataFrame([(["a", "b", "c"],), ([],)], ['data'])
    >>> df.select(array_contains(df.data, "a")).collect()
    [Row(array_contains(data, a)=True), Row(array_contains(data, a)=False)]
    >>> df.select(array_contains(df.data, lit("a"))).collect()
    [Row(array_contains(data, a)=True), Row(array_contains(data, a)=False)]
    """
    sc = SparkContext._active_spark_context
    value = value._jc if isinstance(value, Column) else value
    return Column(sc._jvm.functions.array_contains(_to_java_column(col), value))


@since(2.4)
def arrays_overlap(a1, a2):
    """
    Collection function: returns true if the arrays contain any common non-null element; if not,
    returns null if both the arrays are non-empty and any of them contains a null element; returns
    false otherwise.

    >>> df = spark.createDataFrame([(["a", "b"], ["b", "c"]), (["a"], ["b", "c"])], ['x', 'y'])
    >>> df.select(arrays_overlap(df.x, df.y).alias("overlap")).collect()
    [Row(overlap=True), Row(overlap=False)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.arrays_overlap(_to_java_column(a1), _to_java_column(a2)))


@since(2.4)
def slice(x, start, length):
    """
    Collection function: returns an array containing  all the elements in `x` from index `start`
    (array indices start at 1, or from the end if `start` is negative) with the specified `length`.

    :param x: the array to be sliced
    :param start: the starting index
    :param length: the length of the slice

    >>> df = spark.createDataFrame([([1, 2, 3],), ([4, 5],)], ['x'])
    >>> df.select(slice(df.x, 2, 2).alias("sliced")).collect()
    [Row(sliced=[2, 3]), Row(sliced=[5])]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.slice(
        _to_java_column(x),
        start._jc if isinstance(start, Column) else start,
        length._jc if isinstance(length, Column) else length
    ))


@since(2.4)
def array_join(col, delimiter, null_replacement=None):
    """
    Concatenates the elements of `column` using the `delimiter`. Null values are replaced with
    `null_replacement` if set, otherwise they are ignored.

    >>> df = spark.createDataFrame([(["a", "b", "c"],), (["a", None],)], ['data'])
    >>> df.select(array_join(df.data, ",").alias("joined")).collect()
    [Row(joined='a,b,c'), Row(joined='a')]
    >>> df.select(array_join(df.data, ",", "NULL").alias("joined")).collect()
    [Row(joined='a,b,c'), Row(joined='a,NULL')]
    """
    sc = SparkContext._active_spark_context
    if null_replacement is None:
        return Column(sc._jvm.functions.array_join(_to_java_column(col), delimiter))
    else:
        return Column(sc._jvm.functions.array_join(
            _to_java_column(col), delimiter, null_replacement))


@since(1.5)
def concat(*cols):
    """
    Concatenates multiple input columns together into a single column.
    The function works with strings, binary and compatible array columns.

    >>> df = spark.createDataFrame([('abcd','123')], ['s', 'd'])
    >>> df.select(concat(df.s, df.d).alias('s')).collect()
    [Row(s='abcd123')]

    >>> df = spark.createDataFrame([([1, 2], [3, 4], [5]), ([1, 2], None, [3])], ['a', 'b', 'c'])
    >>> df.select(concat(df.a, df.b, df.c).alias("arr")).collect()
    [Row(arr=[1, 2, 3, 4, 5]), Row(arr=None)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.concat(_to_seq(sc, cols, _to_java_column)))


@since(2.4)
def array_position(col, value):
    """
    Collection function: Locates the position of the first occurrence of the given value
    in the given array. Returns null if either of the arguments are null.

    .. note:: The position is not zero based, but 1 based index. Returns 0 if the given
        value could not be found in the array.

    >>> df = spark.createDataFrame([(["c", "b", "a"],), ([],)], ['data'])
    >>> df.select(array_position(df.data, "a")).collect()
    [Row(array_position(data, a)=3), Row(array_position(data, a)=0)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.array_position(_to_java_column(col), value))


@since(2.4)
def element_at(col, extraction):
    """
    Collection function: Returns element of array at given index in extraction if col is array.
    Returns value for the given key in extraction if col is map.

    :param col: name of column containing array or map
    :param extraction: index to check for in array or key to check for in map

    .. note:: The position is not zero based, but 1 based index.

    >>> df = spark.createDataFrame([(["a", "b", "c"],), ([],)], ['data'])
    >>> df.select(element_at(df.data, 1)).collect()
    [Row(element_at(data, 1)='a'), Row(element_at(data, 1)=None)]

    >>> df = spark.createDataFrame([({"a": 1.0, "b": 2.0},), ({},)], ['data'])
    >>> df.select(element_at(df.data, lit("a"))).collect()
    [Row(element_at(data, a)=1.0), Row(element_at(data, a)=None)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.element_at(
        _to_java_column(col), lit(extraction)._jc))


@since(2.4)
def array_remove(col, element):
    """
    Collection function: Remove all elements that equal to element from the given array.

    :param col: name of column containing array
    :param element: element to be removed from the array

    >>> df = spark.createDataFrame([([1, 2, 3, 1, 1],), ([],)], ['data'])
    >>> df.select(array_remove(df.data, 1)).collect()
    [Row(array_remove(data, 1)=[2, 3]), Row(array_remove(data, 1)=[])]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.array_remove(_to_java_column(col), element))


@since(2.4)
def array_distinct(col):
    """
    Collection function: removes duplicate values from the array.

    :param col: name of column or expression

    >>> df = spark.createDataFrame([([1, 2, 3, 2],), ([4, 5, 5, 4],)], ['data'])
    >>> df.select(array_distinct(df.data)).collect()
    [Row(array_distinct(data)=[1, 2, 3]), Row(array_distinct(data)=[4, 5])]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.array_distinct(_to_java_column(col)))


@since(2.4)
def array_intersect(col1, col2):
    """
    Collection function: returns an array of the elements in the intersection of col1 and col2,
    without duplicates.

    :param col1: name of column containing array
    :param col2: name of column containing array

    >>> from pyspark.sql import Row
    >>> df = spark.createDataFrame([Row(c1=["b", "a", "c"], c2=["c", "d", "a", "f"])])
    >>> df.select(array_intersect(df.c1, df.c2)).collect()
    [Row(array_intersect(c1, c2)=['a', 'c'])]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.array_intersect(_to_java_column(col1), _to_java_column(col2)))


@since(2.4)
def array_union(col1, col2):
    """
    Collection function: returns an array of the elements in the union of col1 and col2,
    without duplicates.

    :param col1: name of column containing array
    :param col2: name of column containing array

    >>> from pyspark.sql import Row
    >>> df = spark.createDataFrame([Row(c1=["b", "a", "c"], c2=["c", "d", "a", "f"])])
    >>> df.select(array_union(df.c1, df.c2)).collect()
    [Row(array_union(c1, c2)=['b', 'a', 'c', 'd', 'f'])]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.array_union(_to_java_column(col1), _to_java_column(col2)))


@since(2.4)
def array_except(col1, col2):
    """
    Collection function: returns an array of the elements in col1 but not in col2,
    without duplicates.

    :param col1: name of column containing array
    :param col2: name of column containing array

    >>> from pyspark.sql import Row
    >>> df = spark.createDataFrame([Row(c1=["b", "a", "c"], c2=["c", "d", "a", "f"])])
    >>> df.select(array_except(df.c1, df.c2)).collect()
    [Row(array_except(c1, c2)=['b'])]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.array_except(_to_java_column(col1), _to_java_column(col2)))


@since(1.4)
def explode(col):
    """
    Returns a new row for each element in the given array or map.
    Uses the default column name `col` for elements in the array and
    `key` and `value` for elements in the map unless specified otherwise.

    >>> from pyspark.sql import Row
    >>> eDF = spark.createDataFrame([Row(a=1, intlist=[1,2,3], mapfield={"a": "b"})])
    >>> eDF.select(explode(eDF.intlist).alias("anInt")).collect()
    [Row(anInt=1), Row(anInt=2), Row(anInt=3)]

    >>> eDF.select(explode(eDF.mapfield).alias("key", "value")).show()
    +---+-----+
    |key|value|
    +---+-----+
    |  a|    b|
    +---+-----+
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.explode(_to_java_column(col))
    return Column(jc)


@since(2.1)
def posexplode(col):
    """
    Returns a new row for each element with position in the given array or map.
    Uses the default column name `pos` for position, and `col` for elements in the
    array and `key` and `value` for elements in the map unless specified otherwise.

    >>> from pyspark.sql import Row
    >>> eDF = spark.createDataFrame([Row(a=1, intlist=[1,2,3], mapfield={"a": "b"})])
    >>> eDF.select(posexplode(eDF.intlist)).collect()
    [Row(pos=0, col=1), Row(pos=1, col=2), Row(pos=2, col=3)]

    >>> eDF.select(posexplode(eDF.mapfield)).show()
    +---+---+-----+
    |pos|key|value|
    +---+---+-----+
    |  0|  a|    b|
    +---+---+-----+
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.posexplode(_to_java_column(col))
    return Column(jc)


@since(2.3)
def explode_outer(col):
    """
    Returns a new row for each element in the given array or map.
    Unlike explode, if the array/map is null or empty then null is produced.
    Uses the default column name `col` for elements in the array and
    `key` and `value` for elements in the map unless specified otherwise.

    >>> df = spark.createDataFrame(
    ...     [(1, ["foo", "bar"], {"x": 1.0}), (2, [], {}), (3, None, None)],
    ...     ("id", "an_array", "a_map")
    ... )
    >>> df.select("id", "an_array", explode_outer("a_map")).show()
    +---+----------+----+-----+
    | id|  an_array| key|value|
    +---+----------+----+-----+
    |  1|[foo, bar]|   x|  1.0|
    |  2|        []|null| null|
    |  3|      null|null| null|
    +---+----------+----+-----+

    >>> df.select("id", "a_map", explode_outer("an_array")).show()
    +---+----------+----+
    | id|     a_map| col|
    +---+----------+----+
    |  1|{x -> 1.0}| foo|
    |  1|{x -> 1.0}| bar|
    |  2|        {}|null|
    |  3|      null|null|
    +---+----------+----+
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.explode_outer(_to_java_column(col))
    return Column(jc)


@since(2.3)
def posexplode_outer(col):
    """
    Returns a new row for each element with position in the given array or map.
    Unlike posexplode, if the array/map is null or empty then the row (null, null) is produced.
    Uses the default column name `pos` for position, and `col` for elements in the
    array and `key` and `value` for elements in the map unless specified otherwise.

    >>> df = spark.createDataFrame(
    ...     [(1, ["foo", "bar"], {"x": 1.0}), (2, [], {}), (3, None, None)],
    ...     ("id", "an_array", "a_map")
    ... )
    >>> df.select("id", "an_array", posexplode_outer("a_map")).show()
    +---+----------+----+----+-----+
    | id|  an_array| pos| key|value|
    +---+----------+----+----+-----+
    |  1|[foo, bar]|   0|   x|  1.0|
    |  2|        []|null|null| null|
    |  3|      null|null|null| null|
    +---+----------+----+----+-----+
    >>> df.select("id", "a_map", posexplode_outer("an_array")).show()
    +---+----------+----+----+
    | id|     a_map| pos| col|
    +---+----------+----+----+
    |  1|{x -> 1.0}|   0| foo|
    |  1|{x -> 1.0}|   1| bar|
    |  2|        {}|null|null|
    |  3|      null|null|null|
    +---+----------+----+----+
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.posexplode_outer(_to_java_column(col))
    return Column(jc)


@since(1.6)
def get_json_object(col, path):
    """
    Extracts json object from a json string based on json path specified, and returns json string
    of the extracted json object. It will return null if the input json string is invalid.

    :param col: string column in json format
    :param path: path to the json object to extract

    >>> data = [("1", '''{"f1": "value1", "f2": "value2"}'''), ("2", '''{"f1": "value12"}''')]
    >>> df = spark.createDataFrame(data, ("key", "jstring"))
    >>> df.select(df.key, get_json_object(df.jstring, '$.f1').alias("c0"), \\
    ...                   get_json_object(df.jstring, '$.f2').alias("c1") ).collect()
    [Row(key='1', c0='value1', c1='value2'), Row(key='2', c0='value12', c1=None)]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.get_json_object(_to_java_column(col), path)
    return Column(jc)


@since(1.6)
def json_tuple(col, *fields):
    """Creates a new row for a json column according to the given field names.

    :param col: string column in json format
    :param fields: list of fields to extract

    >>> data = [("1", '''{"f1": "value1", "f2": "value2"}'''), ("2", '''{"f1": "value12"}''')]
    >>> df = spark.createDataFrame(data, ("key", "jstring"))
    >>> df.select(df.key, json_tuple(df.jstring, 'f1', 'f2')).collect()
    [Row(key='1', c0='value1', c1='value2'), Row(key='2', c0='value12', c1=None)]
    """
    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.json_tuple(_to_java_column(col), _to_seq(sc, fields))
    return Column(jc)


@since(2.1)
def from_json(col, schema, options={}):
    """
    Parses a column containing a JSON string into a :class:`MapType` with :class:`StringType`
    as keys type, :class:`StructType` or :class:`ArrayType` with
    the specified schema. Returns `null`, in the case of an unparseable string.

    :param col: string column in json format
    :param schema: a StructType or ArrayType of StructType to use when parsing the json column.
    :param options: options to control parsing. accepts the same options as the json datasource

    .. note:: Since Spark 2.3, the DDL-formatted string or a JSON format string is also
              supported for ``schema``.

    >>> from pyspark.sql.types import *
    >>> data = [(1, '''{"a": 1}''')]
    >>> schema = StructType([StructField("a", IntegerType())])
    >>> df = spark.createDataFrame(data, ("key", "value"))
    >>> df.select(from_json(df.value, schema).alias("json")).collect()
    [Row(json=Row(a=1))]
    >>> df.select(from_json(df.value, "a INT").alias("json")).collect()
    [Row(json=Row(a=1))]
    >>> df.select(from_json(df.value, "MAP<STRING,INT>").alias("json")).collect()
    [Row(json={'a': 1})]
    >>> data = [(1, '''[{"a": 1}]''')]
    >>> schema = ArrayType(StructType([StructField("a", IntegerType())]))
    >>> df = spark.createDataFrame(data, ("key", "value"))
    >>> df.select(from_json(df.value, schema).alias("json")).collect()
    [Row(json=[Row(a=1)])]
    >>> schema = schema_of_json(lit('''{"a": 0}'''))
    >>> df.select(from_json(df.value, schema).alias("json")).collect()
    [Row(json=Row(a=None))]
    >>> data = [(1, '''[1, 2, 3]''')]
    >>> schema = ArrayType(IntegerType())
    >>> df = spark.createDataFrame(data, ("key", "value"))
    >>> df.select(from_json(df.value, schema).alias("json")).collect()
    [Row(json=[1, 2, 3])]
    """

    sc = SparkContext._active_spark_context
    if isinstance(schema, DataType):
        schema = schema.json()
    elif isinstance(schema, Column):
        schema = _to_java_column(schema)
    jc = sc._jvm.functions.from_json(_to_java_column(col), schema, _options_to_str(options))
    return Column(jc)


@since(2.1)
def to_json(col, options={}):
    """
    Converts a column containing a :class:`StructType`, :class:`ArrayType` or a :class:`MapType`
    into a JSON string. Throws an exception, in the case of an unsupported type.

    :param col: name of column containing a struct, an array or a map.
    :param options: options to control converting. accepts the same options as the JSON datasource.
                    Additionally the function supports the `pretty` option which enables
                    pretty JSON generation.

    >>> from pyspark.sql import Row
    >>> from pyspark.sql.types import *
    >>> data = [(1, Row(age=2, name='Alice'))]
    >>> df = spark.createDataFrame(data, ("key", "value"))
    >>> df.select(to_json(df.value).alias("json")).collect()
    [Row(json='{"age":2,"name":"Alice"}')]
    >>> data = [(1, [Row(age=2, name='Alice'), Row(age=3, name='Bob')])]
    >>> df = spark.createDataFrame(data, ("key", "value"))
    >>> df.select(to_json(df.value).alias("json")).collect()
    [Row(json='[{"age":2,"name":"Alice"},{"age":3,"name":"Bob"}]')]
    >>> data = [(1, {"name": "Alice"})]
    >>> df = spark.createDataFrame(data, ("key", "value"))
    >>> df.select(to_json(df.value).alias("json")).collect()
    [Row(json='{"name":"Alice"}')]
    >>> data = [(1, [{"name": "Alice"}, {"name": "Bob"}])]
    >>> df = spark.createDataFrame(data, ("key", "value"))
    >>> df.select(to_json(df.value).alias("json")).collect()
    [Row(json='[{"name":"Alice"},{"name":"Bob"}]')]
    >>> data = [(1, ["Alice", "Bob"])]
    >>> df = spark.createDataFrame(data, ("key", "value"))
    >>> df.select(to_json(df.value).alias("json")).collect()
    [Row(json='["Alice","Bob"]')]
    """

    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.to_json(_to_java_column(col), _options_to_str(options))
    return Column(jc)


@since(2.4)
def schema_of_json(json, options={}):
    """
    Parses a JSON string and infers its schema in DDL format.

    :param json: a JSON string or a string literal containing a JSON string.
    :param options: options to control parsing. accepts the same options as the JSON datasource

    .. versionchanged:: 3.0
       It accepts `options` parameter to control schema inferring.

    >>> df = spark.range(1)
    >>> df.select(schema_of_json(lit('{"a": 0}')).alias("json")).collect()
    [Row(json='struct<a:bigint>')]
    >>> schema = schema_of_json('{a: 1}', {'allowUnquotedFieldNames':'true'})
    >>> df.select(schema.alias("json")).collect()
    [Row(json='struct<a:bigint>')]
    """
    if isinstance(json, str):
        col = _create_column_from_literal(json)
    elif isinstance(json, Column):
        col = _to_java_column(json)
    else:
        raise TypeError("schema argument should be a column or string")

    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.schema_of_json(col, _options_to_str(options))
    return Column(jc)


@since(3.0)
def schema_of_csv(csv, options={}):
    """
    Parses a CSV string and infers its schema in DDL format.

    :param col: a CSV string or a string literal containing a CSV string.
    :param options: options to control parsing. accepts the same options as the CSV datasource

    >>> df = spark.range(1)
    >>> df.select(schema_of_csv(lit('1|a'), {'sep':'|'}).alias("csv")).collect()
    [Row(csv='struct<_c0:int,_c1:string>')]
    >>> df.select(schema_of_csv('1|a', {'sep':'|'}).alias("csv")).collect()
    [Row(csv='struct<_c0:int,_c1:string>')]
    """
    if isinstance(csv, str):
        col = _create_column_from_literal(csv)
    elif isinstance(csv, Column):
        col = _to_java_column(csv)
    else:
        raise TypeError("schema argument should be a column or string")

    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.schema_of_csv(col, _options_to_str(options))
    return Column(jc)


@since(3.0)
def to_csv(col, options={}):
    """
    Converts a column containing a :class:`StructType` into a CSV string.
    Throws an exception, in the case of an unsupported type.

    :param col: name of column containing a struct.
    :param options: options to control converting. accepts the same options as the CSV datasource.

    >>> from pyspark.sql import Row
    >>> data = [(1, Row(age=2, name='Alice'))]
    >>> df = spark.createDataFrame(data, ("key", "value"))
    >>> df.select(to_csv(df.value).alias("csv")).collect()
    [Row(csv='2,Alice')]
    """

    sc = SparkContext._active_spark_context
    jc = sc._jvm.functions.to_csv(_to_java_column(col), _options_to_str(options))
    return Column(jc)


@since(1.5)
def size(col):
    """
    Collection function: returns the length of the array or map stored in the column.

    :param col: name of column or expression

    >>> df = spark.createDataFrame([([1, 2, 3],),([1],),([],)], ['data'])
    >>> df.select(size(df.data)).collect()
    [Row(size(data)=3), Row(size(data)=1), Row(size(data)=0)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.size(_to_java_column(col)))


@since(2.4)
def array_min(col):
    """
    Collection function: returns the minimum value of the array.

    :param col: name of column or expression

    >>> df = spark.createDataFrame([([2, 1, 3],), ([None, 10, -1],)], ['data'])
    >>> df.select(array_min(df.data).alias('min')).collect()
    [Row(min=1), Row(min=-1)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.array_min(_to_java_column(col)))


@since(2.4)
def array_max(col):
    """
    Collection function: returns the maximum value of the array.

    :param col: name of column or expression

    >>> df = spark.createDataFrame([([2, 1, 3],), ([None, 10, -1],)], ['data'])
    >>> df.select(array_max(df.data).alias('max')).collect()
    [Row(max=3), Row(max=10)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.array_max(_to_java_column(col)))


@since(1.5)
def sort_array(col, asc=True):
    """
    Collection function: sorts the input array in ascending or descending order according
    to the natural ordering of the array elements. Null elements will be placed at the beginning
    of the returned array in ascending order or at the end of the returned array in descending
    order.

    :param col: name of column or expression

    >>> df = spark.createDataFrame([([2, 1, None, 3],),([1],),([],)], ['data'])
    >>> df.select(sort_array(df.data).alias('r')).collect()
    [Row(r=[None, 1, 2, 3]), Row(r=[1]), Row(r=[])]
    >>> df.select(sort_array(df.data, asc=False).alias('r')).collect()
    [Row(r=[3, 2, 1, None]), Row(r=[1]), Row(r=[])]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.sort_array(_to_java_column(col), asc))


@since(2.4)
def array_sort(col):
    """
    Collection function: sorts the input array in ascending order. The elements of the input array
    must be orderable. Null elements will be placed at the end of the returned array.

    :param col: name of column or expression

    >>> df = spark.createDataFrame([([2, 1, None, 3],),([1],),([],)], ['data'])
    >>> df.select(array_sort(df.data).alias('r')).collect()
    [Row(r=[1, 2, 3, None]), Row(r=[1]), Row(r=[])]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.array_sort(_to_java_column(col)))


@since(2.4)
def shuffle(col):
    """
    Collection function: Generates a random permutation of the given array.

    .. note:: The function is non-deterministic.

    :param col: name of column or expression

    >>> df = spark.createDataFrame([([1, 20, 3, 5],), ([1, 20, None, 3],)], ['data'])
    >>> df.select(shuffle(df.data).alias('s')).collect()  # doctest: +SKIP
    [Row(s=[3, 1, 5, 20]), Row(s=[20, None, 3, 1])]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.shuffle(_to_java_column(col)))


@since(1.5)
def reverse(col):
    """
    Collection function: returns a reversed string or an array with reverse order of elements.

    :param col: name of column or expression

    >>> df = spark.createDataFrame([('Spark SQL',)], ['data'])
    >>> df.select(reverse(df.data).alias('s')).collect()
    [Row(s='LQS krapS')]
    >>> df = spark.createDataFrame([([2, 1, 3],) ,([1],) ,([],)], ['data'])
    >>> df.select(reverse(df.data).alias('r')).collect()
    [Row(r=[3, 1, 2]), Row(r=[1]), Row(r=[])]
     """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.reverse(_to_java_column(col)))


@since(2.4)
def flatten(col):
    """
    Collection function: creates a single array from an array of arrays.
    If a structure of nested arrays is deeper than two levels,
    only one level of nesting is removed.

    :param col: name of column or expression

    >>> df = spark.createDataFrame([([[1, 2, 3], [4, 5], [6]],), ([None, [4, 5]],)], ['data'])
    >>> df.select(flatten(df.data).alias('r')).collect()
    [Row(r=[1, 2, 3, 4, 5, 6]), Row(r=None)]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.flatten(_to_java_column(col)))


@since(2.3)
def map_keys(col):
    """
    Collection function: Returns an unordered array containing the keys of the map.

    :param col: name of column or expression

    >>> from pyspark.sql.functions import map_keys
    >>> df = spark.sql("SELECT map(1, 'a', 2, 'b') as data")
    >>> df.select(map_keys("data").alias("keys")).show()
    +------+
    |  keys|
    +------+
    |[1, 2]|
    +------+
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.map_keys(_to_java_column(col)))


@since(2.3)
def map_values(col):
    """
    Collection function: Returns an unordered array containing the values of the map.

    :param col: name of column or expression

    >>> from pyspark.sql.functions import map_values
    >>> df = spark.sql("SELECT map(1, 'a', 2, 'b') as data")
    >>> df.select(map_values("data").alias("values")).show()
    +------+
    |values|
    +------+
    |[a, b]|
    +------+
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.map_values(_to_java_column(col)))


@since(3.0)
def map_entries(col):
    """
    Collection function: Returns an unordered array of all entries in the given map.

    :param col: name of column or expression

    >>> from pyspark.sql.functions import map_entries
    >>> df = spark.sql("SELECT map(1, 'a', 2, 'b') as data")
    >>> df.select(map_entries("data").alias("entries")).show()
    +----------------+
    |         entries|
    +----------------+
    |[{1, a}, {2, b}]|
    +----------------+
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.map_entries(_to_java_column(col)))


@since(2.4)
def map_from_entries(col):
    """
    Collection function: Returns a map created from the given array of entries.

    :param col: name of column or expression

    >>> from pyspark.sql.functions import map_from_entries
    >>> df = spark.sql("SELECT array(struct(1, 'a'), struct(2, 'b')) as data")
    >>> df.select(map_from_entries("data").alias("map")).show()
    +----------------+
    |             map|
    +----------------+
    |{1 -> a, 2 -> b}|
    +----------------+
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.map_from_entries(_to_java_column(col)))


@since(2.4)
def array_repeat(col, count):
    """
    Collection function: creates an array containing a column repeated count times.

    >>> df = spark.createDataFrame([('ab',)], ['data'])
    >>> df.select(array_repeat(df.data, 3).alias('r')).collect()
    [Row(r=['ab', 'ab', 'ab'])]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.array_repeat(
        _to_java_column(col),
        _to_java_column(count) if isinstance(count, Column) else count
    ))


@since(2.4)
def arrays_zip(*cols):
    """
    Collection function: Returns a merged array of structs in which the N-th struct contains all
    N-th values of input arrays.

    :param cols: columns of arrays to be merged.

    >>> from pyspark.sql.functions import arrays_zip
    >>> df = spark.createDataFrame([(([1, 2, 3], [2, 3, 4]))], ['vals1', 'vals2'])
    >>> df.select(arrays_zip(df.vals1, df.vals2).alias('zipped')).collect()
    [Row(zipped=[Row(vals1=1, vals2=2), Row(vals1=2, vals2=3), Row(vals1=3, vals2=4)])]
    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.arrays_zip(_to_seq(sc, cols, _to_java_column)))


@since(2.4)
def map_concat(*cols):
    """Returns the union of all the given maps.

    :param cols: list of column names (string) or list of :class:`Column` expressions

    >>> from pyspark.sql.functions import map_concat
    >>> df = spark.sql("SELECT map(1, 'a', 2, 'b') as map1, map(3, 'c') as map2")
    >>> df.select(map_concat("map1", "map2").alias("map3")).show(truncate=False)
    +------------------------+
    |map3                    |
    +------------------------+
    |{1 -> a, 2 -> b, 3 -> c}|
    +------------------------+
    """
    sc = SparkContext._active_spark_context
    if len(cols) == 1 and isinstance(cols[0], (list, set)):
        cols = cols[0]
    jc = sc._jvm.functions.map_concat(_to_seq(sc, cols, _to_java_column))
    return Column(jc)


@since(2.4)
def sequence(start, stop, step=None):
    """
    Generate a sequence of integers from `start` to `stop`, incrementing by `step`.
    If `step` is not set, incrementing by 1 if `start` is less than or equal to `stop`,
    otherwise -1.

    >>> df1 = spark.createDataFrame([(-2, 2)], ('C1', 'C2'))
    >>> df1.select(sequence('C1', 'C2').alias('r')).collect()
    [Row(r=[-2, -1, 0, 1, 2])]
    >>> df2 = spark.createDataFrame([(4, -4, -2)], ('C1', 'C2', 'C3'))
    >>> df2.select(sequence('C1', 'C2', 'C3').alias('r')).collect()
    [Row(r=[4, 2, 0, -2, -4])]
    """
    sc = SparkContext._active_spark_context
    if step is None:
        return Column(sc._jvm.functions.sequence(_to_java_column(start), _to_java_column(stop)))
    else:
        return Column(sc._jvm.functions.sequence(
            _to_java_column(start), _to_java_column(stop), _to_java_column(step)))


@since(3.0)
def from_csv(col, schema, options={}):
    """
    Parses a column containing a CSV string to a row with the specified schema.
    Returns `null`, in the case of an unparseable string.

    :param col: string column in CSV format
    :param schema: a string with schema in DDL format to use when parsing the CSV column.
    :param options: options to control parsing. accepts the same options as the CSV datasource

    >>> data = [("1,2,3",)]
    >>> df = spark.createDataFrame(data, ("value",))
    >>> df.select(from_csv(df.value, "a INT, b INT, c INT").alias("csv")).collect()
    [Row(csv=Row(a=1, b=2, c=3))]
    >>> value = data[0][0]
    >>> df.select(from_csv(df.value, schema_of_csv(value)).alias("csv")).collect()
    [Row(csv=Row(_c0=1, _c1=2, _c2=3))]
    >>> data = [("   abc",)]
    >>> df = spark.createDataFrame(data, ("value",))
    >>> options = {'ignoreLeadingWhiteSpace': True}
    >>> df.select(from_csv(df.value, "s string", options).alias("csv")).collect()
    [Row(csv=Row(s='abc'))]
    """

    sc = SparkContext._active_spark_context
    if isinstance(schema, str):
        schema = _create_column_from_literal(schema)
    elif isinstance(schema, Column):
        schema = _to_java_column(schema)
    else:
        raise TypeError("schema argument should be a column or string")

    jc = sc._jvm.functions.from_csv(_to_java_column(col), schema, _options_to_str(options))
    return Column(jc)


def _unresolved_named_lambda_variable(*name_parts):
    """
    Create `o.a.s.sql.expressions.UnresolvedNamedLambdaVariable`,
    convert it to o.s.sql.Column and wrap in Python `Column`

    :param name_parts: str
    """
    sc = SparkContext._active_spark_context
    name_parts_seq = _to_seq(sc, name_parts)
    expressions = sc._jvm.org.apache.spark.sql.catalyst.expressions
    return Column(
        sc._jvm.Column(
            expressions.UnresolvedNamedLambdaVariable(name_parts_seq)
        )
    )


def _get_lambda_parameters(f):
    import inspect

    signature = inspect.signature(f)
    parameters = signature.parameters.values()

    # We should exclude functions that use
    # variable args and keyword argnames
    # as well as keyword only args
    supported_parmeter_types = {
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.POSITIONAL_ONLY,
    }

    # Validate that
    # function arity is between 1 and 3
    if not (1 <= len(parameters) <= 3):
        raise ValueError(
            "f should take between 1 and 3 arguments, but provided function takes {}".format(
                len(parameters)
            )
        )

    # and all arguments can be used as positional
    if not all(p.kind in supported_parmeter_types for p in parameters):
        raise ValueError(
            "f should use only POSITIONAL or POSITIONAL OR KEYWORD arguments"
        )

    return parameters


def _create_lambda(f):
    """
    Create `o.a.s.sql.expressions.LambdaFunction` corresponding
    to transformation described by f

    :param f: A Python of one of the following forms:
            - (Column) -> Column: ...
            - (Column, Column) -> Column: ...
            - (Column, Column, Column) -> Column: ...
    """
    parameters = _get_lambda_parameters(f)

    sc = SparkContext._active_spark_context
    expressions = sc._jvm.org.apache.spark.sql.catalyst.expressions

    argnames = ["x", "y", "z"]
    args = [
        _unresolved_named_lambda_variable(arg) for arg in argnames[: len(parameters)]
    ]

    result = f(*args)

    if not isinstance(result, Column):
        raise ValueError("f should return Column, got {}".format(type(result)))

    jexpr = result._jc.expr()
    jargs = _to_seq(sc, [arg._jc.expr() for arg in args])

    return expressions.LambdaFunction(jexpr, jargs, False)


def _invoke_higher_order_function(name, cols, funs):
    """
    Invokes expression identified by name,
    (relative to ```org.apache.spark.sql.catalyst.expressions``)
    and wraps the result with Column (first Scala one, then Python).

    :param name: Name of the expression
    :param cols: a list of columns
    :param funs: a list of((*Column) -> Column functions.

    :return: a Column
    """
    sc = SparkContext._active_spark_context
    expressions = sc._jvm.org.apache.spark.sql.catalyst.expressions
    expr = getattr(expressions, name)

    jcols = [_to_java_column(col).expr() for col in cols]
    jfuns = [_create_lambda(f) for f in funs]

    return Column(sc._jvm.Column(expr(*jcols + jfuns)))


@since(3.1)
def transform(col, f):
    """
    Returns an array of elements after applying a transformation to each element in the input array.

    :param col: name of column or expression
    :param f: a function that is applied to each element of the input array.
        Can take one of the following forms:

        - Unary ``(x: Column) -> Column: ...``
        - Binary ``(x: Column, i: Column) -> Column...``, where the second argument is
            a 0-based index of the element.

        and can use methods of :class:`pyspark.sql.Column`, functions defined in
        :py:mod:`pyspark.sql.functions` and Scala ``UserDefinedFunctions``.
        Python ``UserDefinedFunctions`` are not supported
        (`SPARK-27052 <https://issues.apache.org/jira/browse/SPARK-27052>`__).

    :return: a :class:`pyspark.sql.Column`

    >>> df = spark.createDataFrame([(1, [1, 2, 3, 4])], ("key", "values"))
    >>> df.select(transform("values", lambda x: x * 2).alias("doubled")).show()
    +------------+
    |     doubled|
    +------------+
    |[2, 4, 6, 8]|
    +------------+

    >>> def alternate(x, i):
    ...     return when(i % 2 == 0, x).otherwise(-x)
    >>> df.select(transform("values", alternate).alias("alternated")).show()
    +--------------+
    |    alternated|
    +--------------+
    |[1, -2, 3, -4]|
    +--------------+
    """
    return _invoke_higher_order_function("ArrayTransform", [col], [f])


@since(3.1)
def exists(col, f):
    """
    Returns whether a predicate holds for one or more elements in the array.

    :param col: name of column or expression
    :param f: an function ``(x: Column) -> Column: ...``  returning the Boolean expression.
        Can use methods of :class:`pyspark.sql.Column`, functions defined in
        :py:mod:`pyspark.sql.functions` and Scala ``UserDefinedFunctions``.
        Python ``UserDefinedFunctions`` are not supported
        (`SPARK-27052 <https://issues.apache.org/jira/browse/SPARK-27052>`__).
    :return: a :class:`pyspark.sql.Column`

    >>> df = spark.createDataFrame([(1, [1, 2, 3, 4]), (2, [3, -1, 0])],("key", "values"))
    >>> df.select(exists("values", lambda x: x < 0).alias("any_negative")).show()
    +------------+
    |any_negative|
    +------------+
    |       false|
    |        true|
    +------------+
    """
    return _invoke_higher_order_function("ArrayExists", [col], [f])


@since(3.1)
def forall(col, f):
    """
    Returns whether a predicate holds for every element in the array.

    :param col: name of column or expression
    :param f: an function ``(x: Column) -> Column: ...``  returning the Boolean expression.
        Can use methods of :class:`pyspark.sql.Column`, functions defined in
        :py:mod:`pyspark.sql.functions` and Scala ``UserDefinedFunctions``.
        Python ``UserDefinedFunctions`` are not supported
        (`SPARK-27052 <https://issues.apache.org/jira/browse/SPARK-27052>`__).
    :return: a :class:`pyspark.sql.Column`

    >>> df = spark.createDataFrame(
    ...     [(1, ["bar"]), (2, ["foo", "bar"]), (3, ["foobar", "foo"])],
    ...     ("key", "values")
    ... )
    >>> df.select(forall("values", lambda x: x.rlike("foo")).alias("all_foo")).show()
    +-------+
    |all_foo|
    +-------+
    |  false|
    |  false|
    |   true|
    +-------+
    """
    return _invoke_higher_order_function("ArrayForAll", [col], [f])


@since(3.1)
def filter(col, f):
    """
    Returns an array of elements for which a predicate holds in a given array.

    :param col: name of column or expression
    :param f: A function that returns the Boolean expression.
        Can take one of the following forms:

        - Unary ``(x: Column) -> Column: ...``
        - Binary ``(x: Column, i: Column) -> Column...``, where the second argument is
            a 0-based index of the element.

        and can use methods of :class:`pyspark.sql.Column`, functions defined in
        :py:mod:`pyspark.sql.functions` and Scala ``UserDefinedFunctions``.
        Python ``UserDefinedFunctions`` are not supported
        (`SPARK-27052 <https://issues.apache.org/jira/browse/SPARK-27052>`__).

    :return: a :class:`pyspark.sql.Column`

    >>> df = spark.createDataFrame(
    ...     [(1, ["2018-09-20",  "2019-02-03", "2019-07-01", "2020-06-01"])],
    ...     ("key", "values")
    ... )
    >>> def after_second_quarter(x):
    ...     return month(to_date(x)) > 6
    >>> df.select(
    ...     filter("values", after_second_quarter).alias("after_second_quarter")
    ... ).show(truncate=False)
    +------------------------+
    |after_second_quarter    |
    +------------------------+
    |[2018-09-20, 2019-07-01]|
    +------------------------+
    """
    return _invoke_higher_order_function("ArrayFilter", [col], [f])


@since(3.1)
def aggregate(col, zero, merge, finish=None):
    """
    Applies a binary operator to an initial state and all elements in the array,
    and reduces this to a single state. The final state is converted into the final result
    by applying a finish function.

    Both functions can use methods of :class:`pyspark.sql.Column`, functions defined in
    :py:mod:`pyspark.sql.functions` and Scala ``UserDefinedFunctions``.
    Python ``UserDefinedFunctions`` are not supported
    (`SPARK-27052 <https://issues.apache.org/jira/browse/SPARK-27052>`__).

    :param col: name of column or expression
    :param zero: initial value. Name of column or expression
    :param merge: a binary function ``(acc: Column, x: Column) -> Column...`` returning expression
        of the same type as ``zero``
    :param finish: an optional unary function ``(x: Column) -> Column: ...``
        used to convert accumulated value.
    :return: a :class:`pyspark.sql.Column`

    >>> df = spark.createDataFrame([(1, [20.0, 4.0, 2.0, 6.0, 10.0])], ("id", "values"))
    >>> df.select(aggregate("values", lit(0.0), lambda acc, x: acc + x).alias("sum")).show()
    +----+
    | sum|
    +----+
    |42.0|
    +----+

    >>> def merge(acc, x):
    ...     count = acc.count + 1
    ...     sum = acc.sum + x
    ...     return struct(count.alias("count"), sum.alias("sum"))
    >>> df.select(
    ...     aggregate(
    ...         "values",
    ...         struct(lit(0).alias("count"), lit(0.0).alias("sum")),
    ...         merge,
    ...         lambda acc: acc.sum / acc.count,
    ...     ).alias("mean")
    ... ).show()
    +----+
    |mean|
    +----+
    | 8.4|
    +----+
    """
    if finish is not None:
        return _invoke_higher_order_function(
            "ArrayAggregate",
            [col, zero],
            [merge, finish]
        )

    else:
        return _invoke_higher_order_function(
            "ArrayAggregate",
            [col, zero],
            [merge]
        )


@since(3.1)
def zip_with(col1, col2, f):
    """
    Merge two given arrays, element-wise, into a single array using a function.
    If one array is shorter, nulls are appended at the end to match the length of the longer
    array, before applying the function.

    :param col1: name of the first column or expression
    :param col2: name of the second column or expression
    :param f: a binary function ``(x1: Column, x2: Column) -> Column...``
        Can use methods of :class:`pyspark.sql.Column`, functions defined in
        :py:mod:`pyspark.sql.functions` and Scala ``UserDefinedFunctions``.
        Python ``UserDefinedFunctions`` are not supported
        (`SPARK-27052 <https://issues.apache.org/jira/browse/SPARK-27052>`__).
    :return: a :class:`pyspark.sql.Column`

    >>> df = spark.createDataFrame([(1, [1, 3, 5, 8], [0, 2, 4, 6])], ("id", "xs", "ys"))
    >>> df.select(zip_with("xs", "ys", lambda x, y: x ** y).alias("powers")).show(truncate=False)
    +---------------------------+
    |powers                     |
    +---------------------------+
    |[1.0, 9.0, 625.0, 262144.0]|
    +---------------------------+

    >>> df = spark.createDataFrame([(1, ["foo", "bar"], [1, 2, 3])], ("id", "xs", "ys"))
    >>> df.select(zip_with("xs", "ys", lambda x, y: concat_ws("_", x, y)).alias("xs_ys")).show()
    +-----------------+
    |            xs_ys|
    +-----------------+
    |[foo_1, bar_2, 3]|
    +-----------------+
    """
    return _invoke_higher_order_function("ZipWith", [col1, col2], [f])


@since(3.1)
def transform_keys(col, f):
    """
    Applies a function to every key-value pair in a map and returns
    a map with the results of those applications as the new keys for the pairs.

    :param col: name of column or expression
    :param f: a binary function ``(k: Column, v: Column) -> Column...``
        Can use methods of :class:`pyspark.sql.Column`, functions defined in
        :py:mod:`pyspark.sql.functions` and Scala ``UserDefinedFunctions``.
        Python ``UserDefinedFunctions`` are not supported
        (`SPARK-27052 <https://issues.apache.org/jira/browse/SPARK-27052>`__).
    :return: a :class:`pyspark.sql.Column`

    >>> df = spark.createDataFrame([(1, {"foo": -2.0, "bar": 2.0})], ("id", "data"))
    >>> df.select(transform_keys(
    ...     "data", lambda k, _: upper(k)).alias("data_upper")
    ... ).show(truncate=False)
    +-------------------------+
    |data_upper               |
    +-------------------------+
    |{BAR -> 2.0, FOO -> -2.0}|
    +-------------------------+
    """
    return _invoke_higher_order_function("TransformKeys", [col], [f])


@since(3.1)
def transform_values(col, f):
    """
    Applies a function to every key-value pair in a map and returns
    a map with the results of those applications as the new values for the pairs.

    :param col: name of column or expression
    :param f: a binary function ``(k: Column, v: Column) -> Column...``
        Can use methods of :class:`pyspark.sql.Column`, functions defined in
        :py:mod:`pyspark.sql.functions` and Scala ``UserDefinedFunctions``.
        Python ``UserDefinedFunctions`` are not supported
        (`SPARK-27052 <https://issues.apache.org/jira/browse/SPARK-27052>`__).
    :return: a :class:`pyspark.sql.Column`

    >>> df = spark.createDataFrame([(1, {"IT": 10.0, "SALES": 2.0, "OPS": 24.0})], ("id", "data"))
    >>> df.select(transform_values(
    ...     "data", lambda k, v: when(k.isin("IT", "OPS"), v + 10.0).otherwise(v)
    ... ).alias("new_data")).show(truncate=False)
    +---------------------------------------+
    |new_data                               |
    +---------------------------------------+
    |{OPS -> 34.0, IT -> 20.0, SALES -> 2.0}|
    +---------------------------------------+
    """
    return _invoke_higher_order_function("TransformValues", [col], [f])


@since(3.1)
def map_filter(col, f):
    """
    Returns a map whose key-value pairs satisfy a predicate.

    :param col: name of column or expression
    :param f: a binary function ``(k: Column, v: Column) -> Column...``
        Can use methods of :class:`pyspark.sql.Column`, functions defined in
        :py:mod:`pyspark.sql.functions` and Scala ``UserDefinedFunctions``.
        Python ``UserDefinedFunctions`` are not supported
        (`SPARK-27052 <https://issues.apache.org/jira/browse/SPARK-27052>`__).
    :return: a :class:`pyspark.sql.Column`

    >>> df = spark.createDataFrame([(1, {"foo": 42.0, "bar": 1.0, "baz": 32.0})], ("id", "data"))
    >>> df.select(map_filter(
    ...     "data", lambda _, v: v > 30.0).alias("data_filtered")
    ... ).show(truncate=False)
    +--------------------------+
    |data_filtered             |
    +--------------------------+
    |{baz -> 32.0, foo -> 42.0}|
    +--------------------------+
    """
    return _invoke_higher_order_function("MapFilter", [col], [f])


@since(3.1)
def map_zip_with(col1, col2, f):
    """
    Merge two given maps, key-wise into a single map using a function.

    :param col1: name of the first column or expression
    :param col2: name of the second column or expression
    :param f: a ternary function ``(k: Column, v1: Column, v2: Column) -> Column...``
        Can use methods of :class:`pyspark.sql.Column`, functions defined in
        :py:mod:`pyspark.sql.functions` and Scala ``UserDefinedFunctions``.
        Python ``UserDefinedFunctions`` are not supported
        (`SPARK-27052 <https://issues.apache.org/jira/browse/SPARK-27052>`__).
    :return: a :class:`pyspark.sql.Column`

    >>> df = spark.createDataFrame([
    ...     (1, {"IT": 24.0, "SALES": 12.00}, {"IT": 2.0, "SALES": 1.4})],
    ...     ("id", "base", "ratio")
    ... )
    >>> df.select(map_zip_with(
    ...     "base", "ratio", lambda k, v1, v2: round(v1 * v2, 2)).alias("updated_data")
    ... ).show(truncate=False)
    +---------------------------+
    |updated_data               |
    +---------------------------+
    |{SALES -> 16.8, IT -> 48.0}|
    +---------------------------+
    """
    return _invoke_higher_order_function("MapZipWith", [col1, col2], [f])


# ---------------------- Partition transform functions --------------------------------

@since(3.1)
def years(col):
    """
    Partition transform function: A transform for timestamps and dates
    to partition data into years.

    >>> df.writeTo("catalog.db.table").partitionedBy(  # doctest: +SKIP
    ...     years("ts")
    ... ).createOrReplace()

    .. warning::
        This function can be used only in combinatiion with
        :py:meth:`~pyspark.sql.readwriter.DataFrameWriterV2.partitionedBy`
        method of the `DataFrameWriterV2`.

    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.years(_to_java_column(col)))


@since(3.1)
def months(col):
    """
    Partition transform function: A transform for timestamps and dates
    to partition data into months.

    >>> df.writeTo("catalog.db.table").partitionedBy(
    ...     months("ts")
    ... ).createOrReplace()  # doctest: +SKIP

    .. warning::
        This function can be used only in combinatiion with
        :py:meth:`~pyspark.sql.readwriter.DataFrameWriterV2.partitionedBy`
        method of the `DataFrameWriterV2`.

    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.months(_to_java_column(col)))


@since(3.1)
def days(col):
    """
    Partition transform function: A transform for timestamps and dates
    to partition data into days.

    >>> df.writeTo("catalog.db.table").partitionedBy(  # doctest: +SKIP
    ...     days("ts")
    ... ).createOrReplace()

    .. warning::
        This function can be used only in combinatiion with
        :py:meth:`~pyspark.sql.readwriter.DataFrameWriterV2.partitionedBy`
        method of the `DataFrameWriterV2`.

    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.days(_to_java_column(col)))


@since(3.1)
def hours(col):
    """
    Partition transform function: A transform for timestamps
    to partition data into hours.

    >>> df.writeTo("catalog.db.table").partitionedBy(   # doctest: +SKIP
    ...     hours("ts")
    ... ).createOrReplace()

    .. warning::
        This function can be used only in combinatiion with
        :py:meth:`~pyspark.sql.readwriter.DataFrameWriterV2.partitionedBy`
        method of the `DataFrameWriterV2`.

    """
    sc = SparkContext._active_spark_context
    return Column(sc._jvm.functions.hours(_to_java_column(col)))


@since(3.1)
def bucket(numBuckets, col):
    """
    Partition transform function: A transform for any type that partitions
    by a hash of the input column.

    >>> df.writeTo("catalog.db.table").partitionedBy(  # doctest: +SKIP
    ...     bucket(42, "ts")
    ... ).createOrReplace()

    .. warning::
        This function can be used only in combination with
        :py:meth:`~pyspark.sql.readwriter.DataFrameWriterV2.partitionedBy`
        method of the `DataFrameWriterV2`.

    """
    if not isinstance(numBuckets, (int, Column)):
        raise TypeError(
            "numBuckets should be a Column or an int, got {}".format(type(numBuckets))
        )

    sc = SparkContext._active_spark_context
    numBuckets = (
        _create_column_from_literal(numBuckets)
        if isinstance(numBuckets, int)
        else _to_java_column(numBuckets)
    )
    return Column(sc._jvm.functions.bucket(numBuckets, _to_java_column(col)))


# ---------------------------- User Defined Function ----------------------------------

@since(1.3)
def udf(f=None, returnType=StringType()):
    """Creates a user defined function (UDF).

    .. note:: The user-defined functions are considered deterministic by default. Due to
        optimization, duplicate invocations may be eliminated or the function may even be invoked
        more times than it is present in the query. If your function is not deterministic, call
        `asNondeterministic` on the user defined function. E.g.:

    >>> from pyspark.sql.types import IntegerType
    >>> import random
    >>> random_udf = udf(lambda: int(random.random() * 100), IntegerType()).asNondeterministic()

    .. note:: The user-defined functions do not support conditional expressions or short circuiting
        in boolean expressions and it ends up with being executed all internally. If the functions
        can fail on special rows, the workaround is to incorporate the condition into the functions.

    .. note:: The user-defined functions do not take keyword arguments on the calling side.

    :param f: python function if used as a standalone function
    :param returnType: the return type of the user-defined function. The value can be either a
        :class:`pyspark.sql.types.DataType` object or a DDL-formatted type string.

    >>> from pyspark.sql.types import IntegerType
    >>> slen = udf(lambda s: len(s), IntegerType())
    >>> @udf
    ... def to_upper(s):
    ...     if s is not None:
    ...         return s.upper()
    ...
    >>> @udf(returnType=IntegerType())
    ... def add_one(x):
    ...     if x is not None:
    ...         return x + 1
    ...
    >>> df = spark.createDataFrame([(1, "John Doe", 21)], ("id", "name", "age"))
    >>> df.select(slen("name").alias("slen(name)"), to_upper("name"), add_one("age")).show()
    +----------+--------------+------------+
    |slen(name)|to_upper(name)|add_one(age)|
    +----------+--------------+------------+
    |         8|      JOHN DOE|          22|
    +----------+--------------+------------+
    """

    # The following table shows most of Python data and SQL type conversions in normal UDFs that
    # are not yet visible to the user. Some of behaviors are buggy and might be changed in the near
    # future. The table might have to be eventually documented externally.
    # Please see SPARK-28131's PR to see the codes in order to generate the table below.
    #
    # +-----------------------------+--------------+----------+------+---------------+--------------------+-----------------------------+----------+----------------------+---------+--------------------+----------------------------+------------+--------------+------------------+----------------------+  # noqa
    # |SQL Type \ Python Value(Type)|None(NoneType)|True(bool)|1(int)|         a(str)|    1970-01-01(date)|1970-01-01 00:00:00(datetime)|1.0(float)|array('i', [1])(array)|[1](list)|         (1,)(tuple)|bytearray(b'ABC')(bytearray)|  1(Decimal)|{'a': 1}(dict)|Row(kwargs=1)(Row)|Row(namedtuple=1)(Row)|  # noqa
    # +-----------------------------+--------------+----------+------+---------------+--------------------+-----------------------------+----------+----------------------+---------+--------------------+----------------------------+------------+--------------+------------------+----------------------+  # noqa
    # |                      boolean|          None|      True|  None|           None|                None|                         None|      None|                  None|     None|                None|                        None|        None|          None|                 X|                     X|  # noqa
    # |                      tinyint|          None|      None|     1|           None|                None|                         None|      None|                  None|     None|                None|                        None|        None|          None|                 X|                     X|  # noqa
    # |                     smallint|          None|      None|     1|           None|                None|                         None|      None|                  None|     None|                None|                        None|        None|          None|                 X|                     X|  # noqa
    # |                          int|          None|      None|     1|           None|                None|                         None|      None|                  None|     None|                None|                        None|        None|          None|                 X|                     X|  # noqa
    # |                       bigint|          None|      None|     1|           None|                None|                         None|      None|                  None|     None|                None|                        None|        None|          None|                 X|                     X|  # noqa
    # |                       string|          None|    'true'|   '1'|            'a'|'java.util.Gregor...|         'java.util.Gregor...|     '1.0'|         '[I@66cbb73a'|    '[1]'|'[Ljava.lang.Obje...|               '[B@5a51eb1a'|         '1'|       '{a=1}'|                 X|                     X|  # noqa
    # |                         date|          None|         X|     X|              X|datetime.date(197...|         datetime.date(197...|         X|                     X|        X|                   X|                           X|           X|             X|                 X|                     X|  # noqa
    # |                    timestamp|          None|         X|     X|              X|                   X|         datetime.datetime...|         X|                     X|        X|                   X|                           X|           X|             X|                 X|                     X|  # noqa
    # |                        float|          None|      None|  None|           None|                None|                         None|       1.0|                  None|     None|                None|                        None|        None|          None|                 X|                     X|  # noqa
    # |                       double|          None|      None|  None|           None|                None|                         None|       1.0|                  None|     None|                None|                        None|        None|          None|                 X|                     X|  # noqa
    # |                   array<int>|          None|      None|  None|           None|                None|                         None|      None|                   [1]|      [1]|                 [1]|                [65, 66, 67]|        None|          None|                 X|                     X|  # noqa
    # |                       binary|          None|      None|  None|bytearray(b'a')|                None|                         None|      None|                  None|     None|                None|           bytearray(b'ABC')|        None|          None|                 X|                     X|  # noqa
    # |                decimal(10,0)|          None|      None|  None|           None|                None|                         None|      None|                  None|     None|                None|                        None|Decimal('1')|          None|                 X|                     X|  # noqa
    # |              map<string,int>|          None|      None|  None|           None|                None|                         None|      None|                  None|     None|                None|                        None|        None|      {'a': 1}|                 X|                     X|  # noqa
    # |               struct<_1:int>|          None|         X|     X|              X|                   X|                            X|         X|                     X|Row(_1=1)|           Row(_1=1)|                           X|           X|  Row(_1=None)|         Row(_1=1)|             Row(_1=1)|  # noqa
    # +-----------------------------+--------------+----------+------+---------------+--------------------+-----------------------------+----------+----------------------+---------+--------------------+----------------------------+------------+--------------+------------------+----------------------+  # noqa
    #
    # Note: DDL formatted string is used for 'SQL Type' for simplicity. This string can be
    #       used in `returnType`.
    # Note: The values inside of the table are generated by `repr`.
    # Note: 'X' means it throws an exception during the conversion.
    # Note: Python 3.7.3 is used.

    # decorator @udf, @udf(), @udf(dataType())
    if f is None or isinstance(f, (str, DataType)):
        # If DataType has been passed as a positional argument
        # for decorator use it as a returnType
        return_type = f or returnType
        return functools.partial(_create_udf, returnType=return_type,
                                 evalType=PythonEvalType.SQL_BATCHED_UDF)
    else:
        return _create_udf(f=f, returnType=returnType,
                           evalType=PythonEvalType.SQL_BATCHED_UDF)


def _test():
    import doctest
    from pyspark.sql import Row, SparkSession
    import pyspark.sql.functions
    globs = pyspark.sql.functions.__dict__.copy()
    spark = SparkSession.builder\
        .master("local[4]")\
        .appName("sql.functions tests")\
        .getOrCreate()
    sc = spark.sparkContext
    globs['sc'] = sc
    globs['spark'] = spark
    globs['df'] = spark.createDataFrame([Row(age=2, name='Alice'), Row(age=5, name='Bob')])
    (failure_count, test_count) = doctest.testmod(
        pyspark.sql.functions, globs=globs,
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    spark.stop()
    if failure_count:
        sys.exit(-1)


if __name__ == "__main__":
    _test()