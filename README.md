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
- The segment anything model with vit_b [[Google drive](https://drive.google.com/file/d/15MIZgQ276UCkyz8zcA6yf1BzRcS-Q8eM/view?usp=drive_link)]
- 
- A standard-sized model trained on LOL [[Google drive](https://drive.google.com/file/d/1t3kASTRXbnEnCZ0EcIvGhMHYkoJ8E2C4/view?usp=sharing)] with training config file `./confs/LOL-pc.yml`.
- A standard-sized model trained on LOL-v2 [[Google drive](https://drive.google.com/file/d/1n7XwIlNr1lUxgZ9qlmFXCwzMTWSStQIW/view?usp=sharing)] with training config file `./confs/LOLv2-pc.yml`.

