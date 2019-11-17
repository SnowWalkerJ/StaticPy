// #include "stdafx.h"
#include <stdarg.h>

template <typename T, unsigned int ndim>
class Array {
public:
    T *data;
    unsigned int shape[ndim];
    const unsigned int dim = ndim;
    Array(T *data, ...) {
        this -> data = data;
        va_list args;
        va_start(args, data);
        for (int i = 0; i < ndim; i++) {
            shape[i] = va_arg(args, unsigned int);
        }
        va_end(args);
    }
    inline T& operator[](int index) {
        return data[index];
    }

    inline T& getData(unsigned int index0, ...) {
        // transform numpy-like index to C-like index
        va_list args;
        va_start(args, index0);
        unsigned int indices[ndim];
        indices[0] = index0;
        for (unsigned int i = 1; i < ndim; i++) {
            indices[i] = va_arg(args, unsigned int);
        }
        va_end(args);
        unsigned int stride = 1, index = 0;
        for (unsigned int i = ndim-1; i >= 0; i--) {
            index += stride * indices[i];
            stride *= shape[i];
        }
        return this->operator[](index);
    }

};