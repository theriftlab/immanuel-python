import os
import swisseph as swe


swe.set_ephe_path(f'{os.path.dirname(__file__)}{os.sep}resources{os.sep}ephemeris')