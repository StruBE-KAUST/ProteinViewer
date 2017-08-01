import Biskit as B
import Biskit.Mod.modUtils as U
from django.conf import settings

def prep():
        
    fk = B.PDBModel('%s/01_fk_cut_trans.pdb' %(settings.MEDIA_ROOT))
    cit= B.PDBModel('%s/02_cit_cut_trans.pdb' %(settings.MEDIA_ROOT))

    seq_fk = fk.sequence()
    seq_linker = 'TG' + 10*'GS' + 'TG'
    seq_cit = cit.sequence()


    seq_target = 'MTG' + seq_fk + seq_linker + seq_cit + '*'
    aln_fk     = '---' + seq_fk + '-'*(len(seq_linker)+len(seq_cit)) + '*'
    aln_cit    = '---' + '-'*(len(seq_fk)+len(seq_linker)) + seq_cit + '*'

    def seq2pir( seq, name,
                     alntype='structure',
                     ):
        """
        format sequence as PIR alignment entry
        see: https://salilab.org/modeller/9v7/manual/node445.html
        """
        r = '>P1;%s\n' % name
        r += '%s:%s:.:.:.:.::::\n' % (alntype, name)
        r += U.format_fasta(seq, width=75)
        
        return r

    with open('%s/target_aln.pir' %(settings.MEDIA_ROOT), 'w') as f:
        f.write( seq2pir( seq_target, 'target', alntype='sequence') + '\n\n' )
        f.write( seq2pir( aln_fk, '01_fk_cut_trans' ) + '\n\n' )
        f.write( seq2pir( aln_cit, '02_cit_cut_trans')+ '\n\n' )
