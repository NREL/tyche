import pandas as pd


sheets = ['parameters','indices','designs','investments','tranches','parameters','functions','results']
f_name = 'transport_model_data.xlsx'

for s in sheets: 
    out = pd.read_excel(f_name, s)
    out_name = s + '.tsv'
    out.to_csv(out_name, sep='\t', index=False)
    