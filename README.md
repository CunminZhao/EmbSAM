# [ArXiv] EmbSAM: Cell boundary localization and Segment Anything Model for 3D fast-growing embryos
<br>_Cunmin Zhao<sup>#</sup>, Zelin Li<sup>#</sup>, Ming-Kin Wong, Lu-Yan Chan, Hong Yan, Chao Tang, Guoye Guan<sup>\*</sup>, Zhongying Zhao<sup>\*</sup>_<br>
In [ArXiv]  
<sup>#</sup> Equal contribution,
<sup>*</sup> Correspondence Author.

**Motivations**: Fluorescence imaging on cell membranes would exhibit a low signal-to-noise ratio (SNR) under common experimental conditions. As embryonic development involves cell deformation, migration, division, and differentiation as fast as seconds to minutes, customized fluorescence imaging at high temporal resolution requests a weak laser intensity to limit photobleaching and phototoxicity, leading to a low SNR that impedes three-dimensional (3D) shape reconstruction across cellular to organismic scales.  
**Results**: We devised a computational framework, EmbSAM, which incorporates a deep-learning-based cell boundary localization algorithm and the Segment Anything Model. With the nematode Caenorhabditis elegans embryos, EmbSAM outperforms the latest cell segmentation tools and rebuilds all the 3D cell shapes up to the gastrulation onset at 10-second intervals. The outputted data can clearly illustrate cell shape changes related to cell division, body axis establishment, and cell migration.  



## Overall
<img width="900" alt="Ai" src="https://github.com/cuminzhao/EmbSAM/assets/80189429/c59d7d4f-e53f-44a7-8a9c-5f2efec8df19">      


**Fig. 1. The flowchart of EmbSAM**
## Get Started
### Dependencies and Installation
- Python 3.11.0
- Pytorch 2.0.1

1. Create Conda Environment
```
conda create --name EmbSAM python=3.11.0
conda activate EmbSAM
conda install anaconda::git
```
2. Clone Repo
```
git clone https://github.com/cuminzhao/EmbSAM.git
```
3. Install Dependencies
```
cd EmbSAM
pip install -r ./requirement.txt
```

### Dataset
You can refer to the following links to download the datasets
[190311plc1mp1_raw.zip](https://drive.google.com/file/d/1SuLN8iG_siZlKvDuMIbYknOVR8WY4Axu/view?usp=drive_link), 
[190311plc1mp3_raw.zip](https://drive.google.com/file/d/1uL9M1xOuXyR36clcs0csCi-bLYWrYdg3/view?usp=drive_link). and
[cell_membrane_10s.zip](https://drive.google.com/file/d/1t0MxzF-48Gp6BWrEhGM-abljXOTefYAC/view?usp=sharing)


### Pre-trained Model
the pre-trained models of this project can be downloaded here
- The model_parameters with segment anything model(vit_b) and the image denosing model trained on x_axis, y_axis and z_axis [[model_parameters](https://drive.google.com/drive/folders/1vNp7KypEOxTXCxHLS6N4kET1M_cfBtup?usp=drive_link)]. You need to download these parameters and put them into model_parameters.
* **Structure of model_parameters**: 
    ```buildoutcfg
    model_parameters/
      |--Z_axis.pth
      |--Y_axis.pth
      |--X_axis.pth
      |--sam_vit_b_01ec64.pth
    ```

### Test  
**Example1**: to run EmbSAM with 190311plc1mp1_raw, you need to keep these data in
* **Structure of data folder**: 
    ```buildoutcfg
    data/
      |--190311plc1mp1_raw/*.tif
    ```
* **Structure of confs folder**: 
    ```buildoutcfg
    confs/
      |--CD190311plc1mp1.csv
      |--running_190311plc1mp1.txt
      ...
      |--other running confs
    ```
Then run
```
python EmbSAM.py -cfg_path ./confs/running_190311plc1mp1.txt
```

**Example2**: to run EmbSAM with cell_membrane_10s, you need to keep these data in
* **Structure of data folder**: 
    ```buildoutcfg
    data/
      |--/cell_membrane_10s/*.tif
    ```
* **Structure of confs folder**: 
    ```buildoutcfg
    confs/
      |--DataS1_CellTracing.csv
      |--running_Mem.txt
      ...
      |--other running confs
    ```
Then run
```
python EmbSAM.py -cfg_path ./confs/running_Mem.txt 
```

you will get your result in 
```
./output_folder/result
```

## To do list
- [ ] add Training script for custom dataset
- [ ] add script to calculate the Dice and Hausdroff
## Acknowledgement
- The design of the segmentation algorithm is inspired by [CShaper](https://github.com/cao13jf/CShaper) and [MedLSAM](https://github.com/openmedlab/MedLSAM).
- A part of code is modified from [llflow](https://github.com/wyf0912/LLFlow).
- We thank Meta AI for making the source code of [segment anything](https://github.com/facebookresearch/segment-anything) publicly available.
