from parsing.parse_functions import get_universities
from parsing.config import FOLDER
import pickle


with open(f'{FOLDER}/universities-info.pkl', 'wb') as file:
    pickle.dump(get_universities(), file)
