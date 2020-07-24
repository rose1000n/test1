from class_conf_pro import Network


#  Generate Network ---------------------------------------
Net = Network()


#  Generate Conf File -------------------------------------

#  (Name, N, C, Taum, RestPot, ResetPot, Threshold)
#neus= ['neu','neu1','neu2','neu3','neu4','neu5','neu6','neu7','neu8','neu9']
#for neu in neus:
#Net.add_neuron(neu[], 1, 1, 10, -70, -50, -30.01)
neu=1
while neu<=10:
 Net.add_neuron(str(neu), 1, 1, 10, -70, -50, -30.01)
 neu+=1
 

#  (Name, Tau, RevPot, FreqExt, MeanExtEff, MeanExtCon)
Net.add_receptor('Ach', 20, 0, 0, 2.1, 1)
Net.add_receptor('NMDA', 100, 0, 0, 2.1, 1)
Net.add_receptor('AMPA', 2, 0, 0, 2.1, 1)
Net.add_receptor('GABA', 5, -70, 0, 2.1, 1)
Net.set_neuron_receptor_all('GABA')

#  (Pre_syn, Post_syn, TargetReceptor, MeanEff, weight)
#for neu in neus 
#neupost=neus-neu
#Net.add_target(neu[], neupost[], 'GABA', 10, 10)
#%%
import  random
neu=1
neupost=1
while neu<=10:
 rounds=1
 while rounds<=4:
  neupost=random.randint(1,10)
  while neu==neupost:
   neupost=random.randint(1,10) 
  Net.add_target(str(neu), str(neupost), 'GABA', 10, 10)
  rounds+=1
 neu+=1
 if neu==10:
    break
   

#  Generate Pro File -------------------------------------

Type_Mem = 'ChangeMembraneNoise'
Type_Freq = 'ChangeExtFreq'
Type_End = 'EndTrial'

#  (Time, Type, GaussMean, GaussSTD)
Net.add_event(1, Type_Mem, str(neu), 4, 0)
Net.add_event(500, Type_End)

#  (File_Name, Output_Type, Population, *args)
Net.add_output('FiringRateALL.dat', 'FiringRate', str(neu), 100, 10)
Net.add_output('SpikeALL.dat', 'Spike', 'AllPopulation')
Net.add_output('MemPot.dat', 'MemPot', 'AllPopulation')


#  Output -------------------------------------------------

Net.output('network.conf', 'network.pro')
Net.plot_network()
#%%

# %%
