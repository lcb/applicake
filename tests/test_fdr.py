#!/usr/bin/env python2.7
import os
import shutil
import tempfile
import unittest

from appliapps.tpp.fdr import get_iprob_for_fdr


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tdir = tempfile.mkdtemp(dir=".")
        os.chdir(cls.tdir)
        with open("mayuout_main_1.07.csv", "w") as f:
            f.write("""nr_runs,nr_files,mFDR,IP/PPs,target_PSM,decoy_PSM,FP_PSM,TP_PSM,target_pepID,decoy_pepID,FP_pepID,FP_pepID_stdev,TP_pepID,pepFDR,target_protID,decoy_protID,FP_protID,FP_protID_stdev,TP_protID,protFDR,target_protIDs,decoy_protIDs,FP_protIDs,TP_protIDs,protFDRs,target_protIDns,decoy_protIDns,FP_protIDns,TP_protIDns,protFDRns
3,1,0,0.989757,3189,0,0,3189,520,0,0,0.00000000,520,0.00000000,58,0,0,0.00000000,58,0.00000000,1,0,0,1,0.00000000,57,0,0,57,0.00000000
3,1,0.0005,0.988996,3209,1,1,3208,522,1,1,0.25703663,521,0.00177945,58,1,0,0.34992711,58,0.00246305,1,1,0,1,0.14285714,57,0,0,57,0.00000000
3,1,0.001,0.978287,3354,3,3,3351,541,1,1,0.26130777,540,0.00171217,58,1,0,0.34992711,58,0.00246305,1,0,0,1,0.00000000,57,1,0,57,0.00250627
3,1,0.0015,0.968018,3436,5,5,3431,547,3,3,0.45425360,544,0.00507707,58,3,1,0.69229543,57,0.01139163,1,2,0,1,0.44047619,57,1,0,57,0.00386383
3,1,0.002,0.95758,3486,6,6,3480,551,3,3,0.45578326,548,0.00503724,58,3,1,0.69229543,57,0.01139163,1,2,0,1,0.44047619,57,1,0,57,0.00386383
3,1,0.0025,0.945814,3526,8,8,3518,557,5,5,0.59053373,552,0.00829989,58,5,1,0.95831485,57,0.02216749,1,4,1,-0,1.02857143,57,1,0,57,0.00451128
3,1,0.003,0.935662,3560,10,10,3550,560,6,6,0.64805520,554,0.00990348,58,6,1,1.05516761,57,0.02545156,1,5,1,-0,1.23015873,57,1,0,57,0.00431635
3,1,0.0035,0.925491,3594,12,12,3582,565,8,7,0.75035956,558,0.01308170,58,8,2,1.19069938,56,0.03089080,1,7,2,-1,1.56770833,57,1,0,57,0.00392909
3,1,0.004,0.916488,3623,14,14,3609,568,9,8,0.79728805,560,0.01463470,58,9,2,1.35315569,56,0.04197455,1,7,2,-1,1.89351852,57,2,1,56,0.00949132
3,1,0.0045,0.910972,3635,16,16,3619,569,11,10,0.88094319,559,0.01785765,58,10,3,1.38335641,55,0.04354195,1,7,2,-1,1.76780303,57,3,1,56,0.01329175
3,1,0.005,0.874862,3705,18,18,3687,572,11,10,0.88310818,562,0.01775612,59,10,2,1.34407295,57,0.03432937,2,5,1,1,0.50635823,57,5,1,56,0.01776696
3,1,0.0055,0.861569,3722,20,20,3702,574,12,11,0.92324918,563,0.01929975,59,10,2,1.34407295,57,0.03432937,2,4,1,1,0.40508658,57,6,1,56,0.02132035
3,1,0.006,0.83055,3772,22,22,3750,578,13,12,0.96341736,566,0.02075393,59,11,3,1.54576494,56,0.04449886,2,5,1,1,0.59668930,57,6,1,56,0.02512376
3,1,0.0065,0.803986,3810,24,24,3786,581,14,13,1.00153308,568,0.02222814,59,12,3,1.64679353,56,0.04901864,2,5,1,1,0.60252074,57,7,2,55,0.02959751
3,1,0.007,0.799483,3817,26,26,3791,582,14,13,1.00234016,569,0.02218667,59,12,3,1.64679353,56,0.04901864,2,5,1,1,0.60252074,57,7,2,55,0.02959751
3,1,0.0075,0.75728,3852,28,28,3824,589,16,15,1.07612743,574,0.02503572,59,14,3,1.72842099,56,0.05386125,1,7,2,-1,1.58890693,58,7,2,56,0.02739495
3,1,0.008,0.754957,3878,30,30,3848,592,18,17,1.14261341,575,0.02801766,59,15,3,1.81933472,56,0.05838103,1,7,2,-1,1.60742424,58,8,2,56,0.03167338
3,1,0.0085,0.754957,3878,32,32,3846,592,19,18,1.17314275,574,0.02957823,59,15,3,1.81933472,56,0.05838103,1,5,1,-0,1.14816017,58,10,2,56,0.03959173
3,1,0.009,0.745937,3885,34,34,3851,593,20,18,1.20377649,575,0.03108211,59,16,4,1.96722617,55,0.06516069,1,6,1,-0,1.44168019,58,10,2,56,0.04142759""")
        with open("iprophet.pep.xml", "w") as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<msms_pipeline_analysis date="2014-07-02T00:17:27" xmlns="http://regis-web.systemsbiology.net/pepXML" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://regis-web.systemsbiology.net/pepXML /tools/bin/TPP/tpp/schema/pepXML_v18.xsd" summary_xml="/cluster/scratch_xp/shareholder/imsb_ra/workflows//1407020005/InterProphet/iprophet.pep.xml">
<analysis_summary analysis="interprophet" time="2014-07-02T00:17:27">
<inputfile name="/cluster/scratch_xp/shareholder/imsb_ra/workflows//1407020005/DATASET_CODE_0/InterProphet/iprophet.pep.xml"/>
<inputfile name="/cluster/scratch_xp/shareholder/imsb_ra/workflows//1407020005/DATASET_CODE_1/InterProphet/iprophet.pep.xml"/>
<inputfile name="/cluster/scratch_xp/shareholder/imsb_ra/workflows//1407020005/DATASET_CODE_2/InterProphet/iprophet.pep.xml"/>
<roc_data_point min_prob="0.9999" sensitivity="0.5783" error="0.0000" num_corr="2647" num_incorr="0"/>
<roc_data_point min_prob="0.9990" sensitivity="0.6198" error="0.0000" num_corr="2837" num_incorr="0"/>
<roc_data_point min_prob="0.9900" sensitivity="0.6948" error="0.0005" num_corr="3180" num_incorr="2"/>
<roc_data_point min_prob="0.9800" sensitivity="0.7295" error="0.0012" num_corr="3339" num_incorr="4"/>
<roc_data_point min_prob="0.9500" sensitivity="0.7670" error="0.0027" num_corr="3510" num_incorr="10"/>
<roc_data_point min_prob="0.9000" sensitivity="0.7988" error="0.0057" num_corr="3656" num_incorr="21"/>
<roc_data_point min_prob="0.8500" sensitivity="0.8139" error="0.0082" num_corr="3725" num_incorr="31"/>
<roc_data_point min_prob="0.8000" sensitivity="0.8294" error="0.0119" num_corr="3796" num_incorr="46"/>
<roc_data_point min_prob="0.7500" sensitivity="0.8417" error="0.0159" num_corr="3853" num_incorr="62"/>
<roc_data_point min_prob="0.7000" sensitivity="0.8531" error="0.0206" num_corr="3905" num_incorr="82"/>
<roc_data_point min_prob="0.6500" sensitivity="0.8624" error="0.0254" num_corr="3947" num_incorr="103"/>
<roc_data_point min_prob="0.6000" sensitivity="0.8722" error="0.0315" num_corr="3992" num_incorr="130"/>
<roc_data_point min_prob="0.5500" sensitivity="0.8804" error="0.0378" num_corr="4030" num_incorr="158"/>
<roc_data_point min_prob="0.5000" sensitivity="0.8891" error="0.0456" num_corr="4070" num_incorr="194"/>
<roc_data_point min_prob="0.4500" sensitivity="0.8988" error="0.0558" num_corr="4114" num_incorr="243"/>
<roc_data_point min_prob="0.4000" sensitivity="0.9063" error="0.0653" num_corr="4148" num_incorr="290"/>
<roc_data_point min_prob="0.3500" sensitivity="0.9164" error="0.0804" num_corr="4194" num_incorr="367"/>
<roc_data_point min_prob="0.3000" sensitivity="0.9259" error="0.0975" num_corr="4238" num_incorr="458"/>
<roc_data_point min_prob="0.2500" sensitivity="0.9362" error="0.1198" num_corr="4285" num_incorr="583"/>
<roc_data_point min_prob="0.2000" sensitivity="0.9486" error="0.1523" num_corr="4342" num_incorr="780"/>
<roc_data_point min_prob="0.1500" sensitivity="0.9611" error="0.1934" num_corr="4399" num_incorr="1055"/>
<roc_data_point min_prob="0.1000" sensitivity="0.9733" error="0.2461" num_corr="4455" num_incorr="1454"/>
<roc_data_point min_prob="0.0500" sensitivity="0.9857" error="0.3260" num_corr="4512" num_incorr="2182"/>
<roc_data_point min_prob="0.0000" sensitivity="1.0000" error="0.9175" num_corr="4577" num_incorr="50930"/>
<error_point error="0.0000" min_prob="1.0000" num_corr="2" num_incorr="0"/>
<error_point error="0.0001" min_prob="0.9971" num_corr="2950" num_incorr="0"/>
<error_point error="0.0002" min_prob="0.9953" num_corr="3030" num_incorr="1"/>
<error_point error="0.0003" min_prob="0.9939" num_corr="3090" num_incorr="1"/>
<error_point error="0.0004" min_prob="0.9919" num_corr="3137" num_incorr="1"/>
<error_point error="0.0005" min_prob="0.9903" num_corr="3173" num_incorr="2"/>
<error_point error="0.0006" min_prob="0.9892" num_corr="3206" num_incorr="2"/>
<error_point error="0.0007" min_prob="0.9877" num_corr="3235" num_incorr="2"/>
<error_point error="0.0008" min_prob="0.9861" num_corr="3261" num_incorr="3"/>
<error_point error="0.0009" min_prob="0.9845" num_corr="3284" num_incorr="3"/>
<error_point error="0.0010" min_prob="0.9830" num_corr="3306" num_incorr="3"/>
<error_point error="0.0015" min_prob="0.9748" num_corr="3390" num_incorr="5"/>
<error_point error="0.0020" min_prob="0.9658" num_corr="3450" num_incorr="7"/>
<error_point error="0.0025" min_prob="0.9553" num_corr="3495" num_incorr="9"/>
<error_point error="0.0030" min_prob="0.9444" num_corr="3530" num_incorr="11"/>
<error_point error="0.0040" min_prob="0.9278" num_corr="3586" num_incorr="14"/>
<error_point error="0.0050" min_prob="0.9122" num_corr="3630" num_incorr="18"/>
<error_point error="0.0060" min_prob="0.8951" num_corr="3667" num_incorr="22"/>
<error_point error="0.0070" min_prob="0.8773" num_corr="3697" num_incorr="26"/>
<error_point error="0.0080" min_prob="0.8550" num_corr="3723" num_incorr="30"/>
<error_point error="0.0090" min_prob="0.8395" num_corr="3745" num_incorr="34"/>
<error_point error="0.0100" min_prob="0.8264" num_corr="3765" num_incorr="38"/>
<error_point error="0.0150" min_prob="0.7587" num_corr="3842" num_incorr="59"/>
<error_point error="0.0200" min_prob="0.7058" num_corr="3900" num_incorr="80"/>
<error_point error="0.0250" min_prob="0.6524" num_corr="3945" num_incorr="102"/>
<error_point error="0.0300" min_prob="0.6078" num_corr="3982" num_incorr="124"/>
<error_point error="0.0400" min_prob="0.5302" num_corr="4043" num_incorr="169"/>
<error_point error="0.0500" min_prob="0.4805" num_corr="4090" num_incorr="216"/>
<error_point error="0.0750" min_prob="0.3712" num_corr="4179" num_incorr="340"/>
<error_point error="0.1000" min_prob="0.2939" num_corr="4244" num_incorr="473"/>

<mixturemodel name="NSS" pos_bandwidth="0.1" neg_bandwidth="0.1">
</mixturemodel>
<mixturemodel name="NRS" pos_bandwidth="3.002" neg_bandwidth="3.002">
<point value="-15.01" pos_dens="0.00212685" neg_dens="0.0156122" neg_obs_dens="0.0160947" pos_obs_dens="0.00224026"/>
<point value="-14.9498" pos_dens="0.00217388" neg_dens="0.0159221" neg_obs_dens="0.0164127" pos_obs_dens="0.00228702"/>
<point value="-14.8897" pos_dens="0.00222162" neg_dens="0.0162347" neg_obs_dens="0.0167335" pos_obs_dens="0.00233441"/>
<point value="-14.8295" pos_dens="0.00227009" neg_dens="0.01655" neg_obs_dens="0.017057" pos_obs_dens="0.00238243"/>
<point value="-14.7694" pos_dens="0.00231929" neg_dens="0.016868" neg_obs_dens="0.0173831" pos_obs_dens="0.00243108"/>
<point value="-14.7092" pos_dens="0.00236923" neg_dens="0.0171887" neg_obs_dens="0.017712" pos_obs_dens="0.00248037"/>
<point value="-14.649" pos_dens="0.00241993" neg_dens="0.0175119" neg_obs_dens="0.0180434" pos_obs_dens="0.00253031"/>
<point value="-14.5889" pos_dens="0.00247138" neg_dens="0.0178377" neg_obs_dens="0.0183773" pos_obs_dens="0.00258091"/>
<point value="-14.5287" pos_dens="0.0025236" neg_dens="0.0181659" neg_obs_dens="0.0187138" pos_obs_dens="0.00263216"/>""")

    def test_fdr(self):
        iprob, fdr = get_iprob_for_fdr("0.004", "mayu-mFDR", mayuout='mayuout_main_1.07.csv')
        assert iprob == 0.916488

        iprob, fdr = get_iprob_for_fdr("0.025", "mayu-pepFDR", mayuout='mayuout_main_1.07.csv')
        assert iprob == 0.75728

        iprob, fdr = get_iprob_for_fdr("0.05", "mayu-protFDR", mayuout='mayuout_main_1.07.csv')
        assert iprob == 0.803986

        iprob, fdr = get_iprob_for_fdr("0.025", "iprophet-pepFDR", pepxml="iprophet.pep.xml")
        assert iprob == 0.6524

        self.assertRaises(RuntimeError, get_iprob_for_fdr, "0.1234", "iprophet-pepFDR", pepxml="iprophet.pep.xml")


    @classmethod
    def tearDownClass(cls):
        os.chdir("..")
        shutil.rmtree(cls.tdir)


if __name__ == "__main__":
    unittest.main()
