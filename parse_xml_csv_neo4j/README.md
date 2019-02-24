### Parsing pubmed xml to csv 
This parses pubmed medline xml to csv. It downloaded citations from eutilities API to fill in the citation. It goes two steps into the citation chain.

#### How to run:
Using python 3
```
pip install pandas
git clone https://github.com/titipata/pubmed_parser.git
pip install ./pubmed_parser
```

#### Import csv to neo4j sandbox
Go into neo4j_load_sandbox.txt
The queries pull data from S3 and import to neo4j sandbox. Do the following:
- login to sandbox
- copy to neo4j and execute line by line