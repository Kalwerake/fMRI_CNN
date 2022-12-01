import os
import pandas as pd
from dfc_functions import DFC
from dfc_functions import PictureThis

phenotype_path = os.path.join(os.getcwd(), 'phenotype_files/pheno_clean.csv')
phenotype_df = pd.read_csv(phenotype_path)

pickle_party = DFC(phenotype_df, 'rois_cc200', 'dfc_cc200')

pickle_party.pickle_jar()
