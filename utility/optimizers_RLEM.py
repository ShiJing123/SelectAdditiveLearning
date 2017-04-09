#!/usr/bin/env python

import theano
import theano.tensor as T
import numpy as np

from collections import OrderedDict

class Optimizer:

    """
    Optimization methods for backpropagation
    """

    def __init__(self):

        """
        __TODO__ add gradient clipping
        """

    def sgd(self, cost, params, lr):
        """
        Stochatic Gradient Descent.
        """
        gradients = T.grad(cost, params.values())

        # updates = OrderedDict()
        updates = []
        for paramID, param, gradient in zip(params.keys(), params.values(), gradients):
            # updates[param] = (param, param - lr * gradient)
            updates.append((param, param - lr * gradient))

        return updates

    def adagrad(self, cost, params, lr, epsilon=1e-6):
        """
        Adaptive Gradient Optimization.
        """
        epsilon = theano.shared(np.float32(epsilon).astype(theano.config.floatX))

        gradients = T.grad(cost, params.values())

        updates = []
        for paramID, param, gradient in zip(params.keys(), params.values(), gradients):
            accumulated_gradient = theano.shared(np.zeros_like(param.get_value(borrow=True)).astype(np.float32), borrow=True)
            accumulated_gradient_new = accumulated_gradient + gradient  ** 2
            updates.append((accumulated_gradient, accumulated_gradient_new))
            updates.append((param, param - lr * gradient / T.sqrt(accumulated_gradient_new + epsilon)))
            # updates[param] = (param, param - lr * gradient / T.sqrt(accumulated_gradient_new + epsilon))
        return updates

    def rmsprop(self, cost, params, lr, rho=0.9, epsilon=1e-6):
        """
        RMSProp - Root Mean Square
        Reference - http://www.cs.toronto.edu/~tijmen/csc321/slides/lecture_slides_lec6.pdf
        """

        epsilon = theano.shared(np.float32(epsilon).astype(theano.config.floatX))
        rho = theano.shared(np.float32(rho).astype(theano.config.floatX))

        gradients = T.grad(cost, params.values())

        updates = []
        for paramID, param, gradient in zip(params.keys(), params.values(), gradients):
            accumulated_gradient = theano.shared(np.zeros_like(param.get_value(borrow=True)).astype(np.float32), borrow=True)
            accumulated_gradient_new = accumulated_gradient * rho + gradient ** 2 * (1 - rho)
            updates.append((accumulated_gradient, accumulated_gradient_new))
            updates.append((param, param - lr * gradient / T.sqrt(accumulated_gradient_new + epsilon)))
            # updates[param] = (param, param - lr * gradient / T.sqrt(accumulated_gradient_new + epsilon))
        return updates

    def adam(self, cost, params, lr, beta_1=0.9, beta_2=0.999, epsilon=1e-8):
        """
        ADAM
        Reference - http://arxiv.org/pdf/1412.6980v8.pdf - Page 2
        """

        epsilon = theano.shared(np.float32(epsilon).astype(theano.config.floatX))
        beta_1 = theano.shared(np.float32(beta_1).astype(theano.config.floatX))
        beta_2 = theano.shared(np.float32(beta_2).astype(theano.config.floatX))
        t = theano.shared(np.float32(1.0).astype(theano.config.floatX))

        gradients = T.grad(cost, params.values())

        updates = []
        for paramID, param, gradient in zip(params.keys(), params.values(), gradients):
            param_value = param.get_value(borrow=True)
            m_tm_1 = theano.shared(np.zeros_like(param_value).astype(np.float32), borrow=True)
            v_tm_1 = theano.shared(np.zeros_like(param_value).astype(np.float32), borrow=True)

            m_t = beta_1 * m_tm_1 + (1 - beta_1) * gradient
            v_t = beta_2 * v_tm_1 + (1 - beta_2) * gradient ** 2

            m_hat = m_t / (1 - beta_1)
            v_hat = v_t / (1 - beta_2)

            updated_param = param - (lr * m_hat) / (T.sqrt(v_hat) + epsilon)
            updates.append((m_tm_1, m_t))
            updates.append((v_tm_1, v_t))
            updates.append((param, updated_param))
            # if 'm' in paramID or 'v' in paramID:
            #     updates[param] = m_t
            # updates[param] = (param, updated_param)

        # updates.append((t, t + 1.0))
        return updates
