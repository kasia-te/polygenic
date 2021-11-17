import argparse
import sys
import os

from polygenic.tools.utils import error_exit
from polygenic.tools.utils import setup_logger
from polygenic.tools.utils import download
from polygenic.tools.utils import is_valid_path
from polygenic.tools.utils import clump
from polygenic.tools.utils import read_table
from polygenic.tools.utils import validate_with_source
from polygenic.data.vcf_accessor import VcfAccessor

def parse_args(args):
    parser = argparse.ArgumentParser(description='pgstk model-biobankuk prepares polygenic score model based on p value data')
    parser.add_argument('--code', '--phenocode', type=str, required=True, help='phenocode of phenotype form Uk Biobank')
    parser.add_argument('--sex', '--pheno_sex', type=str, default="both_sexes", help='pheno_sex of phenotype form Uk Biobank')
    parser.add_argument('--coding', type=str, default="", help='additional coding of phenotype form Uk Biobank')
    parser.add_argument('--output-directory', type=str, default='.', help='output directory')
    parser.add_argument('--index-file', type=str, help='path to Index file from PAN UKBiobank. It can be downloaded using gbe-get')
    parser.add_argument('--variant-metrics-file', type=str, help='path to annotation file. It can be downloaded from https://pan-ukb-us-east-1.s3.amazonaws.com/sumstats_release/full_variant_qc_metrics.txt.bgz')
    parser.add_argument('--index-url', type=str, default='https://pan-ukb-us-east-1.s3.amazonaws.com/sumstats_release/phenotype_manifest.tsv.bgz', help='url of index file for PAN UKBiobank.')
    parser.add_argument('--variant-metrics-url', type=str, default='https://pan-ukb-us-east-1.s3.amazonaws.com/sumstats_release/full_variant_qc_metrics.txt.bgz', help='url for variant summary metrics')
    parser.add_argument('--threshold', type=float, default=1e-08, help='significance cut-off threshold')
    parser.add_argument('--population', type=str, default='EUR', help='population: meta, AFR, AMR, CSA, EAS, EUR, MID')
    parser.add_argument('--clumping-vcf', type=str, default='eur.phase3.biobank.set.vcf.gz', help='')
    parser.add_argument('--source-ref-vcf', type=str, default='', help='')
    parser.add_argument('--target-ref-vcf', type=str, default='', help='')
    parser.add_argument('-l', '--log-file', type=str, help='path to log file')
    parsed_args = parser.parse_args(args)
    parsed_args.index_file = parsed_args.index_file if parsed_args.index_file else parsed_args.output_directory + "/biobankuk_phenotype_manifest.tsv"
    parsed_args.variant_metrics_file = parsed_args.variant_metrics_file if parsed_args.variant_metrics_file else parsed_args.output_directory + "/full_variant_qc_metrics.txt"
    return parsed_args

def get_index(args):
    download(args.index_url, os.path.abspath(args.index_file))
    download(args.variant_metrics_url, os.path.abspath(args.variant_metrics_file))
    return

def get_data(args):
    with open(args.index_file, 'r') as indexfile:
        firstline = indexfile.readline()
        phenocode_colnumber = firstline.split('\t').index("phenocode")
        pheno_sex_colnumber = firstline.split('\t').index("pheno_sex")
        coding_colnumber = firstline.split('\t').index("coding")
        aws_link_colnumber = firstline.split('\t').index("aws_link")
        while True:
            line = indexfile.readline()
            if not line:
                break
            if line.split('\t')[phenocode_colnumber] != args.code:
                continue
            if line.split('\t')[pheno_sex_colnumber] != args.sex:
                continue
            if line.split('\t')[coding_colnumber] != args.coding:
                continue
            url = line.split('\t')[aws_link_colnumber]
            break
    if not url is None:
        output_directory = os.path.abspath(os.path.expanduser(args.output_directory))
        output_file_name = os.path.splitext(os.path.basename(url))[0]
        output_path = output_directory + "/" + output_file_name
        download(url=url, output_path=output_path, force=False, progress=True)
        args.gwas_file = output_path
        return output_path
    return None

def validate_paths(args):
    if not is_valid_path(args.output_directory, is_directory=True): return
    if not is_valid_path(args.gwas_file): return
    if not is_valid_path(args.target_ref_vcf): return
    if not is_valid_path(args.target_ref_vcf): return

def filter_pval(args):
    output_path = args.gwas_file + ".filtered"
    with open(args.gwas_file, 'r') as data, open(args.variant_metrics_file, 'r') as anno, open(output_path, 'w') as output:
        data_header = data.readline().rstrip().split('\t')
        anno_header = anno.readline().rstrip().split('\t')
        output.write('\t'.join(data_header + anno_header) + "\n")
        while True:
            try:
                data_line = data.readline().rstrip().split('\t')
                anno_line = anno.readline().rstrip().split('\t')
                if float(data_line[data_header.index('pval_' + args.population)].replace('NA', '1', 1)) <= args.threshold:
                    output.write('\t'.join(data_line + anno_line) + "\n")
            except:
                break
    return

def clump_variants(args):
    return clump(
        gwas_file = args.gwas_file, 
        reference = os.path.abspath(os.path.expanduser(args.clumping_vcf)), 
        clump_field = "pval_" + args.population,
        threshold = args.threshold)

def read_clumped_variants(args):
    source_vcf = VcfAccessor(args.source_ref_vcf)
    data = read_table(args.gwas_file + ".clumped")
    for line in data: line.update({"rsid": line['chr'] + ":" + line['pos'] + "_" + line['ref'] + "_" + line['alt']})
    for line in data: line.update({"REF": line['ref'], "ALT": line['alt']})
    for line in data: line.update({"BETA": line["beta_" + args.population]})
    for line in data: line.update({"af": line["af_" + args.population]})
    return data

def run(args):
    get_index(args)
    gwas_file = get_data(args)
    #validate_paths(args)
    #filter_pval(args)
    #clump_variants(args)
    data = read_clumped_variants(args)
    data = validate_with_source(data, args.source_ref_vcf)
    # source_vcf = VcfAccessor(parsed_args.source_ref_vcf)
    # target_vcf = VcfAccessor(parsed_args.target_ref_vcf)

    



    # data = [validate(line, validation_source = target_vcf) for line in data]

    # description = simulate_parameters(data)

    # model_path = path + ".yml"
    # write_model(data, description, model_path)

    return

def main(args = sys.argv[1:]):

    args = parse_args(args) 
    setup_logger(args.log_file) if args.log_file else setup_logger(args.output_directory + "/pgstk.log")

    try:
        run(args)
    except PolygenicException as e:
        error_exit(e)

if __name__ == '__main__':
    main(sys.argv[1:])