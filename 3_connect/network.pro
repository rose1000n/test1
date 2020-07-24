%(1, 'ChangeMembraneNoise', '10', 4, 0)
%(500, 'EndTrial')

%--------------------------------

EventTime 1
Type=ChangeMembraneNoise
Population: 10
GaussMean=4
GaussSTD=0
EndEvent

EventTime 500
Type=EndTrial
EndEvent


%--------------------------------

OutControl

FileName: FiringRateALL.dat
Type=FiringRate
population=10
FiringRateWindow=100
PrintStep=10
EndOutputFile

FileName: SpikeALL.dat
Type=Spike
population=AllPopulation
EndOutputFile

FileName: MemPot.dat
Type=MemPot
population=AllPopulation
EndOutputFile

EndOutControl
