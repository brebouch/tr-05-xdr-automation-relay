import os
from __version__ import VERSION


class Config:
    VERSION = VERSION

    SECRET_KEY = os.environ.get('SECRET_KEY')
    CCT_OBSERVABLE_TYPES = {
        'ip': {}
    }

    CTR_HEADERS = {
        'User-Agent': ('XDR Integrations '
                       '<tr-integrations-support@cisco.com>')
    }

    # Supported types of verdict
    DISPOSITIONS = {
        'clean': (1, 'Clean'),
        'malicious': (2, 'Malicious'),
        'suspicious': (3, 'Suspicious'),
        'common': (4, 'Common'),
        'unknown': (5, 'Unknown')
    } 
