To create an xls file with sheets to be filled use the example and modify to your needs.
--descriptions   adds the descriptions in the second line
--enums adds the enum options in the third line

python3 get_field_info.py --type User --type Award --type Lab --type Organism --type Publication --type Document --type Vendor --type Protocol --type ProtocolsCellCulture --type Biosource --type Enzyme --type Construct --type TreatmentRnai --type Modification --type Biosample --type File --type FileSet --type IndividualHuman --type IndividualMouse --type ExperimentHiC --type ExperimentSet --descriptions --enums --writexls


To get a single sheet use
'''
python3 get_field_info.py --type Lab --descriptions --enums --writexls
'''
