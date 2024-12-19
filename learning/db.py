import duckdb
from typing import Optional


# con = duckdb.connect(database = "birds.duckdb", read_only = True)

def json_query(query):
    base = """SELECT json_group_array(to_json(row)) as json_data
            FROM (
                {}
            ) row;"""
    return duckdb.sql(base.format(query)).fetchone()[0]

def get_species_locations(species_name: str, limit: Optional[int]=5000):
    ls = ''
    if limit is not None:
        ls = f'LIMIT {limit}'

    query = """SELECT decimalLatitude AS x,
    decimalLongitude AS y,
    eventDate AS t,
    ifnull(individualCount, 1) AS z
    FROM birds.parquet
    WHERE species = '{species}' {ls}""".format(species=species_name, 
                                               ls=ls)

    return duckdb.sql(query)