import pandas as pd
from pathlib import Path

DATA = Path(r"C:\Users\thiag\Downloads\Fontes Summerjob")
cad_file = list(DATA.glob("*cadastro-unico-2023.csv"))[0]
df = pd.read_csv(cad_file, sep=None, engine='python', encoding='latin1', nrows=5)
print("COLUMNS IN CADASTRO UNICO:", list(df.columns))
