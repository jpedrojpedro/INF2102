import re
from string import Template
from endpoints.sparql_query import SparqlQuery


class Enrich:
    REGEX_VARIABLE = r"(SELECT\s+|DISTINCT\s+)(\?[a-zA-Z_]+)(\sFROM\s+[a-z<>:\/.]+\s+|\s+WHERE)"
    SPARQL_TEMPLATE = """
        $prefixes
        select distinct $variable ?p ?o
        where {
          { $subquery }
          $variable ?p ?o .
          filter(isLiteral(?o)) .
        }
    """

    def __init__(self, endpoint, question):
        self.endpoint = endpoint
        self.question = question
        self.variable = None
        self.enriched_query = None
        self.results = None

    def apply(self):
        self._set_variable()
        self._set_enriched_query()
        sq = SparqlQuery(self.endpoint, self.enriched_query)
        df = sq.execute()
        self.results = df

    def _set_variable(self):
        result = re.search(self.REGEX_VARIABLE, self.question.query, re.IGNORECASE)
        if result is None:
            return
        self.variable = result.group(2)

    def _set_enriched_query(self):
        template = Template(self.SPARQL_TEMPLATE)
        self.enriched_query = template.substitute(
            prefixes=self.question.display_prefixes(), variable=self.variable, subquery=self.question.query
        )
