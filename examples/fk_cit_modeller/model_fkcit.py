import modeller as M
import modeller.automodel as AM
import time

# request verbose output
M.log.verbose() 

# create a new MODELLER environment to build this model in
env = M.environ()

# directories for input atom files
env.io.atom_files_directory = ['.']

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


## a = AM.automodel(env, ## default modelling without restraints

a = CustomModel(env,
                alnfile='target_aln.pir',
                knowns= ('01_fk_moved', '02_cit_moved'),
                sequence = 'target')


a.starting_model = 1
a.ending_model = 1

## a.very_fast() ## does not seem to work for us

clock_start = time.time()
a.make()

clock_end = time.time()
print "Run finished after: ", clock_end - clock_start, " seconds."

