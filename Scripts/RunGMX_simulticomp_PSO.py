import os, sys
sys.path.insert(1, os.path.expanduser('~') +'/Git/TranSFF/Scripts/')
from pso import parallel_pso, serial_pso, parallel_pso_auxiliary
from multiprocessing import Process, Pool
import numpy

# Input parameters ##################
run_name = "SimulPSO_C4_select3sat2lowrho1"
molecules_array = ["C4"]
datafile_keyword_array=[ "REFPROP"]
site_names_array = ["CH3", "CH2"]

ITIC_subset_name = "select3sat2lowrho1"
weights_file = "$HOME/Git/TranSFF/Weights/select3sat2lowrho1_80-20-4_2-2-1.wts"
LJ_or_BUCK="BUCK"
raw_ff_path = "$HOME/Git/ITIC_GROMACS/Forcefields/Buck-raw"

config_filename="TC_RC14_LF_BR_0.5NS-0.5NS_LINCS8_CSG.config"
gmx_exe_address = "$HOME/Git/GROMACS/gromacs-2018.1/build/bin/gmx"

Nproc_per_particle = "3"

nnn = None
sig_sigfig = 3
eps_sigfig = 1
nnn_sigfig = 1

# Set PSO parameters ################
swarm_size = 11
max_iterations = 20
tol = 1e-6

# Set PSO bounds and initial guesses ################
lb = [3.594, 119.6, 14.0, 3.860, 63.5, 20.0]
ub = [4.594, 139.6, 18.0, 4.860, 83.5, 24.0]
initial_guess = [[4.094, 129.6, 16.0, 4.360, 73.5, 22.0], [], [], [], [], [], [], [], [], [], []]
nnbp = 3



#============================================================================================
molecules = ""
datafile_keywords_string = ""
for imolec in range(0, len(molecules_array)):
    molecules = molecules + molecules_array[imolec] + " "
    datafile_keywords_string = datafile_keywords_string + datafile_keyword_array[imolec] + " "

molecules = molecules[:-1]
molecules =  "\"" + molecules + "\""
datafile_keywords_string = datafile_keywords_string[:-1]
datafile_keywords_string =  "\"" + datafile_keywords_string + "\""

print(datafile_keywords_string)
log = "pso.log"
iter = 0
def objective_function(x):
    global iter
    iter = iter + 1  

    np = len(x[:, 0])   # Number of particles (candidate solutions)
    nd = len(x[0, :])   # Number of dimensions (variables)
    
    objective_array = [] 
    def run_one_particle(run_particle_input_array):        
        iteration = run_particle_input_array[0]
        particle = run_particle_input_array[1]
        sig_eps_nnn = run_particle_input_array[2]

        for isite in range(0, len(site_names_array)):
            for inbp in range(0, nnbp):
                if nnbp == 2:
                    if inbp % (nnbp) == 0:
                        vars()['sig' + str(isite)] = round( sig_eps_nnn[isite * nnbp + inbp], sig_sigfig)
                    elif inbp % (nnbp) == 1: 
                        vars()['eps' + str(isite)] = round( sig_eps_nnn[isite * nnbp + inbp], eps_sigfig)
                elif nnbp == 3:
                    if inbp % (nnbp) == 0:
                        vars()['sig' + str(isite)] = round( sig_eps_nnn[isite * nnbp + inbp], sig_sigfig)
                    elif inbp % (nnbp) == 1: 
                        vars()['eps' + str(isite)] = round( sig_eps_nnn[isite * nnbp + inbp], eps_sigfig)
                    elif inbp % (nnbp) == 2:    
                        vars()['nnn' + str(isite)] = round( sig_eps_nnn[isite * nnbp + inbp], nnn_sigfig)

        site_sig_eps_nnn = ""
        for isite in range(0, len(site_names_array)):
            if nnbp == 2:
                if nnn is None:
                    site_sig_eps_nnn = site_sig_eps_nnn + site_names_array[isite] + "-" +  str(vars()['sig' + str(isite)]) + "-" + str(vars()['eps' + str(isite)])  + "_"
                else:
                    site_sig_eps_nnn = site_sig_eps_nnn + site_names_array[isite] + "-" +  str(vars()['sig' + str(isite)]) + "-" + str(vars()['eps' + str(isite)])  + "-" + str(round( nnn, nnn_sigfig)) + "_"
            if nnbp == 3:
                site_sig_eps_nnn = site_sig_eps_nnn + site_names_array[isite] + "-" +  str(vars()['sig' + str(isite)]) + "-" + str(vars()['eps' + str(isite)])  + "-" + str(vars()['nnn' + str(isite)]) + "_"                
        site_sig_eps_nnn = site_sig_eps_nnn[:-1]
        print(site_sig_eps_nnn)

        prefix = "i-" + str(iteration) + "_p-" + str(particle)
        print(site_sig_eps_nnn)
        arg1 = site_sig_eps_nnn
        arg2 = prefix
        arg3 = molecules
        arg4 = raw_ff_path
        arg5 = datafile_keywords_string 
        arg6 = gmx_exe_address
        arg7 = weights_file
        arg8 = Nproc_per_particle
        arg9 = ITIC_subset_name
        arg10 = config_filename
        arg11 = LJ_or_BUCK
        command = "bash $HOME/Git/ITIC_GROMACS/Scripts/RunGMX_simulticomp.sh" + " " + arg1 + " " + arg2+  " " + arg3 + " " + arg4 + " " + arg5 + " " + arg6 + " " + arg7 + " " + arg8 + " " + arg9 + " " + arg10 + " " + arg11 #+ " " + arg12 + " " + arg13 + " " + arg14 + " " + arg15 + " " + arg16
        print(command)
        os.system(command)
        
        return 
    
    run_particle_input_array = []
    for p in range(0, np):
        run_particle_input_array.append( [iter, p + 1, x[p, :]] )

    for p in range(0, np):
        exec_string = "p" + str(p) + " = Process(target = run_one_particle, args=(run_particle_input_array[" + str(p) + "],))"
        exec(exec_string)
        exec_string = "p" + str(p) + ".start()"
        exec(exec_string)

    for p in range(0, np):
        exec_string = "p" + str(p) + ".join()"
        exec(exec_string)
    
    # wait for all particles to get ready

    for p in range(0, np):
        score_file_address = "i-" + str(iter) + "_p-" + str(p + 1) + ".score"
        scores_data = numpy.loadtxt(score_file_address, skiprows=1, usecols=[1,2,3])

        if len(molecules_array) == 1:
            score = numpy.sum(scores_data[0])
        else:
            score = numpy.sum(scores_data[:,0])

        objective_array.append(score)

    print("objective_array: ", objective_array)
    print()

    return objective_array  ####################### End of objective_function

print("initial_guess: ", initial_guess)
print()
xopt, fopt = parallel_pso(objective_function, lb, ub, ig = initial_guess ,swarmsize=swarm_size, omega=0.5, phip=0.5, phig=0.5, maxiter=max_iterations, minstep=tol, minfunc=tol, debug=False, outFile = log)

print("xopt, fopt: ", xopt, fopt)

#os.system("bash $HOME/Git/TranSFF/Scripts/simulticomp_organize.sh " + run_name + " " + molecules)
