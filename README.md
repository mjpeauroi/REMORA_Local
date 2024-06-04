# REMORA_Local
Local scripts for the Remora system

Running data_pull.py or data_pull_input.py will grab data from the Sofar API and perform conversions to csv and image files.
- data_pull.py has start date, end date, spotter ID, and auth token hard coded in.
- data_pull_input.py asks for these parameters as input when it is run. Dates should be in the form YYYY-MM-DD
Processing functions are found in data_handling.py
