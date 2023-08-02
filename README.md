# MyOme Variant Annotation Technical Challenge

****

## Set Up

#### Install from PyPi

1. Naviagate to https://pypi.org/project/myome-ensembl-query/0.0.1/.
2. Run `pip install myome-ensembl-query==0.0.1` to install on your local device. I recommend using a **virtual environment** as the package requires `python 3.10`
3. Once downloaded, the command line command is `query_variant`
4. To run a query: `query_variant <absolute file_path>`
   1. file must be a `.txt` file.
   2. `must be absolute path`
   3. run `query_variant <-h>`for help


#### Install from repo

1. Navigate to `./myome_mharleytake_home/dist/myome_ensembl_query-0.0.1-py3-none-any.whl` in repo and copy wheel path
2. run `pip install <wheel_path>`
3. The command line run will be the same as above
   
#### Run using python3

1. Pull down github repo: https://github.com/MGhostHarley/myome_takehome/tree/em_branch.
2. Navigate to `myome_mharleytake_home/myome_ensembl_query/api_calls.py``
3. run `python3 api_calls.py <variant_file_path>`
   1. **Note**: Requires python 3.10, pytest and requests to be installed. I recommend using a virtual environment.
   
#### Ouput

Upon successful completion, a `results` folder will be created with two `.tsv` files: an `output` file and an `error` file. Both will have timestamps to denote the last time they were ran. The `error` file will have any failed api requests.

## Discussion

#### Code Layout

The code is split into three sections:
    1. *Helper functions* that help with basic functionality
    2. *IO* which are functions that deal with file IO
    3. *API* functions that run the actual api calls

#### Code Design
The code can be found: `./myome_mharleytake_home/myome_ensembl_query/api_calls.py` 

After reviewing the problem and doing some preliminary analysis, I thought about creating a *client* class that would handle most of the functionality. I decided instead that a functional approach was the best way to implement this exercise for three reasons:

1. The ease and speed of development
2. The ease and speed of testing
3. Separating the concerns of data from behavior

Separating concerns of data and behavior was particularly attractive because I wasn't initially sure how I would approach some of the problems such as command line arguments, file io and conversion and api calls, so I wanted the flexibility and ease of being able to change one discreet function vs an entire class.

I also leaned heavily on the `ensembl` [rest api documentation](https://rest.ensembl.org/documentation/info/vep_hgvs_get) for the api calls, the `ensembl`   [github repo](https://github.com/Ensembl/ensembl-rest/wiki/Getting-Started#python-helper-functions) for better understanding of the underlying structure of their service: and `ensembl's`  [exception handeling](https://github.com/Ensembl/webvm-deps/blob/f702cc5dee6b85c82adef5e91cadaf447f9c87e4/ensembl-branch-77/ensembl-variation/modules/Bio/EnsEMBL/Variation/DBSQL/VariationFeatureAdaptor.pm#L1804C1-L1805C1) to understand their custom errors.



#### Features
The core feature is taking a file of `variants` and making api calls to see if the variant exists. There are three additional features:

1. Simple rate limiting - ensuring that we do not overload the external server with calls.
2. Timestamp - being able to know and sort the results by when they happned. It also acts as an id
3. Robust error handling
#### Testing
I used pytest for testing. Recognizing the lack of time, I decided to focus the core functionality, which is api calls, found int the `query_ensemble_api` function. I wanted to ensure that it could handle different issues and fail safely. The six tests I wrote were:
1. Checking if the file was empty
2. Checking the behavior of what would happen if the variants didn't exist
3. Checking the that various exceptions were raised when needed, such as:
   1. `HTTP Error`, `ConnectionError`, `TimeoutError`, `RequestError`
   
To run the tests, navigate to `myome_ensembl_query` directory and run `pytest`


#### Weaknesses and Next Steps

One weakness I've identified is that it doesn't couple behavior together that might needed for an api calls. Things like *authentication* are important in general and you do want to tie that behavior to specific set of data. The other issue is that while the functional approach is quick and easy, we might want to be able to allow other people to spin up their own api calls. This would be easier in theory with a `client object` that could manage state and have more configurable options.

**Some next steps I would love to explore:**

1. Being able to take in a variety of file types (`.json, .csv, .xml, .xlsx`)
2. Allowing the user to chose their desired file type output and where the output is created at
3. Supporting more `esnembl` api endpoints and allowing the user to choose which one they need
4. Move away from a bare bones rate limiter and instead to a sliding window implementation
5. Implement additional testing around file io and output.
6. mock api calls instead of using real api calls.
7. Implement dupe checking, and caching


## Questions form Myforme

**Suppose we now want to create a web microservice that accepts a GET (or POST) request with the variant in HGVS format and returns the annotation as JSON. What tools or standards would you implement this? How does your code structure change?**   

I would look to use FAST API for the microservice for three reasons:

1. It's currrently the fastest python service framework
2. It's incredibly lightweight and easy to develop in
3. Being able to design and enforce your REST API schema (its get and response objects) cuts down on the number of bugs, errors and input validation, saving dev time.

For conversion of the `hgvs` format to `json`, I would probably use the standard library's `json` package (`csv` and `pandas` are also good options).

**What's the simplest method you can think of to handle cases of duplicated variants in the input?**

The simplest way to to add each variant to a `been_seen` list and then check a new variant against the list like so:

```
been_seen = []
for variant in variants:
    if variant in been_seen:
        continue

    do_some_api_call(variant)    
    been_seen.append(variant)
```

This, however, is incredibly inefficient. While initially the search space of `been_seen` is effectively `O(1)` because the space is so small, as you continue to add more variants, the search space becomes effectively `O(n^2)` due to the the nested loops(each loop is `O(n)`). This could be incredibly slow if you have a large amount of records.

A better solution would be to sacrifice some space for speed by using a dictionary (hash map) as searching a hashmap is `0(1)`. This would like:

```
been_seen = {}
for variant in variants:
    if variant in been_seen.keys():
        continue

    do_some_api_call(variant)    
    been_seen[variant] = True

```

This significantly speeds up the check for duplicates (run time is `O(n)`), at the expense of space. I lean on the side that always chose speed over space; **disk space is cheap. Time is not**.

**Start-ups and start-up employees must balance quick and satisfactory (i.e., good enough) results with more deliberate and reliable results. The same is true for code. You do not have enough time to write the ultimate answer to variant annotation. What is important to get "right" now and what can be deferred.**


The most important things are:

1. I am able to read in the file type requested, 
2. I am able to make robust api calls that fail safely
3. I am able to return the results in the needed format to be consumed
4. I want to write in a way (composition over inheritance, simple instead of complexity, interfaces over abstract classes) that does not lock me in to a particular way, gives me flexibility to add on new features or change existing functionality as requirements shift

**What optimizations would you pursue in your code if you had time? How would you prioritize your effort?**

The three optimizations I would optimize for are:

1. **Checking dupes** - limits the amount of api calls I have to make.
2. **Better rate limit management** - increasing the efficiency of api calls
3. **Caching**  - Instead of making an api calls, check the local cache, saving time
4. **Concurrent api calls** - Instead of doing api calls sequentially, batching them up.

The priority is on the simplest optimization to the hardest one because the goal is to get the code *good enough*. The easier optimization strategies are quicker to implement and might get me to the the *good enough* place.