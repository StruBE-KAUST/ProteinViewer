import modeller as M
import modeller.automodel as AM
import time
from django.conf import settings

class CustomModel( AM.automodel ):
        """Override restraint generating method to define rigid body regions"""

        def special_restraints(self, aln):
            """
            Fix input domains as rigid bodies -- does not seem to have much
            effect on speed though
            """
            # fix domains as rigid bodies to save time (manual p. 58)
            rb = M.rigid_body( self.residue_range( '4', '110' ) )
            self.restraints.rigid_bodies.append( rb )

            rb = M.rigid_body( self.residue_range( '136', '361') )
            self.restraints.rigid_bodies.append( rb )

def modeller():
    # request verbose output
    M.log.verbose() 

    # create a new MODELLER environment to build this model in
    env = M.environ()

    # directories for input atom files
    env.io.atom_files_directory = ['%s' %(settings.MEDIA_ROOT)]

    print "running modeller"

    ## a = AM.automodel(env, ## default modelling without restraints

    a = CustomModel(env,
                    alnfile='%s/target_aln.pir' %(settings.MEDIA_ROOT),
                    knowns= ('01_fk_cut_trans', '02_cit_cut_trans'),
                    sequence = 'target')


    a.starting_model = 1
    a.ending_model = 1

    ## a.very_fast() ## does not seem to work for us

    clock_start = time.time()
    # remove allow alternates?
    a.make()

    clock_end = time.time()
    print "Run finished after: ", clock_end - clock_start, " seconds."

