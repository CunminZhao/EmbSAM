# [ArXiv] EmbSAM: Cell boundary localization and Segment Anything Model for 3D fast-growing embryos
<br>_Cunmin Zhao, Zelin Li, Hong Yan, Chao Tang, Guoye Guan, Zhongying Zhao_<br>
In [ArXiv]  

**Motivations**: XXX
  
**Results**: XXX 


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

### Pretrained Model
the pre-trained models of this project can be download here
- The model_parameters with segment anything model(vit_b) and the image denosing model trained on x_axis, y_axis and z_axis [[model_parameters](https://drive.google.com/drive/folders/1vNp7KypEOxTXCxHLS6N4kET1M_cfBtup?usp=drive_link)]


* **Structure of folders**: 
    ```buildoutcfg
    DMapNet is used to segmented membrane stack of C. elegans at cellular level
    DMapNet/
      |--configmemb/: parameters for training, testing and unifying label
      |--Data/: raw membrane, raw nucleus and AceTree file (CD**.csv)
          |--MembTraining/: image data with manual annotations
          |--MembValidation/: image data to be segmented
      |--ModelCell/: trained models 
      |--ResultCell/: Segmentation result
          |--BothWithRandomnet/: Binary membrane segmentation from DMapNet
          |--BothWithRandomnetPostseg/: segmented cell before and after label unifying
          |--NucleusLoc/: nucleus location information and annotation
          |--StatShape/: cell lineage tree (with time duration)
      |--ShapeUtil/: utils for unifying cells and calculating robustness
          |--AceForLabel/: multiple AceTree files for generating namedictionary
          |--RobustStat/: nucleus lost sration and cell surface...
          |--TemCellGraph/: temporary result for calculating surface, volume...
        
      |--Util/: utils for training and testing
    ```




