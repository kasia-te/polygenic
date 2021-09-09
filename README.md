# polygenic

[![PyPI](https://img.shields.io/pypi/v/polygenic.svg)](https://pypi.python.org/pypi/polygenic)
python package for computation of polygenic scores based for particular sample

Index:
- [Installation](#installation)
- [Running](#running)
- [YML models](#building_models_in_yml)
- [Python3 models](#building_models_in_py)
- [Updates](#updates)

## Installation
### Using pip
```
pip3 install --upgrade polygenic
```
### In new conda environment
```
docker run -it conda/miniconda3 /bin/bash
```
```
yes | conda create --name py38 python=3.8
eval "$(conda shell.bash hook)"
conda activate py38
### should be 3.8
python --version

### gcc is missing to build pytabix
apt -qq update
apt -y install build-essential

pip install polygenic
```

## Running
```
polygenic --vcf [your_vcf_gz] --model [your_model] [other raguments]
```
### Arguments
#### Required
- `--vcf` vcf.gz file with genotypes (tabix index should be available)
- `--model` path to model file
#### Optional
- `--log_file` log file
- `--out_dir` directory for result jsons
- `--population` population code
- `--models_path` path to a directory containing models
- `--af` an indexed vcf.gz file containing allele freq data
- `--version` prints version of package

## Building models in yml

Index:
[Model structure](#model_structure)
[Model types](#model_types)
[Parameters](#parameters)
[Example diplotype model](#example_diplotype_model)


### Model structure
##### Core structure
Models have two properties which is `model` and `description`. `model` is a specification of computation to be performed and `description` is additional information to be included in the result.
```
model:
description:
```
##### Object keys
Each object that is not collection has a set of predefined keys (required or optional) that can be used for computation. For example: `diplotype_model` object has a required `diplotypes` key.
```
diplotype_model:
  diplotypes:
```
The computation is first delegated to key specified objects and later aggregated by the top level object itself.
##### Collections
There is special category of objects that don't have predefined keys but are collections. Each key within collection becomes element of collection. Collections are easy to recognize, because they are specified in plural form like `diplotypes` or `variants`. Each element of collection will be defined as singular object of collection type. For example key in `variants` collection will becomes objects of `variant` type.
```
      variants:
        rs7041: {diplotype: C/C}
        rs4588: {diplotype: T/T}
```

### Model types
There are currently implemented four types of models:  
- `score_model`
- `diplotype_model`
- `haplotype_model`
- `formula_model`
The type of model can be specified at the top of yml structure or within the `model` field.  
##### Specification of model type at the top of yml structure
```
diplotype_model:
description:
```
##### Specification of model type within the `model` field
```
model:
  diplotype_model:
description:
```
### Parameters
External parameters can be used in `formula_model` through `@parameters` keyword.  
Example parameters file in `.json` format:
```
{"sex": "F"}
```
Path to file can be provided as argument to polygenic tool:
```
--parameters /path/to/parameters.json
```
Example of use of parameters in the `formula_model`:
```
formula_model:
  formula:
    value: "@female.score_model.value if @parameters.sex == 'F' else @male.score_model.value"
  male:
    score_model:
      variants:
        ...
  female:
    score_model:
      variants:
```
### Example diplotype model
This example diplotype model is based on [Randolph 2014](https://pubmed.ncbi.nlm.nih.gov/24447085/).
```
diplotype_model:
  diplotypes:
    1/1:
      variants:
        rs7041: {diplotype: C/C}
        rs4588: {diplotype: T/T}
    1/1s:
      variants:
        rs7041: {diplotype: C/C}
        rs4588: {diplotype: T/G}
    1/1f:
      variants:
        rs7041: {diplotype: C/A}
        rs4588: {diplotype: T/G}
    1/2:
      variants:
        rs7041: {diplotype: C/A}
        rs4588: {diplotype: T/T}
    1s/1s:
      variants:
        rs7041: {diplotype: C/C}
        rs4588: {diplotype: G/G}
    1s/1f:
      variants: 
        rs7041: {diplotype: C/A}
        rs4588: {diplotype: G/G}
    1s/2:
      variants: 
        rs7041: {diplotype: C/A}
        rs4588: {diplotype: G/T}
    1f/1f: 
      variants: 
        rs7041: {diplotype: A/A}
        rs4588: {diplotype: G/G}
    1f/2: 
      variants: 
        rs7041: {diplotype: A/A}
        rs4588: {diplotype: G/T}
    2/2: 
      variants: 
        rs7041: {diplotype: A/A}
        rs4588: {diplotype: T/T}
description:
  pmid: 24447085
  genes: [GC]
  result_diplotype_choice:
    1/1: Moderate
    1/1s: High
    1/1f: High
    1/2: Low
    1s/1s: Very high
    1s/1f: Very high
    1s/2: Moderate
    1f/1f: Very high
    1f/2: Moderate
    2/2: Very low
```

### Example score model with catgeories rescaling
```
score_model:
  variants:
    rs10012: {effect_allele: G, effect_size: 0.369215857410143}
    rs1014971: {effect_allele: T, effect_size: 0.075546961392531}
    rs10936599: {effect_allele: C, effect_size: 0.086359830674748}
    rs11892031: {effect_allele: C, effect_size: -0.552841968657781}
    rs1495741: {effect_allele: A, effect_size: 0.05307844348342}
    rs17674580: {effect_allele: C, effect_size: 0.187520720836463}
    rs2294008: {effect_allele: T, effect_size: 0.08278537031645}
    rs798766: {effect_allele: T, effect_size: 0.093421685162235}
    rs9642880: {effect_allele: G, effect_size: 0.093421685162235}
  categories:
    High risk: {from: 1.371624087, to: 2.581880425, scale_from: 2, scale_to: 3}
    Potential risk: {from: 1.169616034, to: 1.371624087, scale_from: 1, scale_to: 2}
    Average risk: {from: -0.346748358, to: 1.169616034, scale_from: 0, scale_to: 1}
    Low risk: {from: -1.657132197, to: -0.346748358, scale_from: -1, scale_to: 0}
description:
  about: 
  genes: []
  result_statement_choice:
    Average risk: Avg
    Potential risk: Pot
    High risk: Hig
    Low risk: Low
  science_behind_the_test:
  test_type: Polygenic Risk Score
  trait: Breast cancer
  trait_authors:
    - taken from the PGS catalog
  trait_copyright: Intelliseq all rights reserved
  trait_explained: None
  trait_heritability: None
  trait_pgs_id: PGS000001
  trait_pmids:
    - 25855707
  trait_snp_heritability: None
  trait_title: Breast_Cancer
  trait_version: 1.0
  what_you_can_do_choice:
    Average risk:
    High risk:
    Low risk:
  what_your_result_means_choice:
    Average risk:
    High risk:
    Low risk:
 ```

#### Example Formula Model
```
formula_model:
  formula:
    brownexp: "math.exp(@brown.score_model.value - 2.0769)"
    redexp: "math.exp(@red.score_model.value - 6.3953)"
    blackexp: "math.exp(@black.score_model.value - 2.4029)"
    sumexp: "@brownexp + @redexp + @blackexp"
    brown_prob: "@brownexp / (1 + @sumexp)"
    red_prob: "@redexp / (1 + @sumexp)"
    black_prob: "@blackexp / (1 + @sumexp)"
    blonde_prob: "1 - (@brown_prob + @red_prob + @black_prob)"
  brown:
    score_model:
      variants:
        rs796296176: {effect_allele: CA, effect_size: 1.2522}
        rs11547464: {effect_allele: A, effect_size: -0.61155}
        rs885479: {effect_allele: T, effect_size: 0.2937}
        rs1805008: {effect_allele: T, effect_size: -0.50143}
        rs1805005: {effect_allele: T, effect_size: 0.21172}
        rs1805006: {effect_allele: A, effect_size: 1.9293}
        rs1805007: {effect_allele: T, effect_size: -0.32318}
        rs1805009: {effect_allele: C, effect_size: 0.60861}
        rs1805009: {effect_allele: A, effect_size: 0.25624}
        rs2228479: {effect_allele: A, effect_size: -0.054143}
        rs1110400: {effect_allele: C, effect_size: -0.56315}
        rs28777: {effect_allele: C, effect_size: 0.52168}
        rs16891982: {effect_allele: C, effect_size: 0.75284}
        rs12821256: {effect_allele: G, effect_size: -0.34957}
        rs4959270: {effect_allele: A, effect_size: -0.19171}
        rs12203592: {effect_allele: T, effect_size: 1.6475}
        rs1042602: {effect_allele: T, effect_size: 0.16092}
        rs1800407: {effect_allele: A, effect_size: -0.19111}
        rs2402130: {effect_allele: G, effect_size: 0.35821}
        rs12913832: {effect_allele: T, effect_size: 1.214}
        rs2378249: {effect_allele: C, effect_size: 0.12669}
        rs683: {effect_allele: C, effect_size: 0.21172}
  red:
    score_model:
      variants:
        rs796296176: {effect_allele: CA, effect_size: 25.508}
        rs11547464: {effect_allele: A, effect_size: 2.5381}
        rs885479: {effect_allele: T, effect_size: -0.20889}
        rs1805008: {effect_allele: T, effect_size: 2.801}
        rs1805005: {effect_allele: T, effect_size: 0.93493}
        rs1805006: {effect_allele: A, effect_size: 3.65}
        rs1805007: {effect_allele: T, effect_size: 3.4408}
        rs1805009: {effect_allele: C, effect_size: 4.5868}
        rs1805009: {effect_allele: A, effect_size: 22.107}
        rs2228479: {effect_allele: A, effect_size: 0.62307}
        rs1110400: {effect_allele: C, effect_size: 1.4453}
        rs28777: {effect_allele: C, effect_size: 0.70401}
        rs16891982: {effect_allele: C, effect_size: -0.41869}
        rs12821256: {effect_allele: G, effect_size: -0.57964}
        rs4959270: {effect_allele: A, effect_size: 0.24861}
        rs12203592: {effect_allele: T, effect_size: 0.90233}
        rs1042602: {effect_allele: T, effect_size: 0.45003}
        rs1800407: {effect_allele: A, effect_size: -0.27606}
        rs2402130: {effect_allele: G, effect_size: 0.28313}
        rs12913832: {effect_allele: T, effect_size: -0.093776}
        rs2378249: {effect_allele: C, effect_size: 0.76634}
        rs683: {effect_allele: C, effect_size: -0.053427}
  black:
    score_model:
      variants:
        rs796296176: {effect_allele: CA, effect_size: 2.732}
        rs11547464: {effect_allele: A, effect_size: -16.969}
        rs885479: {effect_allele: T, effect_size: 0.39983}
        rs1805008: {effect_allele: T, effect_size: -0.86062}
        rs1805005: {effect_allele: T, effect_size: -0.0029013}
        rs1805006: {effect_allele: A, effect_size: -16.088}
        rs1805007: {effect_allele: T, effect_size: -1.3757}
        rs1805009: {effect_allele: C, effect_size: 0.060631}
        rs1805009: {effect_allele: A, effect_size: 3.9824}
        rs2228479: {effect_allele: A, effect_size: 0.17012}
        rs1110400: {effect_allele: C, effect_size: 0.29143}
        rs28777: {effect_allele: C, effect_size: 0.82228}
        rs16891982: {effect_allele: C, effect_size: 1.1617}
        rs12821256: {effect_allele: G, effect_size: -0.89824}
        rs4959270: {effect_allele: A, effect_size: -0.36359}
        rs12203592: {effect_allele: T, effect_size: 1.997}
        rs1042602: {effect_allele: T, effect_size: 0.065432}
        rs1800407: {effect_allele: A, effect_size: -0.49601}
        rs2402130: {effect_allele: G, effect_size: 0.26536}
        rs12913832: {effect_allele: T, effect_size: 1.9391}
        rs2378249: {effect_allele: C, effect_size: -0.089509}
        rs683: {effect_allele: C, effect_size: 0.15796}
description:
  name: HirisPlex

```

### Description
### Model keys glossary
- `model` - generic model that can aggregate results of other model types  
- `diplotype_model` 
    Required keys:
    - `diplotypes`
- `description` - all properties to be included in the final results  

## Building models in .py
Models defined as .py are pure python3 scripts that use "sequencing query languange" called seqql.  
It is required to import language elements.
```
from polygenic.lib.model.seqql import PolygenicRiskScore
from polygenic.lib.model.seqql import ModelData
from polygenic.lib.model.category import QuantitativeCategory
```

It recommended to add variable pointing population for which score was prepared
```
trait_was_prepared_for_population = "eas"
```
The list of accepted population identifiers:
- `nfe` - Non-Finnish European ancestry
- `eas` - East Asian ancestry
- `afr` - African-American/African ancestry
- `amr` - Latino ancestry
- `asj` - Ashkenazi Jewish ancestry,
- `fin` - Finnish ancestry
- `oth` - Other ancestry

The most important part of model is model itself. Currently it is possible to use PolygenicRiskScore
```
model = PolygenicRiskScore(categories = ..., snps_and_coeffcients = ..., model_type = ...)
```

categories is a list of named results ranges (`QuantitativeCategory`) that can be used to define bucket for which interpretation will be generated
```QuantitativeCategory(from_= ..., to=..., category_name=...)```

snps_and_coeffcients is a list of snps
with their effect allele in genomic notation and coeffcient value. Snps are defined by their rsid
```
'rs10012': ModelData(effect_allele='G', coeff_value=0.369215857410143),
```
### Example model
```
from polygenic.lib.model.seqql import PolygenicRiskScore
from polygenic.lib.model.seqql import ModelData
from polygenic.lib.model.category import QuantitativeCategory

trait_was_prepared_for_population = "eas"

model = PolygenicRiskScore(
    categories=[
        QuantitativeCategory(from_=1.371624087, to=2.581880425, category_name='High risk'),
        QuantitativeCategory(from_=1.169616034, to=1.371624087, category_name='Potential risk'),
        QuantitativeCategory(from_=-0.346748358, to=1.169616034, category_name='Average risk'),
	    QuantitativeCategory(from_=-1.657132197, to=-0.346748358, category_name='Low risk')
    ],
    snips_and_coefficients={
	'rs10012': ModelData(effect_allele='G', coeff_value=0.369215857410143),
	'rs1014971': ModelData(effect_allele='T', coeff_value=0.075546961392531),
	'rs10936599': ModelData(effect_allele='C', coeff_value=0.086359830674748),
	'rs11892031': ModelData(effect_allele='C', coeff_value=-0.552841968657781),
	'rs1495741': ModelData(effect_allele='A', coeff_value=0.05307844348342),
	'rs17674580': ModelData(effect_allele='C', coeff_value=0.187520720836463),
	'rs2294008': ModelData(effect_allele='T', coeff_value=0.08278537031645),
	'rs798766': ModelData(effect_allele='T', coeff_value=0.093421685162235),
	'rs9642880': ModelData(effect_allele='G', coeff_value=0.093421685162235)
    },
    model_type='beta'
)
```

### Rescaling model results
It is possible to further rescale model results within each Category
```
categories=[
        QuantitativeCategory(from_=1.371624087, to=2.581880425, category_name='High risk', scale_from = 2, scale_to = 3),
        QuantitativeCategory(from_=1.169616034, to=1.371624087, category_name='Potential risk', scale_from = 1, scale_to = 2),
        QuantitativeCategory(from_=-0.346748358, to=1.169616034, category_name='Average risk', scale_from = 0, scale_to = 1),
	    QuantitativeCategory(from_=-1.657132197, to=-0.346748358, category_name='Low risk', scale_from = -1, scale_to = 0)
    ],
```

## Updates
#### 1.6.3
- added try-catch for ConflictingAlleleBetweenDataAndModel to allow model to compute
#### 1.8.0
- added yaml as model definitions
#### 1.9.0
- added parameters as input to formula_model
