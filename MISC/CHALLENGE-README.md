# Variant Annotation Technical Challenge

**Please read the [Take-home instructions](#take-home-instructions).**


## Introduction

MyOme technical challenges provide an opportunity for a candidate to interact with the MyOme team on
a software engineering task. Our goal is to witness how a candidate thinks through problems,
responds to ambiguity, and delivers usable code.  Challenges also provide the candidate an
opportunity to experience a bit of MyOme culture to drive to simple, pragmatic, and reliable
solutions to computing problems.

No prior knowledge of bioinformatics or sequence variation is necessary. This project provides an
opportunity to discuss the candidate's experience with variant annotation, code architecture, coding
skills and style.  Although the project is conceptually simple, there are many opprtunities to
demonstrate sound engineering skills.  

## The challenge

For this challenge, you will write a command line script that accepts a list of variants, queries the
[Ensembl](https://ensembl.org) REST service for annotations, and outputs a TSV file with selected
annotations. An example Ensembl query and reply are at the bottom of this README.

The result should be a TSV file with these columns:

- `input variant`
- `assembly name`
- `seq_region_name`
- `start`
- `end`
- `most_severe_consequnece`
- `strand`
- `genes`. This column should be derived from the `gene_symbol` field from `transcript_consequences`. See the example JSON below.

The script should be run like this:

```
$ annotate-variants <variants.txt
variant assembly_name   seq_region_name start   end most_severe_consequence strand  genes
NC_000001.11:g.215674515G>A GRCh38  1   215674515   215674515   missense_variant    1   USH2A
⋮
```

## In-Person Interview Discussion

### Sequences and sequence variation

- How are sequences and sequence variants represented? What is HGVS?
- What variant annotation services and sources is the candidate aware of?
- What constitutes a matching variant? What challenges exist with matching variants?

### Code planning and architecture

- How would you structure this code?  What questions occur to you when
  thinking about code structure?  What Python packages or modules would you use?
- The proposed annotation system uses data from a remote REST
  service.  What factors or concerns occur to you when using an external service
  in a production clinical setting?
- Assume that the input is messy: variants might be duplicated, semantically
  invalid, syntactically invalid, or perhaps not variants at all.  How would you handle erroneous variants?
- Ensembl is one of many annotation sources. Suppose we now want to write an internal microservice that aggregates annotations from multiple sources. What
  standards and tools might we use to implement it? How does this change your code structure?  

## Take-home instructions

- You will be invited to <https://github.com/myome-x/tc-variant-annotation/>.  Click the "Use this template" button to make a new repo under your own username. (Don't fork the repo. See [template repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template) for more info.)
- Invite your interviewer as a collaborator to your new repo.
- Create a new branch for your work.
- Write a Python package that implements the functionality discussed above. Use the `variants.txt`
  for development. It is exactly as intended, and intentionally contains some oddities for you to
  consider.
- Use conventional Python repo and code structure and create a package.  You may restructure the template repo files in any way you see fit.
- Write tests using pytest. Your tests should be meaningful and do not need to be exhaustive.
- Edit `README.md`, add the following:
  - Describe the package
  - Explain setup for development and installation
  - Demonstrate the command line use using the variants.txt file included in this repo.  Please
    include the full output, errors, warnings and all.
  - Discuss features, weaknesses, next steps
  - Respond to the questions below
- Create a PR for your branch and invite your interviewer to review it.

## Questions

- Suppose we now want to create a web microservice that accepts a GET
  (or POST) request with the variant in HGVS format and returns the
  annotation as JSON.  What tools or standards would you implement
  this?  How does your code structure change?
- Start-ups and start-up employees must balance quick and satisfactory
  (i.e., good enough) results with more deliberate and reliable
  results. The same is true for code.  You do not have enough time to
  write the ultimate answer to variant annotation. What is important
  to get "right" now and what can be deferred.
- What's the simplest method you can think of to handle cases of
  duplicated variants in the input?
- What optimizations would you pursue in your code if you had time?
  How would you prioritize your effort?

## Ensembl Annotation Sources

An example Ensembl query and edited response is below.  **N.B. Ensembl
has two certs, one of which is old and leads to random failures. Use
http (not https) for now.** The response is also in
`ensembl-sample-response.json`.
  
    $ curl -H "Content-type:application/json" 'http://rest.ensembl.org/vep/human/hgvs/NC_000006.12:g.152387156G>A'
    [
      {
          "allele_string": "G/A",
          "assembly_name": "GRCh38",
          "end": 152387156,
          "most_severe_consequence": "synonymous_variant",
          "seq_region_name": "6",
          "start": 152387156,
          "strand": 1,
          "transcript_consequences": [
            {
                "amino_acids": "Y",
                "biotype": "protein_coding",
                "cdna_end": 8900,
                "cdna_start": 8900,
                "cds_end": 8424,
                "cds_start": 8424,
                "codons": "taC/taT",
                "consequence_terms": [
                  "synonymous_variant"
                ],
                "gene_id": "ENSG00000131018",
                "gene_symbol": "SYNE1",
                "gene_symbol_source": "HGNC",
                "hgnc_id": "HGNC:17089",
                "impact": "LOW",
                "protein_end": 2808,
                "protein_start": 2808,
                "strand": -1,
                "transcript_id": "ENST00000423061",
                "variant_allele": "A"
            },
            {
                "biotype": "retained_intron",
                "cdna_end": 8621,
                "cdna_start": 8621,
                "consequence_terms": [
                  "non_coding_transcript_exon_variant"
                ],
                "gene_id": "ENSG00000131018",
                "gene_symbol": "SYNE1",
                "gene_symbol_source": "HGNC",
                "hgnc_id": "HGNC:17089",
                "impact": "MODIFIER",
                "strand": -1,
                "transcript_id": "ENST00000461872",
                "variant_allele": "A"
            }
          ]
      }
    ]

- [Reece Hart](https://github.com/reece), 2023
