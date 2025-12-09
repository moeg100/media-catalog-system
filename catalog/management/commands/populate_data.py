from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from catalog.models import Patron, Librarian, MediaItem, Checkout, Hold, MediaRequest, ActivityLog

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **kwargs):
        librarian, _ = Librarian.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@library.com'}
        )
        librarian.set_password('admin123')
        librarian.save()
        self.stdout.write(self.style.SUCCESS(f'Librarian: admin / admin123'))
        
        patron1, _ = Patron.objects.get_or_create(
            card_number='LC-100001',
            defaults={
                'name': 'Sarah Johnson',
                'email': 'sarah@example.com',
                'expires_at': timezone.now() + timedelta(days=365)
            }
        )
        patron1.set_pin('1234')
        patron1.save()
        
        patron2, _ = Patron.objects.get_or_create(
            card_number='LC-100002',
            defaults={
                'name': 'Michael Chen',
                'email': 'michael@example.com',
                'expires_at': timezone.now() + timedelta(days=365)
            }
        )
        patron2.set_pin('1234')
        patron2.save()
        
        self.stdout.write(self.style.SUCCESS(f'Patron: LC-100001 / 1234 (Sarah Johnson)'))
        self.stdout.write(self.style.SUCCESS(f'Patron: LC-100002 / 1234 (Michael Chen)'))

        books = [
            {'title': 'The Midnight Library', 'author': 'Matt Haig', 'media_type': 'book', 'barcode': 'BC-000000001', 'genre': 'Fiction', 'description': 'A novel about regret, choices, and the infinite possibilities of life.'},
            {'title': 'Atomic Habits', 'author': 'James Clear', 'media_type': 'book', 'barcode': 'BC-000000002', 'genre': 'Self-Help', 'description': 'An easy & proven way to build good habits & break bad ones.'},
            {'title': 'Project Hail Mary', 'author': 'Andy Weir', 'media_type': 'book', 'barcode': 'BC-000000003', 'genre': 'Science Fiction', 'description': 'A lone astronaut must save Earth from disaster.'},
            {'title': 'Where the Crawdads Sing', 'author': 'Delia Owens', 'media_type': 'book', 'barcode': 'BC-000000004', 'genre': 'Mystery', 'description': 'A murder mystery set in the marshlands of North Carolina.'},
            {'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'media_type': 'book', 'barcode': 'BC-000000005', 'genre': 'Classic', 'description': 'A tale of wealth, decadence, and the American Dream in the 1920s.'},
            {'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'media_type': 'book', 'barcode': 'BC-000000006', 'genre': 'Classic', 'description': 'A story of racial injustice in the Deep South.'},
            {'title': '1984', 'author': 'George Orwell', 'media_type': 'book', 'barcode': 'BC-000000007', 'genre': 'Dystopian', 'description': 'A dystopian novel about totalitarianism and surveillance.'},
            {'title': 'Dune', 'author': 'Frank Herbert', 'media_type': 'book', 'barcode': 'BC-000000008', 'genre': 'Science Fiction', 'description': 'An epic science fiction novel set on the desert planet Arrakis.'},
            {'title': 'Becoming', 'author': 'Michelle Obama', 'media_type': 'audiobook', 'barcode': 'BC-000000009', 'genre': 'Memoir', 'description': 'A memoir by the former First Lady of the United States.'},
            {'title': 'The Dark Knight', 'author': 'Christopher Nolan', 'media_type': 'dvd', 'barcode': 'BC-000000010', 'genre': 'Action', 'description': 'Batman faces his greatest challenge when the Joker terrorizes Gotham.'},
            {'title': 'Inception', 'author': 'Christopher Nolan', 'media_type': 'dvd', 'barcode': 'BC-000000011', 'genre': 'Sci-Fi', 'description': 'A thief who steals secrets from peoples dreams takes on one final job.'},
            {'title': 'Abbey Road', 'author': 'The Beatles', 'media_type': 'cd', 'barcode': 'BC-000000012', 'genre': 'Rock', 'description': 'The eleventh studio album by the Beatles.'},
            {'title': 'Time Magazine', 'author': 'Time Inc.', 'media_type': 'magazine', 'barcode': 'BC-000000013', 'genre': 'News', 'description': 'Weekly news magazine covering current events.'},
            {'title': 'National Geographic', 'author': 'National Geographic Society', 'media_type': 'magazine', 'barcode': 'BC-000000014', 'genre': 'Science', 'description': 'Monthly magazine about nature, science, and culture.'},
            {'title': 'Klara and the Sun', 'author': 'Kazuo Ishiguro', 'media_type': 'book', 'barcode': 'BC-000000015', 'genre': 'Science Fiction', 'description': 'A story about artificial intelligence and love.'},
        ]
        
        for book_data in books:
            MediaItem.objects.get_or_create(
                barcode=book_data['barcode'],
                defaults=book_data
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(books)} media items'))

        item1 = MediaItem.objects.get(barcode='BC-000000001')
        if not Checkout.objects.filter(patron=patron1, media_item=item1, returned_at__isnull=True).exists():
            checkout = Checkout.objects.create(
                patron=patron1,
                media_item=item1,
                due_date=timezone.now() + timedelta(days=14)
            )
            item1.status = 'checked_out'
            item1.save()
            ActivityLog.objects.create(
                action='checkout',
                patron=patron1,
                media_item=item1,
                description=f'Checked out "{item1.title}"'
            )

        item2 = MediaItem.objects.get(barcode='BC-000000002')
        if not Checkout.objects.filter(patron=patron1, media_item=item2, returned_at__isnull=True).exists():
            checkout = Checkout.objects.create(
                patron=patron1,
                media_item=item2,
                due_date=timezone.now() - timedelta(days=5)
            )
            item2.status = 'checked_out'
            item2.save()
            ActivityLog.objects.create(
                action='checkout',
                patron=patron1,
                media_item=item2,
                description=f'Checked out "{item2.title}"'
            )

        item3 = MediaItem.objects.get(barcode='BC-000000003')
        Hold.objects.get_or_create(
            patron=patron1,
            media_item=item3,
            defaults={'queue_position': 1, 'status': 'pending'}
        )

        MediaRequest.objects.get_or_create(
            patron=patron1,
            title='The Silent Patient',
            defaults={
                'author': 'Alex Michaelides',
                'media_type': 'book',
                'reason': 'It was recommended by my book club.',
                'status': 'pending'
            }
        )
        
        MediaRequest.objects.get_or_create(
            patron=patron2,
            title='Dune (2021)',
            defaults={
                'author': 'Denis Villeneuve',
                'media_type': 'dvd',
                'reason': 'I missed it in theaters.',
                'status': 'pending'
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Sample data populated successfully!'))
