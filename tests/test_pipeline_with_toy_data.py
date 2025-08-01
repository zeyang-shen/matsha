import os
import shutil
import tempfile
import pytest
from click.testing import CliRunner
from matsha.cli import main

@pytest.fixture
def toy_data_dir():
    return os.path.join(os.path.dirname(__file__), "toy_data")

@pytest.fixture
def temp_dir():
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)

def test_pipeline_on_toy_data(temp_dir, toy_data_dir):
    # Setup paths
    input_file = os.path.join(toy_data_dir, "input_file.tsv")
    genome_file = os.path.join(toy_data_dir, "reference.fna")
    genbank_file = os.path.join(toy_data_dir, "reference.gbff")
    output_dir = os.path.join(toy_data_dir, "output")

    # Run CLI with toy data
    runner = CliRunner()
    result = runner.invoke(main, [
        "--input", input_file,
        "--genome", genome_file,
        "--genbank", genbank_file,
        "--output", output_dir,
        "--temp", temp_dir,
        "--keep-temp",
        "--force",
        "--paired",
        "--threads", "1",
    ])

    assert result.exit_code == 0, f"CLI failed: {result.output}"
    
    # Check for expected output:
    # BAM
    expected_bam = os.path.join(temp_dir, "Sample9_novaseq_R1.fastq.sorted.groupAdded.bam")
    assert os.path.isfile(expected_bam), f"Expected BAM file missing: {expected_bam}"
    
    # Coverage
    expected_coverage = os.path.join(temp_dir, "Sample9_novaseq_R1.fastq.coverage")
    assert os.path.isfile(expected_coverage), f"Expected coverage file missing: {expected_coverage}"

    # Subsampling stats
    expected_subsample_stats_file = os.path.join(temp_dir, "subsampling.stats")
    assert os.path.isfile(expected_subsample_stats_file), f"Expected subsampling stats file missing: {expected_subsample_stats_file}"

    # BAM list file
    expected_bam_list_file = os.path.join(temp_dir, "bam.all.list")
    assert os.path.isfile(expected_bam_list_file), f"Expected BAM list file missing: {expected_bam_list_file}"
    with open(expected_bam_list_file, 'r') as file:
        lines = file.read().splitlines()
    assert len(lines) == 20
    assert expected_bam in lines

    # VCF
    expected_vcf = os.path.join(output_dir, "all", "combined.g.vcf")
    assert os.path.isfile(expected_vcf), f"Expected VCF file missing: {expected_vcf}"

    # Final GWAS results
    expected_gwas_gene = os.path.join(output_dir, "all", "gwas_output_significant.gene.tsv")
    assert os.path.isfile(expected_gwas_gene), f"Expected GWAS gene file missing: {expected_gwas_gene}"
    with open(expected_gwas_gene, 'r') as file:
        lines = file.read().splitlines()
    sig_genes = [l.split('\t')[1] for l in lines[1:]]
    assert sig_genes == ["EQW00_RS00010"]

    expected_gwas_variant = os.path.join(output_dir, "all", "gwas_output_significant.variant.tsv")
    assert os.path.isfile(expected_gwas_variant), f"Expected GWAS variant file missing: {expected_gwas_variant}"
    with open(expected_gwas_variant, 'r') as file:
        lines = file.read().splitlines()
    sig_vars = [l.split('\t')[1] for l in lines[1:]]
    assert sig_vars == ["NZ_CP035288.1:1768|EQW00_RS00010", "NZ_CP035288.1:2542|EQW00_RS00010"]


def test_pipeline_on_toy_data_no_gbff(temp_dir, toy_data_dir):
    # Setup paths
    input_file = os.path.join(toy_data_dir, "input_file.tsv")
    genome_file = os.path.join(toy_data_dir, "reference.fna")
    output_dir = os.path.join(temp_dir, "output")

    # Run CLI with toy data
    runner = CliRunner()
    result = runner.invoke(main, [
        "--input", input_file,
        "--genome", genome_file,
        "--output", output_dir,
        "--temp", temp_dir,
        "--keep-temp",
        "--force",
        "--paired",
        "--threads", "1",
    ])

    assert result.exit_code == 0, f"CLI failed: {result.output}"
    
    # Check for expected output:
    # BAM
    expected_bam = os.path.join(temp_dir, "Sample9_novaseq_R1.fastq.sorted.groupAdded.bam")
    assert os.path.isfile(expected_bam), f"Expected BAM file missing: {expected_bam}"
    
    # Coverage
    expected_coverage = os.path.join(temp_dir, "Sample9_novaseq_R1.fastq.coverage")
    assert os.path.isfile(expected_coverage), f"Expected coverage file missing: {expected_coverage}"

    # Subsampling stats
    expected_subsample_stats_file = os.path.join(temp_dir, "subsampling.stats")
    assert os.path.isfile(expected_subsample_stats_file), f"Expected subsampling stats file missing: {expected_subsample_stats_file}"

    # BAM list file
    expected_bam_list_file = os.path.join(temp_dir, "bam.all.list")
    assert os.path.isfile(expected_bam_list_file), f"Expected BAM list file missing: {expected_bam_list_file}"
    with open(expected_bam_list_file, 'r') as file:
        lines = file.read().splitlines()
    assert len(lines) == 20
    assert expected_bam in lines

    # VCF
    expected_vcf = os.path.join(output_dir, "all", "combined.g.vcf")
    assert os.path.isfile(expected_vcf), f"Expected VCF file missing: {expected_vcf}"

    # Final GWAS results
    expected_gwas_gene = os.path.join(output_dir, "all", "gwas_output.gene.tsv")
    assert not os.path.isfile(expected_gwas_gene)

    expected_gwas_variant = os.path.join(output_dir, "all", "gwas_output_significant.variant.tsv")
    assert os.path.isfile(expected_gwas_variant), f"Expected GWAS variant file missing: {expected_gwas_variant}"
    with open(expected_gwas_variant, 'r') as file:
        lines = file.read().splitlines()
    sig_vars = [l.split('\t')[1] for l in lines[1:]]
    assert sig_vars == ["NZ_CP035288.1:1768|", "NZ_CP035288.1:2542|"]
    

