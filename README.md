# [ArXiv] EmbSAM: Cell boundary localization and Segment Anything Model for 3D fast-growing embryos
<br>_Cunmin Zhao, Zelin Li, Hong Yan, Chao Tang, Guoye Guan, Zhongying Zhao_<br>
In [ArXiv]  

**Motivations**: Embryonic development involves cell deformation, migration, division, and differentiation, which can be as fast as in seconds to minutes. Due to photobleaching and phototoxicity, fluorescence imaging at high temporal resolution requests a weak laser intensity, leading to a low signal-to-noise ratio. This shortcoming impedes three-dimensional (3D) shape reconstruction across cellular to organismic scales. 
  
**Results**: We devised a computational framework, EmbSAM, which incorporates a deep-learning-based cell boundary localization algorithm and the Segment Anything Model proposed before. Using the 3D fluorescence images on cell membranes in the nematode Caenorhabditis elegans embryos, EmbSAM outperforms the latest cell segmentation tools and rebuilds all the 3D cell shapes up to the gastrulation stage at 10-second intervals. The outputted data can clearly exhibit critical cell and developmental biological processes, including cytokinesis, body-axis symmetry breaking, cell migration, and gastrulation.  


## Overall
<img width="600" alt="Ai" src="https://github.com/cuminzhao/EmbSAM/assets/80189429/9fb048d2-23f9-42e9-b954-1534ed79c84d"> 

## Get Started
### Dependencies and Installation
- Python 3.XX
- Pytorch X.XX

1. Clone Repo
```
git clone https://github.com/cuminzhao/EmbSAM.git
```
2. Create Conda Environment
```
conda create --name EmbSAM python=3.XX
conda activate EmbSAM
```
3. Install Dependencies
```
cd EmbSAM
pip install -r ./requirements.txt
```

### Dataset
You can refer to the following links to download the datasets
[raw_data1_with_90s_interval](https://drive.google.com/file/d/1SuLN8iG_siZlKvDuMIbYknOVR8WY4Axu/view?usp=sharing), 
[raw_data2_with_90s_interval](https://drive.google.com/file/d/1uL9M1xOuXyR36clcs0csCi-bLYWrYdg3/view?usp=sharing). and
[raw_data3_with_10s_interval](https://drive.google.com/file/d/1t0MxzF-48Gp6BWrEhGM-abljXOTefYAC/view?usp=sharing)
