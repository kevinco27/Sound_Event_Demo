import caffe2
from caffe2.python import brew

def GLU(model, name, pre_blob, inp, out, ms=(2,4), ds=1):
    ## layer name
    conv_name = "module.{}.cnn_lin".format(name)
    bn_name = "module.{}.bn".format(name)
    relu_name = "module.{}.relu".format(name)
    mp_name = "module.{}.mp".format(name)
    ##

    brew.conv(model, pre_blob, conv_name, inp, out, kernel=3, pad=1)
    brew.spatial_bn(model, conv_name, bn_name, out)
    brew.relu(model, bn_name, relu_name)
    return brew.max_pool(model, relu_name, mp_name, kernel=ms)

def DNN(model, name, pre_blob, inp, out):
    ## layer name
    dnn_name = "module.{}.dnn".format(name)
    bn_name = "module.{}.bn".format(name)
    
    ##

# def creatNet():
