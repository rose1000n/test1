# Network ------------------------------------------------

class Network:
    def __init__(self, name='Network'):
        self.name = name
        self.reset()

    def reset(self):
        self.neu = {}
        self.group = {}
        self.eve = []
        self.out = []
        self.receptor = {}
        self.mg = 1.0
        self.track_eve = {}
        self.region = {}

    def add_neuron(self, name, *args):
        neuron = NeuralPopulation(name, *args)
        self.neu[name] = (len(self.neu), neuron)
        return neuron

    def add_neuron_population(self, name, num, start=0):
        arr = []
        for i in range(start, start + num):
            arr.append(self.add_neuron(name + str(i)))
        return arr

    def check_neuron_in_network(self, *neurons):
        for neuron in neurons:
            if neuron not in self.neu.keys():
                raise Exception(f'[{neuron}] cannot be found in [{self.name}].')

    def add_target(self, pre_syn, post_syn, TargetReceptor='', MeanEff=0, weight=0):
        self.check_neuron_in_network(pre_syn, post_syn)
        self.check_receptor_in_population(post_syn, TargetReceptor)
        self.neu[pre_syn][1].add_target(post_syn, TargetReceptor, MeanEff, weight)

    def add_group(self, group_name, *member_name):
        self.check_neuron_in_network(*member_name)
        if group_name in self.group.keys():
            self.group[group_name].add_member_list(member_name)
        else:
            tmp_group = Group(group_name)
            tmp_group.add_member_list(member_name)
            self.group[group_name] = tmp_group

    def check_population_in_network_or_group(self, population):
        if (population not in self.neu.keys()) and (population not in self.group.keys()):
            raise Exception(f'[{population}] cannot be found in the network or any group.')

    def check_receptor_in_population(self, population, receptor):
        if population in self.group.keys():
            for neuron in self.group[population].member:
                if receptor not in [rec.name for rec in self.neu[neuron][1].receptor]:
                    raise Exception(f'[{receptor}] receptor cannot be found in [{neuron} (group:{population})].')
        else:
            if receptor not in [rec.name for rec in self.neu[population][1].receptor]:
                raise Exception(f'[{receptor}] receptor cannot be found in [{population}].')

    def add_event(self, time, event_type, *args):
        if (event_type != 'EndTrial') and (args[0] != 'AllPopulation'):
            self.check_population_in_network_or_group(args[0])
        if event_type == 'ChangeExtFreq':
            self.check_receptor_in_population(args[0], args[1])
        event = Event(time, event_type, *args)
        self.eve.append(event)
        return event

    def add_track_event(self, time, event_type, population, *args):
        if population in self.group.keys():
            for neu in self.group[population].member:
                e = Event(time, event_type, neu, *args)
                self.track_eve[(time, event_type, neu)] = e
        else:
            e = Event(time, event_type, population, *args)
            self.track_eve[(time, event_type, population)] = e

    def add_output(self, file_name, output_type, population, *args):
        if population != 'AllPopulation':
            self.check_population_in_network_or_group(population)
        output = Output(file_name, output_type, population, *args)
        self.out.append(output)
        return output

    def add_receptor(self, name, Tau=0, RevPot=0, FreqExt=0, MeanExtEff=0, MeanExtCon=0):
        self.receptor[name] = Receptor(name, Tau, RevPot, FreqExt, MeanExtEff, MeanExtCon)

    def set_neuron_param(self, name, param, value):
        setattr(self.neu[name][1], param, value)

    def set_neuron_param_all(self, N, C, Taum, RestPot, ResetPot, Threshold, RefactoryPeriod=-1, SpikeDly=-1):
        for neu in self.neu.values():
            neu[1].set_param(N, C, Taum, RestPot, ResetPot, Threshold, RefactoryPeriod, SpikeDly)

    def set_LTP(self, name, tLP, PosISI, NegISI):
        self.neu[name][1].set_LTP(tLP, PosISI, NegISI)

    def set_neuron_receptor(self, name, *receptors):
        self.neu[name][1].receptor.clear()
        for rec in receptors:
            self.neu[name][1].add_receptor(self.receptor[rec])

    def set_neuron_receptor_all(self, *receptors):
        for neu in self.neu.values():
            for rec in receptors:
                neu[1].add_receptor(self.receptor[rec])

    def set_target_param(self, pre_syn, post_syn, param, value):
        setattr(self.neu[pre_syn][1].target[post_syn], param, value)

    def add_innervation(self, name, den_list, axon_list):
        self.neu[name][1].add_innervation('den', den_list)
        self.neu[name][1].add_innervation('axon', axon_list)

    def region_information(self):
        for name, neu_item in self.neu.items():
            neu = neu_item[1]
            for polarity, regions in neu.innervation.items():
                for reg in regions:
                    if reg not in self.region.keys():
                        self.region[reg] = {
                                'den': [],
                                'axon': []
                                }
                    self.region[reg][polarity].append(name)

    def region_to_target(self):
        self.region_information()
        for synapses in self.region.values():
            for pre_syn in synapses['axon']:
                for post_syn in synapses['den']:
                    self.add_target(pre_syn, post_syn, 'AMPA', 1, 1)

    def conf_comment(self, fout):
        for neu_item in self.neu.values():
            neu = neu_item[1]
            if neu.target:
                fout.write('%( ' + neu.name + ' --> ')
                for tar in list(neu.target.values())[:-1]:
                    fout.write(tar.name + ':' + str(round(tar.MeanEff * tar.weight, 6)) + ', ')
                last_target = list(neu.target.values())[-1]
                fout.write(last_target.name + ':' + str(round(last_target.MeanEff * last_target.weight, 6)))
                fout.write(' )\n')
        fout.write('\n')

    def pro_comment(self, fout):
        for eve in self.eve:
            fout.write('%')
            fout.write(str(tuple(eve.__dict__.values())))
            fout.write('\n')
        fout.write('\n')

    def output(self, conf_file, pro_file, comment=True):
        with open(conf_file, 'wt') as conf_out:
            if comment is True:
                self.conf_comment(conf_out)

            if self.mg != 1.0:
                conf_out.write('%--------------------------------' + '\n\n')
                conf_out.write('MagnesiumConcentration=' + str(self.mg) + '\n\n')

            for neu in self.neu.values():
                conf_out.write('%--------------------------------' + '\n')
                neu[1].output(conf_out)

        with open(pro_file, 'wt') as pro_out:
            if self.eve and comment is True:
                self.pro_comment(pro_out)
                pro_out.write('%--------------------------------' + '\n\n')

            if self.group:
                pro_out.write('DefineMacro' + '\n\n')
                for group in self.group.values():
                    group.output(pro_out)
                pro_out.write('EndDefineMacro' + '\n\n\n')
                pro_out.write('%--------------------------------' + '\n\n')

            if self.track_eve:
                for eve in self.track_eve.values():
                    eve.output(pro_out)

            if self.eve:
                for eve in self.eve:
                    eve.output(pro_out)
                pro_out.write('%--------------------------------' + '\n\n')

            if self.out:
                pro_out.write('OutControl' + '\n\n')
                for out in self.out:
                    out.output(pro_out)
                pro_out.write('EndOutControl' + '\n')

    def plot_network(self, filename='', show=True, layout='spring'):
        import matplotlib.pyplot as plt
        import networkx as nx

        G = nx.DiGraph()
        red_edge = []
        blue_edge = []

        for neu_item in self.neu.values():
            neu = neu_item[1]
            for tar in neu.target.values():
                G.add_edge(neu.name, tar.name)
                if tar.TargetReceptor == 'GABA':
                    red_edge.append((neu.name, tar.name))
                else:
                    blue_edge.append((neu.name, tar.name))

        print('neuron number:  ', G.number_of_nodes())
        print('synapse number: ', G.number_of_edges())

        to_layout = getattr(nx, layout + '_layout')
        pos = to_layout(G)

        nx.draw(G, pos, edgelist=blue_edge, edge_color='b', with_labels=True, node_size=1000, arrowsize=20)
        nx.draw(G, pos, edgelist=red_edge, edge_color='r', with_labels=True, node_size=1000, arrowsize=20)

        if filename != '':
            plt.savefig(filename, format='png')
        if show is True:
            plt.show()

    def table(self, filename='connection_table.txt', digit=False):
        with open(filename, 'wt') as fout:
            for neu_item in self.neu.values():
                neu = neu_item[1]
                if digit is False:
                    if neu.target:
                        for tar in neu.target.values():
                            if tar.TargetReceptor == 'GABA':
                                fout.write(neu.name + ' ' + tar.name + ' ' + str(-1 * tar.MeanEff * tar.weight) + '\n')
                            else:
                                fout.write(neu.name + ' ' + tar.name + ' ' + str(tar.MeanEff * tar.weight) + '\n')
                else:
                    if neu.target:
                        for tar in neu.target.values():
                            if tar.TargetReceptor == 'GABA':
                                fout.write(str(self.neu[neu.name][0]) + ' ' + str(self.neu[tar.name][0]) + ' ' + str(-1 * tar.MeanEff * tar.weight) + '\n')
                            else:
                                fout.write(str(self.neu[neu.name][0]) + ' ' + str(self.neu[tar.name][0]) + ' ' + str(tar.MeanEff * tar.weight) + '\n')

    def parse_table(self, filename='connection_table.txt', excitatory_receptor='AMPA'):
        import pandas as pd
        table = pd.read_csv(filename, delim_whitespace=True, header=None)
        for index, row in table.iterrows():
            if str(row[0]) not in self.neu.keys():
                neu = self.add_neuron(str(row[0]))
                if row[2] < 0:
                    neu.add_target(str(row[1]), 'GABA', -1 * row[2], 1)
                else:
                    neu.add_target(str(row[1]), excitatory_receptor, row[2], 1)
            else:
                if row[2] < 0:
                    self.neu[str(row[0])][1].add_target(str(row[1]), 'GABA', -1 * row[2], 1)
                else:
                    self.neu[str(row[0])][1].add_target(str(row[1]), excitatory_receptor, row[2], 1)


    def regenerate_network(self, conf_file='network.conf', pro_file='network.pro', track_mode=False):
        import os

        def read_param(fin, end_sign):
            param_dict = {}
            while True:
                line2 = fin.readline()
                if line2.strip('\n') == end_sign:
                    break
                line2 = line2.strip().split('=')
                line2[1] = line2[1].strip(' ')
                try:
                    param_dict[line2[0]] = float(line2[1])
                except ValueError:
                    param_dict[line2[0]] = line2[1]
            return param_dict

        if os.path.exists(conf_file):
            conf = open(conf_file, 'rt')
            for line in conf:

                if line.startswith('NeuralPopulation'):
                    neu_name = line.split(':')[1].strip(' \n')
                    param = read_param(conf, '')
                    self.add_neuron(neu_name, *param.values())

                if line.startswith('Receptor'):
                    receptor_name = line.split(':')[1].strip(' \n')
                    param = read_param(conf, 'EndReceptor')
                    self.neu[neu_name][1].add_receptor(Receptor(receptor_name, *param.values()))

                if line.startswith('TargetPopulation'):
                    tar_name = line.split(':')[1].strip(' \n')
                    param = read_param(conf, 'EndTargetPopulation')
                    self.add_target(neu_name, tar_name, *param.values())

            conf.close()

        if os.path.exists(pro_file):
            pro = open(pro_file, 'rt')
            for line in pro:

                if line.startswith('GroupName'):
                    group_name = line.split(':')[1].strip(' \n')
                    group_member = pro.readline().split(':')[1].strip(' \n').split(',')
                    self.add_group(group_name, *group_member)

                if line.startswith('EventTime'):
                    event_time = int(line.split(' ')[1].strip(' \n'))
                    event_type = pro.readline().split('=')[1].strip(' \n')
                    if event_type == 'EndTrial':
                        self.add_event(event_time, event_type)
                    else:
                        next_line = pro.readline()
                        if next_line.startswith('Label'):
                            next_line = pro.readline()
                        population = next_line.split(':')[1].strip(' \n')

                        if event_type == 'ChangeMembraneNoise':
                            GaussMean = float(pro.readline().split('=')[1].strip(' \n'))
                            GaussSTD = float(pro.readline().split('=')[1].strip(' \n'))
                            if track_mode is True:
                                self.add_track_event(event_time, event_type, population, GaussMean, GaussSTD)
                            else:
                                self.add_event(event_time, event_type, population, GaussMean, GaussSTD)

                        elif event_type == 'ChangeExtFreq':
                            receptor = pro.readline().split('=')[1].strip(' \n')
                            FreqExt = float(pro.readline().split('=')[1].strip(' \n'))
                            if track_mode is True:
                                self.add_track_event(event_time, event_type, population, receptor, FreqExt)
                            else:
                                self.add_event(event_time, event_type, population, receptor, FreqExt)

                if line.startswith('FileName'):
                    file_name = line.split(':')[1].strip(' \n')
                    param = read_param(pro, 'EndOutputFile')
                    self.add_output(file_name, *param.values())

            pro.close()


# Conf File ----------------------------------------------

class NeuralPopulation():

    def __init__(self, name, N=0, C=0, Taum=0, RestPot=0, ResetPot=0, Threshold=0, RefactoryPeriod=-1, SpikeDly=-1):
        self.name = name
        self.N = N
        self.C = C
        self.Taum = Taum
        self.RestPot = RestPot
        self.ResetPot = ResetPot
        self.Threshold = Threshold
        self.RefactoryPeriod = RefactoryPeriod
        self.SpikeDly = SpikeDly
        self.receptor = []
        self.target = {}
        self.LTP = False
        self.SelfConnection = False
        self.innervation = {
                'den': [],
                'axon': []
                }

    def set_param(self, N, C, Taum, RestPot, ResetPot, Threshold, RefactoryPeriod, SpikeDly):
        self.N = N
        self.C = C
        self.Taum = Taum
        self.RestPot = RestPot
        self.ResetPot = ResetPot
        self.Threshold = Threshold
        self.RefactoryPeriod = RefactoryPeriod
        self.SpikeDly = SpikeDly

    def add_receptor(self, receptor):
        self.receptor.append(receptor)

    def add_target(self, name, TargetReceptor='', MeanEff=0, weight=0):
        self.target[(name, TargetReceptor)] = Target(name, TargetReceptor, MeanEff, weight)

    def set_LTP(self, tLP, PosISI, NegISI):
        self.LTP = True
        self.tLP = tLP
        self.PosISI = PosISI
        self.NegISI = NegISI

    def add_innervation(self, polarity, region):
        self.innervation[polarity].extend(region)

    def output(self, fout):
        fout.write(
                'NeuralPopulation: ' + self.name + '\n' +
                'N=' + str(self.N) + '\n' +
                'C=' + str(self.C) + '\n' +
                'Taum=' + str(self.Taum) + '\n' +
                'RestPot=' + str(self.RestPot) + '\n' +
                'ResetPot=' + str(self.ResetPot) + '\n' +
                'Threshold=' + str(self.Threshold) + '\n'
                )

        if self.RefactoryPeriod >= 0:
            fout.write(
                'RefactoryPeriod=' + str(self.RefactoryPeriod) + '\n'
                )
        if self.SpikeDly >= 0:
            fout.write(
                'SpikeDly=' + str(self.SpikeDly) + '\n'
                )

        fout.write('\n')

        if self.LTP is True:
            fout.write(
                    'LTP_tLP=' + str(self.tLP) + '\n' +
                    'LTP_PosISI=' + str(self.PosISI) + '\n' +
                    'LTP_NegISI=' + str(self.NegISI) + '\n\n'
                    )
        if self.SelfConnection is True:
            fout.write('SelfConnection=true' + '\n\n')

        for receptor in self.receptor:
            fout.write(
                'Receptor: ' + str(receptor.name) + '\n' +
                'Tau=' + str(receptor.Tau) + '\n' +
                'RevPot=' + str(receptor.RevPot) + '\n' +
                'FreqExt=' + str(receptor.FreqExt) + '\n' +
                'MeanExtEff=' + str(receptor.MeanExtEff) + '\n' +
                'MeanExtCon=' + str(receptor.MeanExtCon) + '\n' +
                'EndReceptor' + '\n\n'
                )
        for target in self.target.values():
            fout.write(
                'TargetPopulation: ' + str(target.name) + '\n' +
                'TargetReceptor=' + str(target.TargetReceptor) + '\n' +
                'MeanEff=' + str(target.MeanEff) + '\n' +
                'weight=' + str(target.weight) + '\n' +
                'EndTargetPopulation' + '\n\n'
                )
        fout.write('EndNeuralPopulation' + '\n\n\n')


class Receptor():

    def __init__(self, name, Tau=0, RevPot=0, FreqExt=0, MeanExtEff=0, MeanExtCon=0):
        self.name = name
        self.Tau = Tau
        self.RevPot = RevPot
        self.FreqExt = FreqExt
        self.MeanExtEff = MeanExtEff
        self.MeanExtCon = MeanExtCon

    def set_param(self, Tau, RevPot, FreqExt, MeanExtEff, MeanExtCon):
        self.Tau = Tau
        self.RevPot = RevPot
        self.FreqExt = FreqExt
        self.MeanExtEff = MeanExtEff
        self.MeanExtCon = MeanExtCon


class Target():

    def __init__(self, name, TargetReceptor='', MeanEff=0, weight=0):
        self.name = name
        self.TargetReceptor = TargetReceptor
        self.MeanEff = MeanEff
        self.weight = weight

    def set_param(self, TargetReceptor, MeanEff, weight):
        self.TargetReceptor = TargetReceptor
        self.MeanEff = MeanEff
        self.weight = weight


# Pro File -----------------------------------------------

class Group():

    def __init__(self, name):
        self.name = name
        self.member = []

    def add_member(self, member_name):
        self.member.append(member_name)

    def add_member_list(self, member_list):
        self.member.extend(member_list)

    def output(self, fout):
        fout.write(
                'GroupName:' + str(self.name) + '\n' +
                'GroupMembers:')
        print(*self.member, sep=',', file=fout)
        fout.write('EndGroupMembers' + '\n\n')


class Event():

    def __init__(self, time, event_type, *args):
        self.time = time
        self.type = event_type
        if event_type == 'ChangeMembraneNoise':
            self.population = args[0]
            self.GaussMean = args[1]
            self.GaussSTD = args[2]
        elif event_type == 'ChangeExtFreq':
            self.population = args[0]
            self.Receptor = args[1]
            self.FreqExt = args[2]
        elif event_type == 'EndTrial':
            pass

    def output(self, fout):
        if self.type == 'ChangeMembraneNoise':
            fout.write(
                    'EventTime ' + str(self.time) + '\n' +
                    'Type=ChangeMembraneNoise' + '\n' +
                    'Population: ' + self.population + '\n' +
                    'GaussMean=' + str(self.GaussMean) + '\n' +
                    'GaussSTD=' + str(self.GaussSTD) + '\n' +
                    'EndEvent' + '\n\n'
                    )

        elif self.type == 'ChangeExtFreq':
            fout.write(
                    'EventTime ' + str(self.time) + '\n' +
                    'Type=ChangeExtFreq' + '\n' +
                    'Population: ' + self.population + '\n' +
                    'Receptor=' + str(self.Receptor) + '\n' +
                    'FreqExt=' + str(self.FreqExt) + '\n' +
                    'EndEvent' + '\n\n'
                    )
        elif self.type == 'EndTrial':
            fout.write(
                    'EventTime ' + str(self.time) + '\n' +
                    'Type=EndTrial' + '\n' +
                    'EndEvent' + '\n\n\n'
                    )


class Output():

    def __init__(self, file_name, output_type, population, *args):
        self.check_output_type(output_type)
        if output_type == 'M':
            output_type = 'MemPot'
        if output_type == 'S':
            output_type = 'Spike'
        if output_type == 'F':
            output_type = 'FiringRate'

        self.file_name = file_name
        self.type = output_type
        self.population = population
        if output_type == 'FiringRate':
            self.FiringRateWindow = args[0]
            self.PrintStep = args[1]

    def output(self, fout):
        if self.type == 'FiringRate':
            fout.write(
                    'FileName: ' + self.file_name + '\n' +
                    'Type=' + self.type + '\n' +
                    'population=' + self.population + '\n' +
                    'FiringRateWindow=' + str(self.FiringRateWindow) + '\n' +
                    'PrintStep=' + str(self.PrintStep) + '\n' +
                    'EndOutputFile' + '\n\n'
                    )
        else:
            fout.write(
                    'FileName: ' + self.file_name + '\n' +
                    'Type=' + self.type + '\n' +
                    'population=' + self.population + '\n' +
                    'EndOutputFile' + '\n\n'
                    )

    def check_output_type(self, output_type):
        if output_type not in ['M', 'MemPot', 'S', 'Spike', 'F', 'FiringRate']:
            raise Exception(f'We don\'t support this output type [{output_type}].')
