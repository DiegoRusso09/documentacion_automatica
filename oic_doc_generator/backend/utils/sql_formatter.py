# =========================================================
# FILE:
# oic_doc_generator/utils/sql_formatter.py
# =========================================================


# =========================================================
# SQL KEYWORDS
# =========================================================

SQL_BREAK_KEYWORDS = [

    "SELECT",
    "FROM",
    "WHERE",
    "GROUP BY",
    "ORDER BY",
    "HAVING",
    "UNION",
    "INNER JOIN",
    "LEFT JOIN",
    "RIGHT JOIN",
    "FULL JOIN",
    "JOIN",
    "ON",
    "AND",
    "OR"
]


# =========================================================
# NORMALIZE SQL SPACES
# =========================================================

def normalize_sql_spaces(
    sql_text
):

    if not sql_text:

        return ""

    sql_text = sql_text.replace(
        "\r",
        "\n"
    )

    lines = sql_text.split("\n")

    cleaned = []

    for line in lines:

        cleaned.append(
            line.rstrip()
        )

    return "\n".join(cleaned)


# =========================================================
# APPLY BREAKS
# =========================================================

def apply_sql_breaks(
    sql_text
):

    result = sql_text

    # =====================================================
    # LONGEST FIRST
    # =====================================================

    ordered = sorted(

        SQL_BREAK_KEYWORDS,

        key=len,

        reverse=True
    )

    for keyword in ordered:

        result = result.replace(

            f" {keyword} ",

            f"\n{keyword} "
        )

    return result


# =========================================================
# INDENT SQL
# =========================================================

def indent_sql(
    sql_text
):

    lines = sql_text.split("\n")

    result = []

    for line in lines:

        stripped = line.strip()

        upper = stripped.upper()

        indent = ""

        # =================================================
        # CONDITIONS
        # =================================================

        if upper.startswith("AND"):

            indent = "    "

        elif upper.startswith("OR"):

            indent = "    "

        elif upper.startswith("ON"):

            indent = "    "

        elif upper.startswith("--"):

            indent = "    "

        result.append(
            indent + stripped
        )

    return "\n".join(result)


# =========================================================
# BEAUTIFY SQL
# =========================================================

def beautify_sql(
    sql_text
):

    if not sql_text:

        return ""

    # =====================================================
    # NORMALIZE
    # =====================================================

    result = normalize_sql_spaces(
        sql_text
    )

    # =====================================================
    # BREAKS
    # =====================================================

    result = apply_sql_breaks(
        result
    )

    # =====================================================
    # INDENT
    # =====================================================

    result = indent_sql(
        result
    )

    return result.strip()