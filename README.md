# Segment Annotator

An annotation tool for creating labeled segmentation datasets. 

## Installation

Clone the repository locally:

```shell
git clone https://github.com/Steven-Holland/segment-annotator.git
```

Create the conda env using `python>=3.10`. Please follow the instructions [here](https://pytorch.org/get-started/locally/) to install both PyTorch and TorchVision dependencies. Installing both PyTorch and TorchVision with CUDA support is strongly recommended.

```shell
conda create -n Annotator python=3.10
conda activate Annotator
```

Install the packages:

```shell
cd segment-annotator
pip install -r requirements.txt
```

Download [SAM](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth) and [FastSAM](https://drive.google.com/file/d/1m1sjY4ihXBU1fZXdQ-Xdj-mDltW-2Rqv/view?usp=sharing) model checkpoints. Once they are downloaded, move them to `../src/assets/models`.

## Usage

Move into the `src` folder and run `main.py`
```shell
cd src
python main.py
```