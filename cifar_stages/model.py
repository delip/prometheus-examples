import collections
import torch
import torch.nn as nn
import torch.nn.functional as F
from prometheus.utils.factory import UtilsFactory
from prometheus.dl.callbacks import (
    Callback,
    ClassificationLossCallback, LoggerCallback, OptimizerCallback,
    CheckpointCallback, OneCycleLR, PrecisionCallback)
from prometheus.dl.runner import ClassificationRunner


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


def build_simple_model():
    net = Net()
    return net


NETWORKS = {
    "simple": build_simple_model
}


def prepare_model(config):
    return UtilsFactory.create_model(
        config=config, available_networks=NETWORKS)


class StageCallback(Callback):
    def on_stage_init(self, model, stage):
        model_ = model
        if isinstance(model, torch.nn.DataParallel):
            model_ = model_.module

        if stage == "stage2":
            for key in ["conv1", "pool", "conv2"]:
                layer = getattr(model_, key)
                for param in layer.parameters():
                    param.requires_grad = False


class ModelRunner(ClassificationRunner):

    @staticmethod
    def prepare_callbacks(*, callbacks_params, args, mode, stage=None):
        callbacks = collections.OrderedDict()

        callbacks["stage"] = StageCallback()
        callbacks["loss"] = ClassificationLossCallback()
        callbacks["optimizer"] = OptimizerCallback()
        callbacks["one-cycle"] = OneCycleLR(
            cycle_len=args.epochs,
            div=3, cut_div=4, momentum_range=(0.95, 0.85))
        callbacks["precision"] = PrecisionCallback(
            precision_args=callbacks_params.get("precision_args", [1, 3, 5]))
        callbacks["logger"] = LoggerCallback(
            reset_step=callbacks_params.get("reset_step", False))
        callbacks["saver"] = CheckpointCallback(
            save_n_best=getattr(args, "save_n_best", 5),
            resume=args.resume,
            main_metric=callbacks_params.get("main_metric", "loss"),
            minimize=callbacks_params.get("minimize_metric", True))

        return callbacks
