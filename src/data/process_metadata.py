import tarfile
from os import listdir
import pandas as pd
 
filename = "WebMining/data/raw/cit-HepTh-abstracts.tar"
 
with tarfile.open(filename, "r") as compressed_file:
    compressed_file.extractall("extracted_tar_folder")

years = listdir('WebMining/data/processed/extracted_tar_folder')
all_papers = []

for year in years:
    year_folder = f"WebMining/data/processed/extracted_tar_folder/{year}"
    year_papers = listdir(year_folder)
    year_paper_paths = [f"WebMining/data/processed/extracted_tar_folder/{year}/{paper}" for paper in year_papers]
    all_papers.extend(year_paper_paths)

print('Number of paper files: ', len(all_papers))

def get_paper_dict(paper_file: str):
    with open(paper_file) as f:
        lines = f.readlines()

    paper_lines = [line.rstrip('\n') for line in lines if len(line)>1]
    paper_blocks = '|'.join(paper_lines).split('\\\\')
    if 'Author' not in paper_blocks[1]:
        paper_blocks[1] = paper_blocks[1] + '|' + paper_blocks[2]

    paper_id = paper_blocks[1].split('|Paper:')[1].split('|From')[0]
    submitter = paper_blocks[1].split('|From:')[1].split('|Date')[0]
    submission_date = paper_blocks[1].split('|Date:')[1].split('|Title')[0]
    title = paper_blocks[1].split('|Title:')[1].split('|Author')[0]
    try:
        authors = paper_blocks[1].split('|Authors:')[1].split('|Com')[0].split('|Rep')[0].split('|Jour')[0]
    except IndexError:
        authors = paper_blocks[1].split('|Author:')[1].split('|Com')[0].split('|Rep')[0].split('|Jour')[0]
    try:
        comments = paper_blocks[1].split('|Comments:')[1].split('|Rep')[0].split('|Jour')[0]
    except IndexError:
        comments = ''
    try:
        report_no = paper_blocks[1].split('|Report-no:')[1].split('|Jour')[0]
    except IndexError:
        report_no = '' 
    try: 
        journal_ref = paper_blocks[1].split('|Journal-ref:')[1]
    except IndexError:
        journal_ref = '' 
    abstract = paper_blocks[-2]

    paper_dict = {
        'paper_id': paper_id.replace('|', ' ').strip(),
        'submitter': submitter.replace('|', ' ').strip(),
        'submission_date': submission_date.replace('|', ' ').strip(),
        'title': title.replace('|', ' ').strip(),
        'authors': authors.replace('|', ' ').strip(),
        'comments': comments.replace('|', ' ').strip(),
        'report_no': report_no.replace('|', ' ').strip(),
        'journal_ref': journal_ref.replace('|', ' ').strip(),
        'abstract': abstract.replace('|', ' ').strip()
    }

    return paper_dict

papers_json = []
papers_with_error = []

for paper_file in all_papers:
    try:
        paper_dict = get_paper_dict(paper_file)
        papers_json.append(paper_dict)
    except:
        papers_with_error.append(paper_file)

print('Number of parsed papers: ', len(papers_json))
print('Number of papers with parsing error: ', len(papers_with_error))

metadata = pd.DataFrame(papers_json)
metadata.to_csv('WebMining/data/processed/metadata.csv')
