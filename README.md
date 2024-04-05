# [ArXiv] EmbSAM: Cell boundary localization and Segment Anything Model for 3D fast-growing embryos
<br>_Cunmin Zhao, Zelin Li, Hong Yan, Chao Tang, Guoye Guan, Zhongying Zhao_<br>
In [ArXiv]  

**Motivations**: XXX
  
**Results**: XXX 


## Overall
<img width="900" alt="Ai" src="https://github.com/cuminzhao/EmbSAM/assets/80189429/9fb048d2-23f9-42e9-b954-1534ed79c84d"> 



## Get Started
the code is not totally uploaded and test, please do not start
### Dependencies and Installation
- Python 3.11.0
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
pip install -r ./requirement.txt
```

### Dataset
You can refer to the following links to download the datasets
[190311plc1mp1_raw.zip](https://drive.google.com/file/d/1SuLN8iG_siZlKvDuMIbYknOVR8WY4Axu/view?usp=drive_link), 
[190311plc1mp3_raw.zip](https://drive.google.com/file/d/1uL9M1xOuXyR36clcs0csCi-bLYWrYdg3/view?usp=drive_link). and
[10s_data_from_guoye.zip](https://drive.google.com/file/d/1L3EkZ1URrJ6ABQoVC1Rnpt9fE4I6ssuc/view?usp=drive_link)


### Pretrained Model
the pre-trained models of this project can be download here
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
      |--running_190311plc1mp3.txt
      ...
      |--other running confs
    ```
Then run
```
python EmbSAM.py -cfg_path ./confs/running_190311plc1mp1.txt
```

**Example2**: to run EmbSAM with 10s_data_from_guoye, you need to keep these data in
* **Structure of data folder**: 
    ```buildoutcfg
    data/
      |--10s_data_from_guoye/*.tif
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
### Train
```
will be uploaded soon
```


to be continue...
