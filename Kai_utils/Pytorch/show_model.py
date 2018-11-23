import torch
def show_model(model):
    print('======= Model Parameters =======')
    print(model)
    params=list(model.parameters())
    p=0
    idx=0
    for e in params:
        l=1
        
        if len(e.size())>1:
            for j in e.size():
                l *= j
            print('Layer '+str(idx)+': '+str(list(e.size()))+'  parameters num: '+str(l))
            idx+=1
            p += l
    print('All parameters num: '+str(p))


if __name__ == "__main__":
    ###########
    # example #
    ###########

    # inital model
    Net = model.MSnet_vocal() 
    Net.cuda()
    Net.float()
    Net.eval()

    # load model
    Net.load_state_dict(torch.load(model_path))
    # show model
    show_model(Net)

