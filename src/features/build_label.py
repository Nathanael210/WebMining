import pandas as pd
import numpy as np

PATH_DATES = '../../data/raw/hep-th-slacdates_unzipped.txt'
PATH_CITATION ='../../data/raw/hep-th-citations_unzipped.txt'
PATH_LABEL = '../../data/processed/papers_label.csv'

def read_dates(path):
    df = pd.read_csv(path, sep=' ', header=None, names=['id_paper', 'slac_date'])
    df['slac_date'] = pd.to_datetime(df['slac_date'])
    display(df.head(5))
    return (df)
    
def read_citation(path, df2):
    df1 = pd.read_csv(path, sep=' ', header=None, names=['id_from', 'id_to'])
    # Add dates
    df1 = pd.merge(df1, df2, how="left", left_on='id_from', right_on='id_paper')
    df1 = pd.merge(df1, df2, how="left", left_on='id_to', right_on='id_paper')
    df1.rename(columns={"slac_date_x": "date_from", "slac_date_y": "date_to"}, inplace= True)
    # Select columns
    df1 = df1[['id_from', 'date_from', 'id_to', 'date_to']]
    display(df1.head(5))
    return(df1)
   
def create_label(df1, df2, path, months=3):
    
    # Define variables
    values = [1, 2]
    ls_future_citations = []
    ls_label = []

    # Form main structure with 27,770 papers
    df3 = pd.DataFrame(pd.concat([df1['id_from'], df1['id_to']]), columns=['id_paper'] )
    df3.drop_duplicates(ignore_index=True, inplace = True )
    df3 = pd.merge(df3, df2, how='inner', on='id_paper')

    #Add label
    for index, row in df3.iterrows():
        date_p  = row['slac_date'] + pd.DateOffset(months=months)
        df4 = df1[df1.date_from <= date_p]
        if df4.empty or row['id_paper'] not in df4.id_to.tolist(): # Not citations during those 3 months or not citations for that particular paper
            ls_future_citations.append(0)
            ls_label.append(0)
        else:
            df4 = df4.groupby(['id_to']).count()[['id_from']].reset_index().rename(columns={'id_from':'n_citations'})
            df4['n_citations_p'] = df4.n_citations.rank(pct = True)
            conditions = [(df4.n_citations_p >= 0.67), (df4.n_citations_p >= 0.33) & (df4.n_citations_p < 0.67)]
            df4['label'] = np.select(conditions, values, default=3)
            ls_future_citations.append(df4[df4.id_to == row['id_paper']].iloc[0,1])
            ls_label.append(df4[df4.id_to == row['id_paper']].iloc[0,3])

    df3['n_future_citations'] = ls_future_citations
    df3['label'] = ls_label
    
    df3.to_csv(path, index=False)
    display(df3.head(5))
    
    return (df3)


df_dates = read_dates(PATH_DATES)
df_citation = read_citation(PATH_CITATION, df_dates)
df_papers = create_label(df_citation, df_dates, PATH_LABEL)

