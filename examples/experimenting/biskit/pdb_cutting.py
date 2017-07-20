import Biskit as B

m1 = B.PDBModel('input_fk_Cit.pdb')

d1 = m1.take(range(0, 1029))
d2 = m1.take(range(1029, 2881))

# d2 = m1.take(range(1745, 3596))


d1.writePdb('broken_01')
d2.writePdb('broken_02')