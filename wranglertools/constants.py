#!/usr/bin/env python3
# -*- coding: latin-1 -*-
import pathlib as pp


''' 2022-10-31 add a .submit4dn directory to store keypairs.json and if used google auth files
    the home directory will still be automatically checked to support older installations and
    an enviromental variable will also be queried for
'''
HOME = pp.Path.home()
CONFDIR = HOME.joinpath('.submit4dn')
DEFAULT_KEYPAIR_FILE = 'keypairs.json'
ENV_VAR_DIR = 'SUBMIT_4DN_CONF_DIR'

SHEET_ORDER = [
    "User", "Award", "Lab", "Document", "Protocol", "ExperimentType",
    "Publication", "Organism", "Vendor", "IndividualChicken", "IndividualFly",
    "IndividualHuman", "IndividualMouse", "IndividualPrimate",
    "IndividualZebrafish", "FileFormat", "Enzyme", "GenomicRegion", "Gene",
    "BioFeature", "Construct", "TreatmentRnai", "TreatmentAgent",
    "Antibody", "Modification", "Image", "Biosource", "BiosampleCellCulture",
    "Biosample", "FileFastq", "FileProcessed", "FileReference",
    "FileCalibration", "FileSet", "FileSetCalibration", "MicroscopeSettingD1",
    "MicroscopeSettingD2", "MicroscopeSettingA1", "MicroscopeSettingA2",
    "FileMicroscopy", "FileSetMicroscopeQc", "ImagingPath", "ExperimentMic",
    "ExperimentMic_Path", "ExperimentHiC", "ExperimentCaptureC",
    "ExperimentRepliseq", "ExperimentAtacseq", "ExperimentChiapet",
    "ExperimentDamid", "ExperimentSeq", "ExperimentTsaseq", "ExperimentSet",
    "ExperimentSetReplicate", "WorkflowRunSbg", "WorkflowRunAwsem",
    "OntologyTerm"
]

# list of [sheet, [fields]] that need to be patched as a second step
# should be in sync with loadxl.py in fourfront
LIST_OF_LOADXL_FIELDS = [
    ['Document', ['references']],
    ['User', ['lab', 'submits_for']],
    ['ExperimentType', ['sop', 'reference_pubs']],
    ['Biosample', ['biosample_relation']],
    ['Experiment', ['experiment_relation']],
    ['ExperimentMic', ['experiment_relation']],
    ['ExperimentHiC', ['experiment_relation']],
    ['ExperimentSeq', ['experiment_relation']],
    ['ExperimentTsaseq', ['experiment_relation']],
    ['ExperimentDamid', ['experiment_relation']],
    ['ExperimentChiapet', ['experiment_relation']],
    ['ExperimentAtacseq', ['experiment_relation']],
    ['ExperimentCaptureC', ['experiment_relation']],
    ['ExperimentRepliseq', ['experiment_relation']],
    ['FileFastq', ['related_files']],
    ['FileReference', ['related_files']],
    ['FileCalibration', ['related_files']],
    ['FileMicroscopy', ['related_files']],
    ['FileProcessed', ['related_files', 'produced_from']],
    ['Individual', ['individual_relation']],
    ['IndividualChicken', ['individual_relation']],
    ['IndividualFly', ['individual_relation']],
    ['IndividualHuman', ['individual_relation']],
    ['IndividualMouse', ['individual_relation']],
    ['IndividualPrimate', ['individual_relation']],
    ['IndividualZebrafish', ['individual_relation']],
    ['Publication', ['exp_sets_prod_in_pub', 'exp_sets_used_in_pub']]
]

# these may change are special so adding as explicit constant
XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
ZIP_MIME = 'application/zip'

ALLOWED_MIMES = (
    'application/pdf',
    ZIP_MIME,
    'text/plain',
    'text/tab-separated-values',
    'text/html',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    XLSX_MIME,
    'image/png',
    'image/jpeg',
    'image/gif',
    'image/tiff',
)

''' These are the scope of access needed for accessing google sheets
    Currently only read is supported and needed - this is used in the
    google oauth athentication workflow.
    NOTE: if additional access scopes are wanted needed this will need
    re-approval by google - AJS 2022-10-31'''
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
GCRED_FNAME = 'credentials.json'
AUTH_TOKEN_FNAME = 'authorized_user.json'
# pattern to search url for a google sheet ID
GSHEET_URL_REGEX = "/spreadsheets/d/([A-Za-z0-9_-]+)/*"
# gets all the characters after /d/ and before the next slash
# https://docs.google.com/spreadsheets/d/1hy9iilJUfAIbANCkuDZtbOL5wiQ8nKUGRwENK3qlWj4/edit#gid=0
# https://docs.google.com/spreadsheets/d/1jMY15_7Qmmj5tYPLtDFXj87H-Qy732E0kYtU1S4Ddgs/edit#gid=1689247783
# and then make sure it only has valid characters
GSID_REGEX = "^[A-Za-z0-9_-]+$"
# can only contain alpha-numerics or _ or -
# 1hy9iilJUfAIbANCkuDZtbOL5wiQ8nKUGRwENK3qlWj4 or 1jMY15_7Qmmj5tYPLtDFXj87H-Qy732E0kYtU1S4Ddgs
# supported spreadsheet types
GSHEET = 'gsheet'  # google spreadsheet
EXCEL = 'excel'  # excel xlsx workbook
