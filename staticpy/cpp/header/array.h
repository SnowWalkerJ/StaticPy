#pragma once
#include <vector>
#include <stdarg.h>
#include <stdexcept>
#ifdef PYBIND
#include <pybind11/pybind11.h>
namespace py = pybind11;
#endif

template <typename T, long ndim>
class Array {
public:
    const T *data;
    const long *shape;
    const long *strides;
    const long dim = ndim;
    const long itemsize;
    #ifdef PYBIND
    Array(py::buffer_info& bi) : 
        data((T*)bi.ptr), shape(bi.shape.data()), strides(bi.strides.data()), itemsize(bi.itemsize) {
    }
    #endif
    Array(T* data, std::vector<long>& shape, std::vector<long>& strides, long itemsize) : 
        data(data), shape(shape.data()), strides(strides.data()), itemsize(itemsize) {
    }

};
