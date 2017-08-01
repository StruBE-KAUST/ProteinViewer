import modeller as M
import modeller.automodel as AM
import time
from django.conf import settings

# class CustomModel( AM.automodel ):
#         """Override restraint generating method to define rigid body regions"""

#         def special_restraints(self, aln):
#             """
#             Fix input domains as rigid bodies -- does not seem to have much
#             effect on speed though
#             """
#             # fix domains as rigid bodies to save time (manual p. 58)
#             rb = M.rigid_body( self.residue_range( '4', '110' ) )
#             self.restraints.rigid_bodies.append( rb )

#             rb = M.rigid_body( self.residue_range( '136', '361') )
#             self.restraints.rigid_bodies.append( rb )

def modeller():
    # request verbose output
    M.log.verbose() 

    # create a new MODELLER environment to build this model in
    env = M.environ()

    # directories for input atom files
    env.io.atom_files_directory = ['%s' %(settings.MEDIA_ROOT)]

    # commented out because it doesn't use the templates to build, then; messes
    # up the relative orientations. Still messes up the indivitual orientation,
    # but working to fix that...

    # a = CustomModel(env,
    #                 alnfile='%s/target_aln.pir' %(settings.MEDIA_ROOT),
    #                 knowns= ('01_fk_cut_trans', '02_cit_cut_trans'),
    #                 sequence = 'target')

    # a = AM.automodel(env,
    #                 alnfile='%s/target_aln.pir' %(settings.MEDIA_ROOT),
    #                 knowns= ('01_fk_cut_trans', '02_cit_cut_trans'),
    #                 sequence = 'target')


    # try to use the model class to make use of transfer_xyz.. don't know how to 
    # deal with the linker..
    # a = M.model(env)

    # aln = M.alignment(env, file='%s/target_aln.pir' %(settings.MEDIA_ROOT), align_codes=('01_fk_cut_trans', '02_cit_cut_trans'))
    # aln.malign3d(fit=False)
    # a.read('fk_cit_trans', model_format='PDB', model_segment=('FIRST:@', 'LAST:'))
    
    # aln.append(file='%s/target_aln.pir' %(settings.MEDIA_ROOT), align_codes='linker')

    # a.generate_topology(aln['linker'])

    # a.build(initialize_xyz=False, build_method="INTERNAL_COORDINATES")
    # a.write(file='output.pdb')



    # a = AM.loopmodel(env,
    #                  sequence='target',
    #                  alnfile='%s/target_aln.pir' %(settings.MEDIA_ROOT),
    #                  inimodel='fk_cit_trans')

    # a.loop.starting_model = 1
    # a.loop.ending_model = 1

    class MyModel(AM.automodel):
        def select_atoms(self):
            return M.selection(self.residue_range('111', '134'))

    
    a = MyModel(env, alnfile = '%s/target_aln.pir' %(settings.MEDIA_ROOT),
                knowns= ('01_fk_cut_trans', '02_cit_cut_trans'),
                sequence = 'target')

    a.starting_model = 1
    a.ending_model = 1

    # takes the time from 15-17 sec to 2-3 sec!!! BUT: DOESNT EVEN CONNECT
    # THE DOMAINS?!?!
    # a.very_fast()

    clock_start = time.time()
    a.make()

    clock_end = time.time()
    print "Run finished after: ", clock_end - clock_start, " seconds."

