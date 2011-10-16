DecoyPrefix = ""
MonoPrecursorMzTolerance = $PRECMASSERR $PRECMASSUNIT
FragmentMzTolerance = $FRAGMASSERR $FRAGMASSUNIT

PrecursorMzToleranceRule = "mono"
FragmentationRule= "cid"
FragmentationAutoRule = false
NumIntensityClasses = 3
ClassSizeMultiplier = 2

NumChargeStates = 3
UseSmartPlusThreeModel = true
TicCutoffPercentage = 0.95

CleavageRules = "trypsin"
MaxMissedCleavages = 0
MinTerminiCleavages =  2
MinPeptideLength =  6
MaxPeptideLength = 75
MaxPeptideMass = 6500
MinPeptideMass = 500
DynamicMods = ""
MaxDynamicMods = 0
StaticMods = "C 57.021464"

MaxResultRank = 1
ComputeXCorr = true
NumBatches = 50
ThreadCountMultiplier = 10
UseMultipleProcessors = true