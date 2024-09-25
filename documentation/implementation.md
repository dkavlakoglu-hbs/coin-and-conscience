# Process notes

## Phase 1

### Goal
Use graph to recreate current website functionality. Ignoring introduction and bibliography pages for now, this means:

- [Artist index](https://www.library.hbs.edu/hc/cc/artistindex.html): list of artist names with links to the works they created/contributed to
- [Topic galleries](https://www.library.hbs.edu/hc/cc/vanityvirtue.html): works grouped by topic, with images and metadata displayed

### Implementation steps

#### Scrape data from current site
- Analyzed HTML of relevant pages to determine structure of artist and work entries
- Wrote [Python script](../scripts/export_coin_and_conscience_site_data.py) to:
    - Download HTML of the relevant pages
    - Parse HTML elements
    - Request work URLs to get redirect targets - at some point since site was created,the images were migrated to a IIIF server (e.g., original URL http://nrs.harvard.edu/urn-3:HBS.BAKER:836614?buttons=y&caption=Historical+Collections,+Baker+Library,+Harvard+Business+School redirects to https://iiif.lib.harvard.edu/manifests/view/ids:3910429)
    - Restructure into [CSV file](../data/coin_and_conscience_data.csv) where each row represents a distinct artist/work/topic combination

#### Reconcile person entries to Wikidata
Got ahead of myself - this is more for the intended Phase 2 - but a convenient way to generate URIs for people. Some ambiguous names that required a bit more research, but all of the artists in the index appear to already have Wikidata entries. CSV file with Wikidata URIs added [here](../ontorefine/coin_and_conscience_data_augmented.csv)

#### Additional data cleaning/reshaping in OntoRefine
Cleaning steps captured in [JSON file](../ontorefine/2242510558023-project-configurations.json) for reproducibility.

Added columns by:
- Pulling out IIIF ID from redirect URL column
- Constructing image URL from IIIF ID
- Pulling out size information from print information
- Converting topic to lower case and replacing whitespace/punctuation for use in topic IRI

Iterative process alongside the RDF mapping (below) - started mapping, realized changes needed to be made to data

#### RDF mapping in OntoRefine
RDF mapping captured in [JSON file](../ontorefine/rdf_mapping.json)

Using schema.org as ontology - no extensions/customizations needed for this initial version. More details on mapping provided below.

Applied mapping, exported [TTL file](../ontorefine/result-triples-v1.ttl)

#### Load RDF into GraphDB repository and generate visualizations

- Created new repository in GraphDB: [coins-and-conscience-v1](http://ec2-44-205-108-244.compute-1.amazonaws.com/repositories/coins-and-conscience-v1)
- Imported TTL file (exported from OntoRefine in previous section)
- Created [new visual graph configuration](http://ec2-44-205-108-244.compute-1.amazonaws.com/graphs-visualizations?config=59dca1baa0dd4fc9ae3688214787f118)
    - Wrote SPARQL query in `Node basics` tab to set node type color, node labels, node descriptions
    - Wrote SPARQL query in `Node extra` tab to enable images to show in node infoboxes for works
- Added https://schema.org/name to Autocomplete index and turned autocomplete on for the repository to allow users to search for entities by name and not just IRIs
- Saved visualization snapshots for easy entry point to graph (e.g., [Philip Galle](http://ec2-44-205-108-244.compute-1.amazonaws.com/graphs-visualizations?saved=2941ed3f4a6544a19228dcd058b14525))

### Ontology development

[Competency questions](../ontology-competency-questions/)

For existing site functionality:

- What are all of the works credited to Artist X?
- What are all of the works about Topic Z?

Additional functionality:

- Who are the artists credited with Work Y?
- What is the topic of Work Y?
- What topics has Artist X covered in their works?
- Who are the artists creating works about Topic Z?

After some exploration of upper ontologies, selected [schema.org](https://schema.org/) to use initially - it's familiar and the classes and properties are easy to understand (compared to, say, BFO), which makes it relatively low effort to get off the ground. For the Phase 1 requirements, there's not even a need to declare custom properties/classes to extend schema.org. 

#### Artist mapping
- Use Wikidata URI as IRI
- Use https://schema.org/Person as the class
- Properties/attributes
    - https://schema.org/name 
        - initially take label as-is from artist index (last name, first name ordering - let typos stand)

#### Artwork mapping
- Use IIIF URL as IRI
- Use https://schema.org/CreativeWork as the class
- Properties/attributes
    - https://schema.org/identifier
        - numeric identifier on current site (i.e., numbers listed in artist index and topic galleries)
    - https://schema.org/name
    - https://schema.org/description
    - https://schema.org/image
    - https://schema.org/url
    - https://schema.org/contributor
        - relationship to artist
        - initially use this for all people, eventually parse out artist info metadata into more specific relationships (e.g., engraver, publisher, original artist)
    - https://schema.org/creditText
    - https://schema.org/size
    - https://schema.org/about
        - relationship to topic

#### Topic mapping
- Construct IRI using <https://librarydata.hbs.edu/coins-and-conscience/> prefix and topic name (lower case, no whitespace)
- Use https://schema.org/DefinedTerm as class
- Properties/attributes
    - https://schema.org/name
