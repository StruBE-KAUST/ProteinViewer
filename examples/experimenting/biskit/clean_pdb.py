import Biskit as B

m1 = B.PDBModel('domain02_cit.pdb')

m2 = m1.compress(m1.maskProtein())

m2.writePdb('cleaned_02')