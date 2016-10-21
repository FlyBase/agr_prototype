from intermine.webservice import Service
import mod


class Mouse():
    service = Service("http://www.mousemine.org/mousemine/service")

    @staticmethod
    def gene_href(gene_id):
        return "http://www.informatics.jax.org/marker/" + gene_id

    @staticmethod
    def load_genes(genes):
        query = Mouse.service.new_query("Gene")
        query.add_view(
            "primaryIdentifier", "symbol", "name", "description",
            "sequenceOntologyTerm.name", "organism.shortName",
            "chromosomeLocation.locatedOn.primaryIdentifier",
            "chromosomeLocation.start", "chromosomeLocation.end",
            "chromosomeLocation.strand", "crossReferences.identifier",
            "crossReferences.source.name", "synonyms.value"
        )
        query.add_constraint("organism.shortName", "=", "M. musculus", code = "A")
        query.add_constraint("dataSets.name", "=", "Mouse Gene Catalog from MGI", code = "B")
        query.outerjoin("chromosomeLocation")
        query.outerjoin("chromosomeLocation.locatedOn")
        query.outerjoin("crossReferences")
        query.outerjoin("crossReferences.source")
        query.outerjoin("synonyms")

        print("Fetching gene data from MouseMine...")

        for row in query.rows():
            if row["crossReferences.source.name"]:
                cross_reference_link_type = row["crossReferences.source.name"]
            else:
                cross_reference_link_type = ""

            if row["crossReferences.identifier"]:
                cross_reference_id = row["crossReferences.identifier"]
            else:
                cross_reference_id = ""

            if row["primaryIdentifier"] in genes:
                if row["synonyms.value"] is not None:
                    genes[row["primaryIdentifier"]]["gene_synonyms"].append(row["synonyms.value"])
                elif row["crossReferences.identifier"] is not None:
                    genes[row["primaryIdentifier"]]["external_ids"].append(cross_reference_link_type + " " + cross_reference_id)
                elif row["chromosomes.name"] is not None:
                    genes[row["primaryIdentifier"]]["gene_chromosomes"].append(row["chromosomes.name"])
            else:
                genes[row["primaryIdentifier"]] = {
                    "gene_symbol": row["symbol"],
                    "name": row["name"],
                    "description": row["description"],
                    "gene_synonyms": [row["synonyms.value"]],
                    "gene_type": row["sequenceOntologyTerm.name"],
                    "gene_chromosomes": [row["chromosomeLocation.locatedOn.primaryIdentifier"]],
                    "gene_chromosome_starts": row["chromosomeLocation.start"],
                    "gene_chromosome_ends": row["chromosomeLocation.end"],
                    "gene_chromosome_strand": row["chromosomeLocation.strand"],
                    "external_ids": [cross_reference_link_type + " " + cross_reference_id],
                    "species": "Mus musculus",

                    "gene_biological_process": [],
                    "gene_molecular_function": [],
                    "gene_cellular_component": [],

                    "name_key": row["symbol"],
                    "href": Mouse.gene_href(row["primaryIdentifier"]),
                    "category": "gene"
                }
