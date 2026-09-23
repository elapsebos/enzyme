"""Chemical identity and atom mapping for the literature 2-HE(MHET)3 model."""

SMILES = "OCCOC(=O)c1ccc(C(=O)OCCOC(=O)c2ccc(C(=O)OCCOC(=O)c3ccc(C(=O)OCCO)cc3)cc2)cc1"
EXPECTED_FORMULA = "C32H30O14"
EXPECTED_ATOMS = 76
CONFORMER_SEED = 20260923

# Heavy-atom correspondences from the 5XH3 HEMT component to the middle
# terephthalate unit of 2-HE(MHET)3. The C09/O10/O11 group is the
# oxyanion-hole carbonyl identified from the crystallographic coordinates.
HEMT_TO_PET3 = {
    "C05": 18, "C06": 19, "C07": 20, "C08": 21, "C15": 42, "C16": 43,
    "C03": 16, "O04": 17, "O02": 15, "C01": 14,
    "C09": 22, "O10": 23, "O11": 24, "C12": 25, "C13": 26, "O14": 27,
}
SCISSILE_CARBONYL_C = 22
SCISSILE_CARBONYL_O = 23
SCISSILE_ESTER_O = 24
