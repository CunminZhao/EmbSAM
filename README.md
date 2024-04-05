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
- The segment anything model with vit_b [[sam_vit_b_01ec64.pth](https://drive.google.com/file/d/15MIZgQ276UCkyz8zcA6yf1BzRcS-Q8eM/view?usp=drive_link)]
- The image denosing model trained on x_axis [[X_axis.pth](https://drive.google.com/file/d/1ef4jBB2OdSfkg0W5737XxzCx2G0zT7FO/view?usp=sharing)] 
- The image denosing model trained on y_axis [[Y_axis.pth](https://drive.google.com/file/d/1F8hNc82VuBdZuHmLy0vktgIBhpSkIrIx/view?usp=sharing)]
- The image denosing model trained on z_axis [[Z_axis.pth](https://drive.google.com/file/d/1xNcYA_Vquv33YU2b4SugVyzEkOtK5JmX/view?usp=sharing)]


