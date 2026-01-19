import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from etl.insert_event import log_rental_created

# Remplace ceci par un ID réel existant dans ta base PostgreSQL
location_id = 1

log_rental_created(location_id)
