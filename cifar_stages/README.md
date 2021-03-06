## How to run

### Local run

```bash
PYTHONPATH=. python prometheus/dl/scripts/train.py \
   --config=./cifar_stages/config.yml
```

For tensorboard support use 

`tensorboard --logdir=./logs/cifar_stages`


### Docker run

For docker image goto `prometheus/docker`

```bash
export LOGDIR=$(pwd)/logs/cifar_stages_docker
docker run -it --rm \
   -v $(pwd):/src -v $LOGDIR:/logdir/ \
   -e PYTHONPATH=. \
   pro-cpu python prometheus/dl/scripts/train.py \
   --config=./cifar_stages/config.yml --logdir=/logdir
```


For tensorboard support use 

`tensorboard --logdir=./logs/cifar_docker`