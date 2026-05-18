from .models import FAQ
from .znuny_db import buscar_faqs


def sincronizar():
    rows = buscar_faqs()

    criados = 0
    atualizados = 0

    for row in rows:
        _, created = FAQ.objects.update_or_create(
            znuny_id=row['id'],
            defaults={
                'f_number': row.get('f_number', ''),
                'title': row.get('title', ''),
                'category': row.get('category', ''),
                'keywords': row.get('keywords', '') or '',
                'symptom': row.get('symptom', '') or '',
                'problem': row.get('problem', '') or '',
                'content': row.get('content', '') or '',
            }
        )

        if created:
            criados += 1
        else:
            atualizados += 1

    return criados, atualizados