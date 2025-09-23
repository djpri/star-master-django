from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from music.models import Genre, Artist, Song


class Command(BaseCommand):
    help = 'Create test data for the music app'

    def handle(self, *args, **options):
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                'admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        else:
            self.stdout.write('Admin user already exists')

        # Create test user
        if not User.objects.filter(username='testuser').exists():
            test_user = User.objects.create_user(
                'testuser', 'test@example.com', 'test123')
            self.stdout.write(self.style.SUCCESS('Created test user'))
        else:
            test_user = User.objects.get(username='testuser')
            self.stdout.write('Test user already exists')

        # Create genres
        rock, created = Genre.objects.get_or_create(name='Rock')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Rock genre'))

        pop, created = Genre.objects.get_or_create(name='Pop')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Pop genre'))

        folk, created = Genre.objects.get_or_create(name='Folk')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Folk genre'))

        # Create artists
        beatles, created = Artist.objects.get_or_create(name='The Beatles')
        if created:
            beatles.genres.add(rock, pop)
            self.stdout.write(self.style.SUCCESS('Created The Beatles artist'))

        dylan, created = Artist.objects.get_or_create(name='Bob Dylan')
        if created:
            dylan.genres.add(folk, rock)
            self.stdout.write(self.style.SUCCESS('Created Bob Dylan artist'))

        # Create songs
        song1, created = Song.objects.get_or_create(
            title='Hey Jude',
            artist=beatles,
            defaults={
                'album_name': 'The Beatles 1967-1970',
                'key': 'F',
                'tempo_bpm': 73,
                'created_by': test_user
            }
        )
        if created:
            song1.genres.add(rock, pop)
            self.stdout.write(self.style.SUCCESS('Created Hey Jude song'))

        song2, created = Song.objects.get_or_create(
            title='Blowin\' in the Wind',
            artist=dylan,
            defaults={
                'album_name': 'The Freewheelin\' Bob Dylan',
                'key': 'G',
                'tempo_bpm': 90,
                'created_by': test_user
            }
        )
        if created:
            song2.genres.add(folk)
            self.stdout.write(self.style.SUCCESS(
                'Created Blowin\' in the Wind song'))

        self.stdout.write(self.style.SUCCESS('Test data creation completed!'))
