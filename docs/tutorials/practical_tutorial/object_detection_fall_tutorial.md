# PaddleX 3.0 通用目标检测模型产线———行人跌倒检测教程

PaddleX 提供了丰富的模型产线，模型产线由一个或多个模型组合实现，每个模型产线都能够解决特定的场景任务问题。PaddleX 所提供的模型产线均支持快速体验，如果效果不及预期，也同样支持使用私有数据微调模型，并且 PaddleX 提供了 Python API，方便将产线集成到个人项目中。在使用之前，您首先需要安装 PaddleX， 安装方式请参考[ PaddleX 安装](../INSTALL.md)。此处以一个行人跌倒检测的任务为例子，介绍模型产线工具的使用流程。

## 1. 选择产线

首先，需要根据您的任务场景，选择对应的 PaddleX 产线，此处为行人跌倒检测，需要了解到这个任务属于目标检测任务，对应 PaddleX 的通用目标检测产线。如果无法确定任务和产线的对应关系，您可以在 PaddleX 支持的[模型产线列表](../pipelines/support_pipeline_list.md)中了解相关产线的能力介绍。


## 2. 快速体验

PaddleX 提供了两种体验的方式，一种是可以直接通过 PaddleX wheel 包在本地体验，另外一种是可以在 **AI Studio 星河社区**上体验。

  - 本地体验方式：
    ```bash
    paddlex --pipeline object_detection \
        --model PP-YOLOE_plus-S \
        --input https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/fall.png
    ```

  - 星河社区体验方式：前往[AI Studio 星河社区](https://aistudio.baidu.com/pipeline/mine)，点击【创建产线】，创建【**通用目标检测**】产线进行快速体验；

  快速体验产出推理结果示例：
  <center>

  <img src="https://github.com/user-attachments/assets/b194c08f-c837-4a1c-8b46-dc26b0ca88b4" width=600>

  </center>

当体验完该产线之后，需要确定产线是否符合预期（包含精度、速度等），产线包含的模型是否需要继续微调，如果模型的速度或者精度不符合预期，则需要根据模型选择选择可替换的模型继续测试，确定效果是否满意。如果最终效果均不满意，则需要微调模型。本教程希望产出检测行人是否跌倒的模型，显然默认的权重（COCO 数据集训练产出的权重）无法满足要求，需要采集和标注数据，然后进行训练微调。

## 3. 选择模型

PaddleX 提供了11个端到端的目标检测模型，具体可参考 [模型列表](../models/support_model_list.md)，其中部分模型的benchmark如下：

| 模型列表         | mAP(%) | GPU 推理耗时(ms) | CPU 推理耗时(ms) | 模型存储大小(M) |
| --------------- | ------ | ---------------- | ---------------- | --------------- |
| RT-DETR-H       | 56.3   | 100.65           | 8451.92          | 471             |
| RT-DETR-L       | 53.0   | 27.89            | 841.00           | 125             |
| PP-YOLOE_plus-L | 52.9   | 29.67            | 700.97           | 200             |
| PP-YOLOE_plus-S | 43.7   | 8.11             | 137.23           | 31              |
| PicoDet-L       | 42.6   | 10.09            | 129.32           | 23              |
| PicoDet-S       | 29.1   | 3.17             | 13.36            | 5               |

> **注：以上精度指标为 <a href="https://cocodataset.org/#home" target="_blank">COCO2017</a> 验证集 mAP(0.5:0.95)。GPU 推理耗时基于 NVIDIA Tesla T4 机器，精度类型为 FP32， CPU 推理速度基于 Intel(R) Xeon(R) Gold 5117 CPU @ 2.00GHz，线程数为8，精度类型为 FP32。**

简单来说，表格从上到下，模型推理速度更快，从下到上，模型精度更高。本教程以PP-YOLOE_plus-S模型为例，完成一次模型全流程开发。你可以依据自己的实际使用场景，判断并选择一个合适的模型做训练，训练完成后可在产线内评估合适的模型权重，并最终用于实际使用场景中。

## 4. 数据准备和校验
### 4.1 数据准备

本教程采用 `行人跌倒检测数据集` 作为示例数据集，可通过以下命令获取示例数据集。如果您使用自备的已标注数据集，需要按照 PaddleX 的格式要求对自备数据集进行调整，以满足 PaddleX 的数据格式要求。关于数据格式介绍，您可以参考 [PaddleX 数据格式介绍](../data/dataset_format.md)。如果您有一批待标注数据，可以参考 [通用目标检测数据标注指南](../data/annotation/DetAnnoTools.md) 完成数据标注。

数据集获取命令：
```bash
cd /path/to/paddlex
wget https://paddle-model-ecology.bj.bcebos.com/paddlex/data/fall_det.tar -P ./dataset
tar -xf ./dataset/fall_det.tar -C ./dataset/
```

### 4.2 数据集校验

在对数据集校验时，只需一行命令：

```bash
python main.py -c paddlex/configs/object_detection/PP-YOLOE_plus-S.yaml \
    -o Global.mode=check_dataset \
    -o Global.dataset_dir=./dataset/fall_det
```

执行上述命令后，PaddleX 会对数据集进行校验，并统计数据集的基本信息。命令运行成功后会在 log 中打印出 `Check dataset passed !` 信息，同时相关产出会保存在当前目录的 `./output/check_dataset` 目录下，产出目录中包括可视化的示例样本图片和样本分布直方图。校验结果文件保存在 `./output/check_dataset_result.json`，校验结果文件具体内容为
```
{
  "done_flag": true,
  "check_pass": true,
  "attributes": {
    "num_classes": 1,
    "train_samples": 1224,
    "train_sample_paths": [
      "check_dataset/demo_img/fall_1168.jpg",
      "check_dataset/demo_img/fall_1113.jpg"
    ],
    "val_samples": 216,
    "val_sample_paths": [
      "check_dataset/demo_img/fall_349.jpg",
      "check_dataset/demo_img/fall_394.jpg"
    ]
  },
  "analysis": {
    "histogram": "check_dataset/histogram.png"
  },
  "dataset_path": "./dataset/fall_det",
  "show_type": "image",
  "dataset_type": "COCODetDataset"
}  
```
上述校验结果中，check_pass 为 True 表示数据集格式符合要求，其他部分指标的说明如下：

- attributes.num_classes：该数据集类别数为 1，此处类别数量为后续训练需要传入的类别数量；
- attributes.train_samples：该数据集训练集样本数量为 1224；
- attributes.val_samples：该数据集验证集样本数量为 216；
- attributes.train_sample_paths：该数据集训练集样本可视化图片相对路径列表；
- attributes.val_sample_paths：该数据集验证集样本可视化图片相对路径列表；

另外，数据集校验还对数据集中所有类别的样本数量分布情况进行了分析，并绘制了分布直方图（histogram.png）：
<center>

<img src="https://github.com/user-attachments/assets/10fb6eab-f0aa-4e09-ba6e-65a28706f083" width=600>

</center>

**注**：只有通过数据校验的数据才可以训练和评估。


### 4.3 数据集格式转换/数据集划分（非必选）

如需对数据集格式进行转换或是重新划分数据集，可通过修改配置文件或是追加超参数的方式进行设置。

数据集校验相关的参数可以通过修改配置文件中 `CheckDataset` 下的字段进行设置，配置文件中部分参数的示例说明如下：

* `CheckDataset`:
    * `convert`:
        * `enable`: 是否进行数据集格式转换，为 `True` 时进行数据集格式转换，默认为 `False`;
        * `src_dataset_type`: 如果进行数据集格式转换，则需设置源数据集格式，数据可选源格式为 `LabelMe` 和 `VOC`；
    * `split`:
        * `enable`: 是否进行重新划分数据集，为 `True` 时进行数据集格式转换，默认为 `False`；
        * `train_percent`: 如果重新划分数据集，则需要设置训练集的百分比，类型为 0-100 之间的任意整数，需要保证和 `val_percent` 值加和为 100；
        * `val_percent`: 如果重新划分数据集，则需要设置验证集的百分比，类型为 0-100 之间的任意整数，需要保证和 `train_percent` 值加和为 100；

数据转换和数据划分支持同时开启，对于数据划分原有标注文件会被在原路径下重命名为 `xxx.bak`，以上参数同样支持通过追加命令行参数的方式进行设置，例如重新划分数据集并设置训练集与验证集比例：`-o CheckDataset.split.enable=True -o CheckDataset.split.train_percent=80 -o CheckDataset.split.val_percent=20`。

## 5. 模型训练和评估
### 5.1 模型训练

在训练之前，请确保您已经对数据集进行了校验。完成 PaddleX 模型的训练，只需如下一条命令：

```bash
python main.py -c paddlex/configs/object_detection/PP-YOLOE_plus-S.yaml \
    -o Global.mode=train \
    -o Global.dataset_dir=./dataset/fall_det \
    -o Train.num_classes=1
```

在 PaddleX 中模型训练支持：修改训练超参数、单机单卡/多卡训练等功能，只需修改配置文件或追加命令行参数。

PaddleX 中每个模型都提供了模型开发的配置文件，用于设置相关参数。模型训练相关的参数可以通过修改配置文件中 `Train` 下的字段进行设置，配置文件中部分参数的示例说明如下：

* `Global`：
    * `mode`：模式，支持数据校验（`check_dataset`）、模型训练（`train`）、模型评估（`evaluate`）；
    * `device`：训练设备，可选`cpu`、`gpu`、`xpu`、`npu`、`mlu`，除 cpu 外，多卡训练可指定卡号，如：`gpu:0,1,2,3`；
* `Train`：训练超参数设置；
    * `epochs_iters`：训练轮次数设置；
    * `learning_rate`：训练学习率设置；

更多超参数介绍，请参考 [PaddleX 超参数介绍](../base/hyperparameters_introduction.md)。

**注：**
- 以上参数可以通过追加令行参数的形式进行设置，如指定模式为模型训练：`-o Global.mode=train`；指定前 2 卡 gpu 训练：`-o Global.device=gpu:0,1`；设置训练轮次数为 10：`-o Train.epochs_iters=10`。
- 模型训练过程中，PaddleX 会自动保存模型权重文件，默认为`output`，如需指定保存路径，可通过配置文件中 `-o Global.output` 字段
- PaddleX 对您屏蔽了动态图权重和静态图权重的概念。在模型训练的过程中，会同时产出动态图和静态图的权重，在模型推理时，默认选择静态图权重推理。

**训练产出解释:**  

在完成模型训练后，所有产出保存在指定的输出目录（默认为`./output/`）下，通常有以下产出：

* train_result.json：训练结果记录文件，记录了训练任务是否正常完成，以及产出的权重指标、相关文件路径等；
* train.log：训练日志文件，记录了训练过程中的模型指标变化、loss 变化等；
* config.yaml：训练配置文件，记录了本次训练的超参数的配置；
* .pdparams、.pdema、.pdopt.pdstate、.pdiparams、.pdmodel：模型权重相关文件，包括网络参数、优化器、EMA、静态图网络参数、静态图网络结构等；

### 5.2 模型评估

在完成模型训练后，可以对指定的模型权重文件在验证集上进行评估，验证模型精度。使用 PaddleX 进行模型评估，只需一行命令：

```bash
python main.py -c paddlex/configs/object_detection/PP-YOLOE_plus-S.yaml \
    -o Global.mode=evaluate \
    -o Global.dataset_dir=./dataset/fall_det
```

与模型训练类似，模型评估支持修改配置文件或追加命令行参数的方式设置。

**注：** 在模型评估时，需要指定模型权重文件路径，每个配置文件中都内置了默认的权重保存路径，如需要改变，只需要通过追加命令行参数的形式进行设置即可，如`-o Evaluate.weight_path=./output/best_model.pdparams`。

### 5.3 模型调优

在学习了模型训练和评估后，我们可以通过调整超参数来提升模型的精度。通过合理调整训练轮数，您可以控制模型的训练深度，避免过拟合或欠拟合；而学习率的设置则关乎模型收敛的速度和稳定性。因此，在优化模型性能时，务必审慎考虑这两个参数的取值，并根据实际情况进行灵活调整，以获得最佳的训练效果。

推荐在调试参数时遵循控制变量法：

1. 首先固定训练轮次为 10，批大小为 8。
2. 基于 PP-YOLOE_plus-S 模型启动三个实验，学习率分别为：0.00002，0.0001，0.0005。
3. 可以发现实验二精度最高的配置为学习率为 0.0001，在该训练超参数基础上，改变训练论次数，观察不同轮次的精度结果，发现轮次在 50epoch 时基本达到了最佳精度。

学习率探寻实验结果：
<center>

| 实验  | 轮次 | 学习率   | batch\_size | 训练环境 | mAP@0\.5 |
|-----|----|-------|-------------|------|----------|
| 实验一 | 10 | 0\.00002 | 8          | 4卡   | 0\.880   |
| 实验二 | 10 | 0\.0001 | 8          | 4卡   |**0\.910**|
| 实验三 | 10 | 0\.0005 | 8          | 4卡   | 0\.888   |

</center>

改变 epoch 实验结果：
<center>

| 实验        | 轮次  | 学习率   | batch\_size | 训练环境 | mAP@0\.5 |
|-----------|-----|-------|-------------|------|----------|
| 实验二       | 10  | 0\.0001 | 8          | 4卡   | 0\.910   |
| 实验二增大训练轮次 | 50  | 0\.0001 | 8          | 4卡   | **0\.944**   |
| 实验二增大训练轮次 | 100  | 0\.0001 | 8          | 4卡   | 0\.947   |
</center>

** 注：本教程为4卡教程，如果您只有1张GPU，可通过调整训练卡数完成本次实验，但最终指标未必和上述指标对齐，属正常情况。**

## 6. 产线测试

将产线中的模型替换为微调后的模型进行测试，如：

```bash
python main.py -c paddlex/configs/object_detection/PP-YOLOE_plus-S.yaml \
    -o Global.mode=predict \
    -o Predict.model_dir="output/best_model" \
    -o Predict.input_path="https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/fall.png"
```

通过上述可在`./output`下生成预测结果，其中`fall.png`的预测结果如下：
<center>

<img src="https://github.com/user-attachments/assets/3fc1c127-0893-4362-8721-4701d914a42f" width="600"/>

</center>

## 7. 开发集成/部署
1. 此处提供了轻量级的 PaddleX Python API 的集成方式，使用 Python API 方式可以更加方便的将 PaddleX 产出模型集成到自己的项目中进行二次开发，详细集成方式可参考 [PaddleX 模型产线推理预测](../pipelines/pipeline_inference.md)。
此处提供轻量级的 PaddleX Python API 的集成方式，也提供高性能推理/服务化部署的方式部署模型。 PaddleX Python API 的集成方式如下：

```python
from paddlex import DetPipeline
from paddlex import PaddleInferenceOption

model_name = "PP-YOLOE_plus-S"
model_dir= "./output/best_model"
pipeline = DetPipeline(model_name, model_dir=model_dir, kernel_option=PaddleInferenceOption())
result = pipeline.predict(
        {'input_path': "./dataset/fall_det/images/fall_66.jpg"}
    )

print(result["boxes"])
```  
2. PaddleX也提供了基于 FastDeploy 的高性能推理/服务化部署的方式进行模型部署。该部署方案支持更多的推理后端，并且提供高性能推理和服务化部署两种部署方式，能够满足更多场景的需求，具体流程可参考 [基于 FastDeploy 的模型产线部署]((../pipelines/pipeline_deployment_with_fastdeploy.md))。高性能推理和服务化部署两种部署方式的特点如下：
    * 高性能推理：运行脚本执行推理，或在程序中调用 Python/C++ 的推理 API。旨在实现测试样本的高效输入与模型预测结果的快速获取，特别适用于大规模批量刷库的场景，显著提升数据处理效率。
    * 服务化部署：采用 C/S 架构，以服务形式提供推理能力，客户端可以通过网络请求访问服务，以获取推理结果。
* PaddleX 高性能离线部署和服务化部署流程如下：

    1. 获取离线部署包。
        1. 在 [AIStudio 星河社区](https://aistudio.baidu.com/pipeline/mine) 根据本地训练模型产线创建对应产线，在“选择产线”页面点击“直接部署”。
        2. 在“产线部署”页面选择“导出离线部署包”，使用默认的模型方案，选择与本地测试环境对应的部署包运行环境，点击“导出部署包”。
        3. 待部署包导出完毕后，点击“下载离线部署包”，将部署包下载到本地。
        4. 点击“生成部署包序列号”，根据页面提示完成设备指纹的获取以及设备指纹与序列号的绑定，确保序列号对应的激活状态为“已激活“。
    2. 使用自训练模型替换离线部署包 `model` 目录中的模型。
    3. 根据需要选择要使用的部署SDK：`offline_sdk` 目录对应高性能推理SDK，`serving_sdk` 目录对应服务化部署SDK。按照SDK文档（README.md）中的说明，完成部署环境准备，建议使用文档提供的官方docker进行环境部署。
    4. 对于高性能推理方式部署，修改 `offline_sdk/python_example/fd_model_config.yaml` 中的 "model_path_root" 字段值为自训练模型存放目录，并使用如下命令完成模型高性能推理：

```bash
python infer.py --resource_path . --device gpu --serial_num <serial_number> --update_license True --backend paddle_option  --input_data_path https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/fall.png --is_visualize True
```

其他产线的 Python API 集成方式可以参考[PaddleX 模型产线推理预测](../pipelines/pipeline_inference.md)。
PaddleX 同样提供了高性能的离线部署和服务化部署方式，具体参考[基于 FastDeploy 的模型产线部署](../pipelines/pipeline_deployment_with_fastdeploy.md)。
