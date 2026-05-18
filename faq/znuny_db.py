from django.db import connections

QUERY_TIMEOUT_S = 30


def _set_timeout(cursor):
    # MySQL usa MAX_EXECUTION_TIME (ms), MariaDB usa max_statement_time (s)
    try:
        cursor.execute(f"SET SESSION MAX_EXECUTION_TIME = {QUERY_TIMEOUT_S * 1000}")
    except Exception:
        try:
            cursor.execute(f"SET SESSION max_statement_time = {QUERY_TIMEOUT_S}")
        except Exception:
            pass


def buscar_faqs():
    """Retorna todas as FAQs aprovadas do banco Znuny."""
    query = """
        SELECT
            fi.id,
            fi.f_number,
            fi.f_subject    AS title,
            fi.f_keywords   AS keywords,
            fi.f_field1     AS symptom,
            fi.f_field2     AS problem,
            fi.f_field3     AS content,
            fc.name         AS category,
            fi.created,
            fi.changed
        FROM faq_item fi
        LEFT JOIN faq_category fc ON fi.category_id = fc.id
        WHERE fi.approved = 1
        ORDER BY fc.name, fi.f_subject
    """
    with connections['znuny'].cursor() as cursor:
        _set_timeout(cursor)
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]