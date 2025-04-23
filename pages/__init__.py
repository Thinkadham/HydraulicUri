from .dashboard import show as show_dashboard
from .create_bill import show as show_create_bill
from .pages.contractors import show as show_contractors
from .pages.works import show as show_works
from .pages.reports import show as show_reports
from .pages.settings import show as show_settings

__all__ = [
    'show_dashboard',
    'show_create_bill',
    'show_contractors',
    'show_works',
    'show_reports',
    'show_settings'
]
