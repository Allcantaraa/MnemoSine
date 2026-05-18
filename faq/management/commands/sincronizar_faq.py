from django.core.management.base import BaseCommand
from faq import sync


class Command(BaseCommand):
    help = 'Sincroniza FAQs do Znuny para o banco de dados local'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando sincronização com Znuny...')
        try:
            criados, atualizados = sync.sincronizar()
            self.stdout.write(self.style.SUCCESS(
                f'Concluído: {criados} FAQ(s) criada(s), {atualizados} atualizada(s).'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro: {str(e)}'))