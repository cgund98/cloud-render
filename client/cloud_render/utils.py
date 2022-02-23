"""
Miscellaneous utilities used by the rest of the codebase.
"""

import json
import datetime


class DateTimeEncoder(json.JSONEncoder):
    """Encoder for serializing datetime.datetime objects in JSON"""

    def default(self, o):
        """encode"""
        if isinstance(o, datetime.datetime):
            return str(o)

        return super().default(o)
