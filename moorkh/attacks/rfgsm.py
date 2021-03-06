import torch
import torch.nn as nn

from .base import Attack


class RFGSM(Attack):
    
    def __init__(self, model, eps=16/255, alpha=8/255, itrs=1):
        super(RFGSM, self).__init__(model,"RFGSM")
        self.eps = eps
        self.alpha = alpha
        self.steps = itrs

    def forward(self, images, labels):
        
        images = images.clone().detach().to(self.device)
        labels = labels.clone().detach().to(self.device)
        labels = self._transform_label(images, labels)
        loss = nn.CrossEntropyLoss()

        adv_images = images + self.alpha*torch.randn_like(images).sign()
        adv_images = torch.clamp(adv_images, min=0, max=1).detach()

        for i in range(self.itrs):
            adv_images.requires_grad = True
            outputs = self.model(adv_images)
            cost = self._targeted*loss(outputs, labels)

            grad = torch.autograd.grad(cost, adv_images,
                                       retain_graph=False, create_graph=False)[0]

            adv_images = adv_images - (self.eps-self.alpha)*grad.sign()
            adv_images = torch.clamp(adv_images, min=0, max=1).detach()

        return adv_images